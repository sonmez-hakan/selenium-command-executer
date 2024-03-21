from abc import ABC, abstractmethod


class Browser(ABC):
    @abstractmethod
    def get(self):
        pass
