from abc import ABC, abstractmethod
from typing import Any


class DataSourceInterface(ABC):
    @abstractmethod
    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """Fetch book data by ISBN."""
        pass

    @abstractmethod
    def fetch_by_title_author(
        self, title: str, authors: list[str]
    ) -> dict[str, Any] | None:
        """Fetch book data by title and authors."""
        pass
