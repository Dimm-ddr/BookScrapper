from typing import Any
from .data_aggregator import DataAggregator
from .utils.isbn_utils import is_valid_isbn, normalize_isbn

class Retriever:
    def __init__(self) -> None:
        self.aggregator = DataAggregator()

    def fetch_by_isbn(self, isbn) -> dict[str, Any]:
        if not is_valid_isbn(isbn):
            raise ValueError("Invalid ISBN")
        normalized_isbn = normalize_isbn(isbn)
        return self.aggregator.fetch_data(isbn=normalized_isbn)

    def fetch_by_title_author(self, title, author) -> dict[str, Any]:
        return self.aggregator.fetch_data(title=title, author=author)