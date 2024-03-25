import json
import os
from src.utils import staticclass

class Url:
    def __init__(self, url: str, url_type: str | None = 'web'):
        self.url = _File(url) if url_type is not None and url_type.lower() == 'file' else _Url(url)

    def get(self) -> str:
        return self.url.get()


class _Url:
    def __init__(self, url: str):
        self.url = url

    def get(self) -> str:
        return self.url


class _File:
    def __init__(self, url: str):
        self.url = f"file:///{os.getcwd()}/{url.lstrip('/')}"

    def get(self) -> str:
        return self.url

@staticclass
class Reader:
    @staticmethod
    def read():
        path = f"{os.getcwd()}/sites"
        for element in os.listdir(path):
            file_name = os.path.join(path, element)
            if os.path.isfile(file_name) and element[0] != '.':
                file = open(file_name, 'r')
                yield json.loads(file.read())

