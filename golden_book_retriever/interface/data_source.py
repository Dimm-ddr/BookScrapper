from abc import ABC, abstractmethod
from typing import Any

from golden_book_retriever.utils.raw_data_handler import save_raw_data


class DataSourceInterface(ABC):
    @abstractmethod
    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """Fetch book data by ISBN."""
        pass

    @abstractmethod
    def fetch_by_title_author(
        self, title: str, authors: set[str]
    ) -> dict[str, Any] | None:
        """Fetch book data by title and authors."""
        pass

    def save_raw_data(self, folder_name: str, data: dict[str, Any] | None) -> None:
        """Save raw data from the source."""
        save_raw_data(folder_name, self.__class__.__name__, data)
