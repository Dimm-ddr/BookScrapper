from dataclasses import fields
import logging
from typing import Any

from data.datamodel import BookData

from .interface.data_source import DataSourceInterface
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .sources.goodreads import GoodreadsScraper

logger: logging.Logger = logging.getLogger(__name__)


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
        goodreads_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        book_data: dict[str, Any] = {}
        goodreads_cover: str | None = None
        goodreads_series: str | None = None

        for source in self.sources:
            logger.debug(f"Trying to fetch data from {source.__class__.__name__}")
            if isinstance(source, GoodreadsScraper) and goodreads_data:
                new_data = goodreads_data
                goodreads_cover = new_data.get("cover")
                goodreads_series = new_data.get("series")
            elif isbn is not None:
                new_data: dict[str, Any] | None = source.fetch_by_isbn(isbn)
            elif title is not None and author is not None:
                new_data = source.fetch_by_title_author(title, author)
            else:
                raise ValueError(
                    "Either ISBN or both title and author must be provided"
                )

            if new_data:
                logger.debug(f"Data fetched from {source.__class__.__name__}")
                for key, value in new_data.items():
                    if key not in book_data or not book_data[key]:
                        if key != "cover" or (
                            key == "cover" and isinstance(source, GoodreadsScraper)
                        ):
                            book_data[key] = value

                if self._is_data_complete(book_data):
                    logger.debug("All fields filled, stopping further queries")
                    break
            else:
                logger.debug(f"No data found from {source.__class__.__name__}")

        # Use Goodreads cover if available
        if goodreads_cover:
            book_data["cover"] = goodreads_cover

        # Use Goodreads series if available
        if goodreads_series:
            book_data["series"] = goodreads_series

        return book_data or None

    def _is_data_complete(self, data: dict[str, Any]) -> bool:
        expected_fields: set[str] = {field.name for field in fields(BookData)}
        return all(data.get(field) for field in expected_fields)
