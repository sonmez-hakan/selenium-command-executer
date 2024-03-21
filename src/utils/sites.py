import json
import os


class Sites:
    @staticmethod
    def read():
        path = f"{os.getcwd()}/sites"
        for element in os.listdir(path):
            file_name = os.path.join(path, element)
            if os.path.isfile(file_name):
                file = open(file_name, 'r')
                yield json.loads(file.read())

