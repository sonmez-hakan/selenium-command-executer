import os
from src.driver.chrome import Chrome
from src.driver.safari import Safari


class Factory:
    @staticmethod
    def create() -> Safari | Chrome:
        browser = os.environ.get('BROWSER', 'chrome').lower()
        if browser == 'safari':
            return Safari()
        else:
            return Chrome()
