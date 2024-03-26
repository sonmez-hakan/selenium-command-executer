import os
import sys
from dotenv import load_dotenv
from src.application import Application
from src.utils import staticclass


@staticclass
class Bootstrap:
    @staticmethod
    def load():
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(__file__)

        os.chdir(application_path)
        load_dotenv()


if __name__ == '__main__':
    Bootstrap.load()
    Application.run()
