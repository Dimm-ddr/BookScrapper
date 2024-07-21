import json
from pathlib import Path
import logging
from typing import Any, TypeGuard

from .sources.goodreads import GoodreadsScraper
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .interface.data_source import DataSourceInterface

logger: logging.Logger = logging.getLogger(__name__)


class DataAggregator:
    def __init__(self) -> None:
        self.sources: list[DataSourceInterface] = [
            GoodreadsScraper(),
            OpenLibraryAPI(),
            GoogleBooksAPI(),
        ]

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
        authors: list[str] | None = None,
        goodreads_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        folder_name: str = self._generate_folder_name(isbn, title, authors)
        all_data: dict[str, dict[str, Any] | None] = {}

        for source in self.sources:
            source_name: str = source.__class__.__name__
            logger.info(f"Fetching data from {source_name}")

            try:
                if isinstance(source, GoodreadsScraper) and goodreads_data:
                    new_data = goodreads_data
                elif isbn is not None:
                    new_data = source.fetch_by_isbn(isbn)
                elif title is not None and authors is not None:
                    new_data = source.fetch_by_title_author(title, authors)
                else:
                    raise ValueError(
                        "Either ISBN or both title and author must be provided"
                    )

                if self._is_valid_source_data(new_data):
                    all_data[source_name] = new_data
                    self._save_raw_data(folder_name, source_name, new_data["raw_data"])
                else:
                    logger.warning(f"Invalid or no data received from {source_name}")
                    all_data[source_name] = None
                    self._save_raw_data(folder_name, source_name, None)
            except Exception as e:
                logger.error(
                    f"Error fetching data from {source_name}: {str(e)}", exc_info=True
                )
                all_data[source_name] = None
                self._save_raw_data(folder_name, source_name, None)

        return self._merge_data(all_data)

    def _is_valid_source_data(
        self, data: dict[str, Any] | None
    ) -> TypeGuard[dict[str, Any]]:
        return isinstance(data, dict) and "compiled_data" in data

    def _merge_data(
        self, all_data: dict[str, dict[str, Any] | None]
    ) -> dict[str, Any] | None:
        merged_data: dict[str, Any] = {}
        priority_order: list[str] = [
            "GoodreadsScraper",
            "OpenLibraryAPI",
            "GoogleBooksAPI",
        ]

        for source in priority_order:
            data_source: dict[str, Any] | None = all_data.get(source, None)
            if self._is_valid_source_data(data_source):
                source_data = data_source["compiled_data"]
                if source_data is not None:
                    merged_data.update(source_data)

        return merged_data if merged_data else None

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
