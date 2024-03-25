import csv
import os
from abc import ABC, abstractmethod

PATH = os.environ.get('REPORTS_PATH', 'reports')


class Output(ABC):
    @abstractmethod
    def write(self, records: list, file_options: dict) -> None:
        pass


class CSV(Output):
    def write(self, records: list, file_options: dict):
        file_name = f"{PATH}/{file_options.get('name')}.csv"
        headers = records[0].keys()

        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
