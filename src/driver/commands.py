import csv
import os
import time
from abc import ABC, abstractmethod
from .methods import wait_for_element
from .html_elements import HtmlElement, HtmlElementFactory, ByMapper
from .driver import Driver
from src.utils.url import Url

PATH = os.environ.get('REPORTS_PATH', 'reports')


class Command(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class OpenCommand(Command):
    def run(self, *args, **kwargs):
        Driver.get().get(Url(kwargs.get('url'), kwargs.get('type', 'web')).get())


class RefreshUntilElementAppearsCommand(Command):
    def run(self, *args, **kwargs):
        driver = Driver.get()
        url = Url(kwargs.get('url', driver.current_url), kwargs.get('type', 'web')).get()
        by = kwargs.get('by')
        name = kwargs.get('name')
        refresh_time = kwargs.get('refresh_time')
        element = HtmlElement(by, name)

        while element.exists():
            driver.get(url)
            time.sleep(refresh_time)


class WaitCommand(Command):
    def run(self, *args, **kwargs):
        wait_for_element(ByMapper.transform(kwargs.get('by')), kwargs.get('name'))


class ClickCommand(Command):
    def run(self, *args, **kwargs):
        HtmlElementFactory.element(kwargs.get('find')).click()


class FormCommand(Command):
    def run(self, *args, **kwargs):
        inputs: dict = kwargs.get('inputs', [])
        submit: dict = kwargs.get('submit', None)
        for html_input in inputs:
            element = HtmlElementFactory.input(html_input)
            element.wait(html_input.get('waits', []))
            element.set()

        if submit is not None:
            HtmlElementFactory.element(submit).click()


class DataCommand(Command):
    def run(self, *args, **kwargs):
        find = kwargs.get('find')
        pagination = kwargs.get('pagination')
        logs = kwargs.get('logs')

        page = 1
        records = []
        try:
            while True:
                elements = HtmlElementFactory.find(find.get('by'), find.get('name'))
                if len(elements) == 0:
                    break

                for element in elements:
                    record = {}
                    for log in logs:
                        child = element.child(log.get('by'), log.get('name'))
                        if "data" in log:
                            for data in log.get('data'):
                                self._get_data(child, data, record)
                        else:
                            self._get_data(child, log, record)
                    records.append(record)

                page += 1
                self._page_forward(pagination, page)
        except (SameUrlException, PageNotFound, PageLimitExceeded):
            pass

        self._write_report(records, kwargs.get('file'))

    @staticmethod
    def _get_data(child: HtmlElement, log: dict, record: dict):
        record_name = log.get('log')
        value = child.get_attribute(log.get('attribute', 'text'))
        if "getter" in log:
            func = eval(log.get('getter'))
            try:
                record[record_name] = func(value)
            except Exception:
                record[record_name] = ''
        else:
            record[record_name] = value

    @staticmethod
    def _get_url(url: str, page: int, func_def: str):
        func = eval(func_def)

        return func(url, page)

    @staticmethod
    def _page_forward(pagination: dict, page: int):
        until: int = pagination.get('until')
        if 0 < until < page:
            raise PageLimitExceeded(f'The allowed number of pages has been exceeded. {page}')

        driver = Driver.get()
        url = driver.current_url
        if "link" in pagination:
            driver.get(DataCommand._get_url(url, page, pagination.get('link')))
        else:
            links = pagination.get('links')
            parent = links.get("parent")
            find = links.get("find")
            try:
                element = HtmlElement(parent.get('by'), parent.get('name')).child(
                    find.get('by'), find.get('text').replace('{{page}}', str(page))
                )
            except Exception:
                raise PageNotFound(f'{page} not found')

            if "click" in find:
                func = eval(find.get('click'))
                func(element)
            else:
                element.click()

        if url == driver.current_url:
            raise SameUrlException("After changing url returned the same")

    @staticmethod
    def _write_report(records: list, file: dict):
        file_name = f"{PATH}/{file.get('name')}.csv"
        headers = records[0].keys()

        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)


class ScrollCommand(Command):
    def run(self, *args, **kwargs):
        pass


class CommandFactory:
    @staticmethod
    def create(command_type: str):
        command_type = command_type.lower()
        if command_type == 'open':
            return OpenCommand()

        if command_type == 'refresh_until_element_appears':
            return RefreshUntilElementAppearsCommand()

        if command_type == 'wait':
            return WaitCommand()

        if command_type == 'form':
            return FormCommand()

        if command_type == 'data':
            return DataCommand()


class SameUrlException(Exception):
    pass


class PageNotFound(Exception):
    pass


class PageLimitExceeded(Exception):
    pass
