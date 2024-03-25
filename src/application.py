from src.driver.commands import CommandFactory
from src.driver.driver import Driver
from src.utils.sites import Sites


class Application:
    def run(self):
        for site in Sites.read():
            Driver.set_key(site.get('driver_key'))
            Driver.create(browser=site.get('browser', 'chrome'))
            self.process(site.get('commands'))
            if site.get('quit', False):
                Driver.quit()
        Driver.quit_all()

    def process(self, commands: []):
        for command in commands:
            CommandFactory.create(command.get('type')).run(**command.get('args'))
