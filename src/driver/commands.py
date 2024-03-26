import time
from abc import ABC, abstractmethod
from . import (
    CSV, Url, Driver, HtmlElement, HtmlElementFactory, ByMapper, wait_for_element, LinkPagination, SameUrlException,
    PageNotFound, PageLimitExceeded
)
from src.utils import staticclass


class Command(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class OpenCommand(Command):
    def run(self, *args, **kwargs):
        Driver().get().get(Url(kwargs.get('url'), kwargs.get('type', 'web')).get())


class RefreshUntilElementAppearsCommand(Command):
    def run(self, *args, **kwargs):
        driver = Driver().get()
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
                if not self._wait(find):
                    break

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
                LinkPagination().page_forward(pagination, page)
        except (SameUrlException, PageNotFound, PageLimitExceeded):
            pass

        CSV().write(records, kwargs.get('file'))

    @staticmethod
    def _wait(find: dict) -> bool:
        try:
            WaitCommand().run(**find)
        except:
            return False

        return True

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


class ScrollCommand(Command):
    def run(self, *args, **kwargs):
        pass


class SetSizeCommand(Command):
    def run(self, *args, **kwargs):
        pass


@staticclass
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
