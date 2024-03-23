import csv
import os
from abc import ABC, abstractmethod
from selenium.webdriver.chrome.webdriver import WebDriver
from .methods import wait_for_element
from .html_elements import HtmlElement, HtmlElementFactory, ByMapper

PATH = os.environ.get('REPORTS_PATH', 'reports')


class Command(ABC):
    def __init__(self, driver: WebDriver):
        self.driver: WebDriver = driver

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class OpenCommand(Command):
    def run(self, *args, **kwargs):
        self.driver.get(kwargs.get('url'))


class WaitCommand(Command):
    def run(self, *args, **kwargs):
        wait_for_element(self.driver, ByMapper.transform(kwargs.get('by')), kwargs.get('name'))


class ClickCommand(Command):
    def run(self, *args, **kwargs):
        HtmlElementFactory.element(self.driver, kwargs.get('find')).click()


class FormCommand(Command):
    def run(self, *args, **kwargs):
        inputs: dict = kwargs.get('inputs')
        submit: dict = kwargs.get('submit')
        for html_input in inputs:
            element = HtmlElementFactory.input(self.driver, html_input)
            element.wait(html_input.get('waits', []))
            element.set()

        HtmlElementFactory.element(self.driver, submit).click()


class DataCommand(Command):
    def run(self, *args, **kwargs):
        find = kwargs.get('find')
        pagination = kwargs.get('pagination')
        logs = kwargs.get('logs')

        page = 1
        records = []
        try:
            while True:
                elements = HtmlElementFactory.find(self.driver, find.get('by'), find.get('name'))
                if len(elements) == 0:
                    break

                for element in elements:
                    record = {}
                    for log in logs:
                        child = element.child(log.get('by'), log.get('name'))
                        if "data" in log:
                            for data in log.get('data'):
                                DataCommand._get_data(child, data, record)
                        else:
                            DataCommand._get_data(child, log, record)
                    records.append(record)

                page += 1
                self._page_forward(pagination, page)
        except (SameUrlException, PageNotFound, PageLimitExceeded) as e:
            pass

        DataCommand._write_report(records, kwargs.get('file'))

    @staticmethod
    def _get_data(child: HtmlElement, log: dict, record: dict):
        record_name = log.get('log')
        value = child.get_attribute(log.get('attribute', 'text'))
        if "getter" in log:
            func = eval(log.get('getter'))
            try:
                record[record_name] = func(value)
            except:
                record[record_name] = ''
        else:
            record[record_name] = value

    @staticmethod
    def _get_url(url: str, page: int, func_def: str):
        func = eval(func_def)

        return func(url, page)

    def _page_forward(self, pagination: dict, page: int):
        until: int = pagination.get('until')
        if 0 < until < page:
            raise PageLimitExceeded(f'The allowed number of pages has been exceeded. {page}')

        url = self.driver.current_url
        if "link" in pagination:
            self.driver.get(DataCommand._get_url(url, page, pagination.get('link')))
        else:
            links = pagination.get('links')
            parent = links.get("parent")
            find = links.get("find")
            try:
                element = HtmlElement(self.driver, parent.get('by'), parent.get('name')).child(
                    find.get('by'), find.get('text').replace('{{page}}', str(page))
                )
            except:
                raise PageNotFound(f'{page} not found')

            if "click" in find:
                func = eval(find.get('click'))
                func(element)
            else:
                element.click()

        if url == self.driver.current_url:
            raise SameUrlException("After changing url returned the same")

    @staticmethod
    def _write_report(records: list, file: dict):
        file_name = f"{PATH}/{file.get('name')}.csv"
        headers = records[0].keys()

        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)


class CommandFactory:
    @staticmethod
    def create(driver: WebDriver, command_type: str):
        command_type = command_type.lower()
        if command_type == 'open':
            return OpenCommand(driver)

        if command_type == 'wait':
            return WaitCommand(driver)

        if command_type == 'form':
            return FormCommand(driver)

        if command_type == 'data':
            return DataCommand(driver)


class SameUrlException(Exception):
    pass


class PageNotFound(Exception):
    pass


class PageLimitExceeded(Exception):
    pass
