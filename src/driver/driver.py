from os import environ
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from src.utils import staticclass, singleton, get


class Browser(ABC):
    @abstractmethod
    def get(self):
        pass


class Chrome(Browser):
    def __init__(self, options_list: dict | None = None):
        if options_list is None:
            options_list = {}

        options = webdriver.ChromeOptions()
        for method_name, values in options_list.items():
            method = getattr(options, method_name)
            for key, value in values.items():
                method(key, value)

        self.driver = webdriver.Chrome(options=options, service= Service(ChromeDriverManager().install()))

    def get(self) -> WebDriver:
        return self.driver


class Safari(Browser):
    def __init__(self, options_list: dict | None = None):
        if options_list is None:
            options_list = {}

        options = webdriver.SafariOptions()
        for method_name, values in options_list.items():
            method = getattr(options, method_name)
            for key, value in values.items():
                method(key, value)

        self.driver = webdriver.Safari(options=options)

    def get(self) -> WebDriver:
        return self.driver


@staticclass
class Factory:
    @staticmethod
    def create(browser: dict | None = None) -> WebDriver:
        if browser is None:
            browser = {}

        browser_name = str(get(browser, 'name', environ.get('BROWSER', 'chrome'))).lower()
        options = get(browser, 'options')
        if browser_name == 'safari':
            return Safari(options).get()
        else:
            return Chrome(options).get()


@singleton
class Driver:
    DEFAULT: str = 'default'

    def __init__(self):
        self.drivers: dict[str, WebDriver] = {}
        self.key: str = self.DEFAULT

    def set_key(self, key: str = 'default') -> None:
        self.key = key if key is not None else self.DEFAULT

    def get_driver_key(self) -> str:
        return self.key

    def get_keys(self) -> list[str]:
        return list(self.drivers.keys())

    def _choose_key(self, key: str | None) -> str:
        if key is not None:
            return key

        return self.key

    def get(self, key: str | None = None) -> WebDriver:
        key = self._choose_key(key)
        if key in self.drivers:
            return self.drivers[key]

        raise DriverKeyNotFoundException(f'{key} is not in the dictionary')

    def create(self, **kwargs) -> WebDriver:
        key = self._choose_key(kwargs.get('key'))
        if kwargs.get('force_new', False) and key in self.drivers:
            DriverKeyAlreadyExistsException(f'{key} is already in dictionary')

        web_driver = Factory.create(kwargs.get('browser'))
        web_driver.set_window_size(
            int(str(get(kwargs, 'size.width', environ.get('BROWSER_WIDTH', 1280)))),
            int(str(get(kwargs, 'size.height', environ.get('BROWSER_HEIGHT', 720)))),
        )

        self.drivers[key] = web_driver
        if kwargs.get('set_key', True):
            self.key = key

        return web_driver

    def quit(self, key: str | None = None) -> None:
        key = self._choose_key(key)
        self.drivers.get(key).quit()
        del self.drivers[key]

    def quit_all(self) -> None:
        for key in self.get_keys():
            self.quit(key)


class DriverKeyNotFoundException(Exception):
    pass


class DriverKeyAlreadyExistsException(Exception):
    pass
