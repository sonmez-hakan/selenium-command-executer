from os import environ
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver


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


class Factory:
    @staticmethod
    def create() -> Safari | Chrome:
        browser = environ.get('BROWSER', 'chrome').lower()
        if browser == 'safari':
            return Safari()
        else:
            return Chrome()
