from abc import ABC, abstractmethod

class DataSourceInterface(ABC):
    @abstractmethod
    def fetch_by_isbn(self, isbn):
        pass

    @abstractmethod
    def fetch_by_title_author(self, title, author):
        pass