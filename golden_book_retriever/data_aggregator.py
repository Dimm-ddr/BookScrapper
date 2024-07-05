from typing import Any, TypeGuard, Literal

from .interface.data_source import DataSourceInterface
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .sources.goodreads import GoodreadsScraper


class DataAggregator:
    """
    Aggregates data from multiple book information sources.

    This class manages the priority-based data fetching from different sources
    and combines the results.
    """

    def __init__(self) -> None:
        """Initialize the DataAggregator with data sources in priority order."""
        self.sources: list[DataSourceInterface] = [
            OpenLibraryAPI(),
            GoogleBooksAPI(),
            GoodreadsScraper(),
        ]

    def fetch_data(
        self,
        *,
        isbn: str | None = None,
        title: str | None = None,
        author: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Fetch book data from multiple sources based on provided identifiers.

        This method attempts to fetch data from each source in order of priority,
        stopping when complete data is found or all sources have been tried.

        Args:
            isbn: The ISBN of the book to fetch.
            title: The title of the book to fetch.
            author: The author of the book to fetch.

        Returns:
            A dictionary containing aggregated book information,
            or None if no data is found.

        Raises:
            ValueError: If neither ISBN nor both title and author are provided.
        """
        book_data: dict[str, Any] = {}

        for source in self.sources:
            if isbn is not None:
                new_data: dict[str, Any] | None = source.fetch_by_isbn(isbn)
            elif title is not None and author is not None:
                new_data = source.fetch_by_title_author(title, author)
            else:
                raise ValueError(
                    "Either ISBN or both title and author must be provided"
                )

            if new_data:
                book_data |= new_data
                if self._is_data_complete(book_data):
                    break

        return book_data or None

    @staticmethod
    def _is_data_complete(data: dict[str, Any]) -> bool:
        """
        Check if the collected book data is complete.

        Args:
            data: The book data to check.

        Returns:
            True if the data is complete, False otherwise.
        """
        required_fields: set[str] = {"title", "authors", "isbn", "description"}
        return required_fields.issubset(data.keys())
