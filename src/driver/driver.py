from os import environ
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from src.utils.utils import staticclass


class Browser(ABC):
    @abstractmethod
    def get(self):
        pass


class Chrome(Browser):
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options, service=service)

    def get(self) -> WebDriver:
        return self.driver


class Safari(Browser):
    def __init__(self):
        options = webdriver.SafariOptions()
        self.driver = webdriver.Chrome(options=options)

    def get(self) -> WebDriver:
        return self.driver


@staticclass
class Factory:
    @staticmethod
    def create(browser: str | None = None) -> WebDriver:
        browser = browser if browser is not None else environ.get('BROWSER', 'chrome').lower()
        if browser == 'safari':
            return Safari().get()
        else:
            return Chrome().get()


@staticclass
class Driver:
    drivers: dict[str, WebDriver] = {}
    key: str = 'default'
    DEFAULT: str = 'default'

    @staticmethod
    def set_key(key: str = 'default') -> None:
        Driver.key = key if key is not None else Driver.DEFAULT

    @staticmethod
    def get_driver_key() -> str:
        return Driver.key

    @staticmethod
    def get_keys() -> list[str]:
        return list(Driver.drivers.keys())

    @staticmethod
    def _choose_key(key: str | None) -> str:
        if key is not None:
            return key

        return Driver.key

    @staticmethod
    def get(key: str | None = None) -> WebDriver:
        key = Driver._choose_key(key)
        if key in Driver.drivers:
            return Driver.drivers[key]

        raise DriverKeyNotFoundException(f'{key} is not in the dictionary')

    @staticmethod
    def create(key: str | None = None, browser: str | None = None, force_new: bool = False) -> WebDriver:
        key = Driver._choose_key(key)
        driver = Factory.create(browser)
        if force_new and key in Driver.drivers:
            DriverKeyAlreadyExistsException(f'{key} is already in dictionary')
        Driver.drivers[key] = driver

        return driver

    @staticmethod
    def quit(key: str | None = None) -> None:
        key = Driver._choose_key(key)
        Driver.drivers.get(key).quit()
        del Driver.drivers[key]

    @staticmethod
    def quit_all() -> None:
        for key in Driver.get_keys():
            Driver.quit(key)


class DriverKeyNotFoundException(Exception):
    pass


class DriverKeyAlreadyExistsException(Exception):
    pass
