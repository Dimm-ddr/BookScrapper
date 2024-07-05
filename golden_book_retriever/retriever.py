from typing import Any
from .data_aggregator import DataAggregator
from .utils.isbn_utils import is_valid_isbn, normalize_isbn


class Retriever:
    """
    Main class for retrieving book information.

    This class provides a high-level interface for fetching book data
    by ISBN or title and author, abstracting away the complexity of
    multiple data sources.
    """

    def __init__(self) -> None:
        """Initialize the Retriever with a DataAggregator."""
        self.aggregator = DataAggregator()

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book information by ISBN.

        Args:
            isbn (str): The ISBN of the book to fetch.

        Returns:
            dict[str, Any] | None: A dictionary containing book information,
                                   or None if no data is found.

        Raises:
            ValueError: If the provided ISBN is invalid.
        """
        if not is_valid_isbn(isbn):
            raise ValueError(f"Invalid ISBN: {isbn}")
        normalized_isbn: str = normalize_isbn(isbn)
        return self.aggregator.fetch_data(isbn=normalized_isbn)

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        """
        Fetch book information by title and author.

        Args:
            title (str): The title of the book to fetch.
            author (str): The author of the book to fetch.

        Returns:
            dict[str, Any] | None: A dictionary containing book information,
                                   or None if no data is found.
        """
        return self.aggregator.fetch_data(title=title, author=author)
