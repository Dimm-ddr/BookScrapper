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
    def __init__(self) -> None:
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

        for source in self.sources:
            logger.debug(f"Trying to fetch data from {source.__class__.__name__}")
            if isinstance(source, GoodreadsScraper) and goodreads_data:
                new_data = goodreads_data
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
                self._merge_data(book_data, new_data)

                if self._is_data_complete(book_data):
                    logger.debug("All fields filled, stopping further queries")
                    break
            else:
                logger.debug(f"No data found from {source.__class__.__name__}")

        return book_data or None

    def _merge_data(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key, value in source.items():
            if key not in target or not target[key]:
                target[key] = value
            elif key in ["tags", "authors", "publishers", "languages"]:
                target[key] = list(set(target[key] + value))

        # Prioritize certain fields from Goodreads
        for field in ["link", "description", "cover"]:
            if field in source:
                target[field] = source[field]

    def _is_data_complete(self, data: dict[str, Any]) -> bool:
        expected_fields: set[str] = {field.name for field in fields(BookData)}
        return all(data.get(field) for field in expected_fields)
