from src.driver import CommandFactory, Driver, Reader
from src.utils import staticclass, get


@staticclass
class Application:
    @staticmethod
    def run():
        for site in Reader.read():
            Driver().create(**site.get('driver', {}))
            for command in site.get('commands', []):
                CommandFactory.create(command.get('type')).run(**command.get('args'))

            if get(site, 'driver.quit', False):
                Driver().quit()

        Driver().quit_all()
