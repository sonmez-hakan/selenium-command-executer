import os
import sys
from dotenv import load_dotenv
from src.driver.driver import Driver


class Application:
    @staticmethod
    def load():
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(__file__)

        os.chdir(application_path)
        load_dotenv()

    @staticmethod
    def run():
        driver = Driver()
        driver.search()


if __name__ == '__main__':
    Application.load()
    Application.run()
