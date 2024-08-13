import json
from pathlib import Path
import logging
from typing import Any

from golden_book_retriever.utils.string_utils import normalize_tags
from .sources.goodreads import GoodreadsScraper
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .interface.data_source import DataSourceInterface

logger: logging.Logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Aggregates book data from multiple sources.
    """

    def __init__(self) -> None:
        """
        Initialize the DataAggregator with data sources.
        """
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
        authors: set[str] | None = None,
        existing_goodreads_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Fetch book data from multiple sources.

        Args:
            isbn: The ISBN of the book.
            title: The title of the book.
            authors: A tuple of author names.
            existing_goodreads_data: Pre-existing Goodreads data, if available.

        Returns:
            A dictionary containing the aggregated book data, or None if no data is found.
        """
        book_data: dict[str, Any] = {}
        folder_name: str = self._generate_folder_name(isbn, title, authors)

        for source in reversed(self.sources):
            fetched_data: dict[str, Any] | None = self._fetch_from_source(
                source, isbn, title, authors, existing_goodreads_data
            )
            if fetched_data:
                logger.debug(
                    f"Fetched data from {fetched_data.get('source_name', 'Unknown')}: {fetched_data}"
                )
                self._process_fetched_data(book_data, fetched_data, folder_name)
            else:
                logger.debug(f"No data fetched from {source.__class__.__name__}")

        logger.debug(f"Final aggregated book_data: {book_data}")
        return book_data or None

    def _fetch_from_source(
        self,
        source: DataSourceInterface,
        isbn: str | None,
        title: str | None,
        authors: set[str] | None,
        existing_goodreads_data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """
        Fetch data from a specific source.

        Args:
            source: The data source to fetch from.
            isbn: The ISBN of the book.
            title: The title of the book.
            authors: A tuple of author names.
            existing_goodreads_data: Pre-existing Goodreads data, if available.

        Returns:
            A dictionary containing the fetched data, or None if no data is found.
        """
        source_name: str = source.__class__.__name__
        logger.debug(f"Attempting to fetch data from {source_name}")

        if isinstance(source, GoodreadsScraper):
            return self._fetch_from_goodreads(
                source, isbn, title, authors, existing_goodreads_data
            )
        elif isbn:
            return source.fetch_by_isbn(isbn)
        elif title and authors:
            return source.fetch_by_title_author(title, authors)
        else:
            logger.warning("Insufficient data provided for fetching")
            return None

    def _fetch_from_goodreads(
        self,
        source: GoodreadsScraper,
        isbn: str | None,
        title: str | None,
        authors: set[str] | None,
        existing_goodreads_data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if existing_goodreads_data:
            logger.debug("Using existing Goodreads data")
            return {
                "source_name": "GoodreadsCache",
                "compiled_data": existing_goodreads_data.get("compiled_data", {}),
                "raw_data": None,  # We don't need to save raw data for cached results
            }
        elif isbn:
            return source.fetch_by_isbn(isbn)
        elif title and authors:
            return source.fetch_by_title_author(title, authors)
        return None

    def _process_fetched_data(
        self,
        book_data: dict[str, Any],
        fetched_data: dict[str, Any],
        folder_name: str,
    ) -> None:
        source_name: str = fetched_data.get("source_name", "Unknown")
        logger.debug(f"Processing fetched data from {source_name}")

        compiled_data = fetched_data.get("compiled_data")
        if compiled_data:
            self._merge_data(book_data, compiled_data)
        else:
            logger.debug(f"No compiled data found from {source_name}")

        raw_data = fetched_data.get("raw_data")
        if raw_data:
            self._save_raw_data(folder_name, source_name, raw_data)
        else:
            logger.debug(f"No raw data found from {source_name}")

    def _merge_data(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        if not isinstance(source, dict):
            logger.warning(f"Invalid source data type: {type(source)}. Expected dict.")
            return

        for key, value in source.items():
            if self._is_valid_value(value):
                if key == "tags":
                    existing_tags = set(target.get(key, []))
                    new_tags = set(value) if isinstance(value, list) else {value}
                    target[key] = normalize_tags(list(existing_tags | new_tags))
                elif key in ("authors", "publishers", "languages"):
                    existing_value = target.get(key, set())
                    if isinstance(existing_value, list):
                        existing_value = set(existing_value)
                    if isinstance(value, list):
                        value = set(value)
                    target[key] = list(existing_value | value)
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
        self, isbn: str | None, title: str | None, authors: set[str] | None
    ) -> str:
        if isbn:
            return f"ISBN_{isbn}"
        elif title and authors:
            safe_title: str = "".join(
                c for c in title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()

            # Handle the case where authors is a tuple of strings
            if authors:
                first_author: str = next(
                    iter(authors), ""
                )  # Get the first author safely
                safe_author: str = "".join(
                    c for c in first_author if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                return f"{safe_title}_by_{safe_author}"
            else:
                return safe_title
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
