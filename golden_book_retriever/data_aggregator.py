import json
from pathlib import Path
import logging
from typing import Any, TypeGuard

from black.debug import T

from .sources.goodreads import GoodreadsScraper
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .interface.data_source import DataSourceInterface

logger: logging.Logger = logging.getLogger(__name__)


class DataAggregator:
    def __init__(self) -> None:
        self.sources: tuple[DataSourceInterface, ...] = (
            GoodreadsScraper(),
            GoogleBooksAPI(),
            OpenLibraryAPI(),
        )

    def _check_title_match(self, title1: str, title2: str) -> bool:
        """
        Check if two titles match, ignoring case and punctuation.
        """
        import re

        clean_title1: str = re.sub(r"[^\w\s]", "", title1.lower())
        clean_title2: str = re.sub(r"[^\w\s]", "", title2.lower())
        return clean_title1 == clean_title2

    def _save_raw_data(
        self, folder_name: str, source_name: str, data: dict[str, Any] | None
    ) -> None:
        base_path: Path = Path("data/books/raw_data") / folder_name
        base_path.mkdir(parents=True, exist_ok=True)

        file_path: Path = base_path / f"{source_name}_raw.json"

        if data is None:
            data = {"status": "No data found"}

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Raw data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving raw data to {file_path}: {str(e)}")

    def fetch_data(
        self,
        *,
        isbn: str | None = None,
        title: str | None = None,
        authors: tuple[str, ...] | None = None,
        goodreads_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        book_data: dict[str, Any] = {}

        for source in reversed(self.sources):
            logger.debug(f"Trying to fetch data from {source.__class__.__name__}")
            if isinstance(source, GoodreadsScraper) and goodreads_data:
                new_data = goodreads_data
            elif isbn is not None:
                new_data: dict[str, Any] | None = source.fetch_by_isbn(isbn)
            elif title is not None and authors is not None:
                new_data = source.fetch_by_title_author(title, authors)
            else:
                raise ValueError(
                    "Either ISBN or both title and author must be provided"
                )

            if new_data:
                logger.debug(f"Data fetched from {source.__class__.__name__}")
                self._merge_data(book_data, new_data)

        return book_data or None

    def _merge_data(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key, value in source.items():
            if self._is_valid_value(value):
                if key in ("tags", "authors", "publishers", "languages"):
                    existing_value = target.get(key, set())
                    if isinstance(existing_value, list):
                        existing_value = set(existing_value)
                    if isinstance(value, list):
                        value = set(value)
                    target[key] = existing_value | value
                else:
                    target[key] = value

    @staticmethod
    def _is_valid_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, (str, list, set, dict)):
            return bool(value)
        return True

    def _generate_folder_name(
        self, isbn: str | None, title: str | None, authors: list[str] | None
    ) -> str:
        if isbn:
            return f"ISBN_{isbn}"
        elif title and authors:
            safe_title: str = "".join(
                c for c in title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_author: str = "".join(
                c for c in authors[0] if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            return f"{safe_title}_by_{safe_author}"
        else:
            return "unknown_book"

    def _is_data_complete(self, data: dict[str, Any]) -> bool:
        # Implement your completeness check logic here
        required_fields: list[str] = [
            "title",
            "authors",
            "isbn",
            "description",
            "cover",
        ]
        return all(field in data and data[field] for field in required_fields)
