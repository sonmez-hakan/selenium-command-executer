from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from src.driver.browser import Browser


class Safari(Browser):
    def __init__(self):
        options = webdriver.SafariOptions()
        self.driver = webdriver.Chrome(options=options)

    def get(self) -> WebDriver:
        return self.driver
