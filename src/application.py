from selenium.webdriver.chrome.webdriver import WebDriver
from src.driver.browser import Factory
from src.driver.commands import CommandFactory
from src.utils.sites import Sites


class Application:
    def __init__(self):
        self.driver: WebDriver = Factory.create().get()

    def run(self):
        for site in Sites.read():
            self.process(site)
        self.driver.quit()

    def process(self, site: dict):
        for command in site.get('commands'):
            CommandFactory.create(self.driver, command.get('type')).run(**command.get('args'))
