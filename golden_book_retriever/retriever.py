from typing import Any
from .data_aggregator import DataAggregator
from .sources.goodreads import GoodreadsScraper
import logging

logger: logging.Logger = logging.getLogger(__name__)


class Retriever:
    """
    A class to retrieve book data from various sources.
    """

    def __init__(self) -> None:
        """
        Initialize the Retriever with a DataAggregator and GoodreadsScraper.
        """
        self.aggregator = DataAggregator()
        self.goodreads = GoodreadsScraper()
        self.goodreads_cache: dict[str, Any] | None = None

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book data using an ISBN.

        Args:
            isbn: The ISBN of the book to fetch.

        Returns:
            A dictionary containing the book data, or None if no data is found.
        """
        return self.aggregator.fetch_data(
            isbn=isbn, existing_goodreads_data=self.goodreads_cache
        )

    def fetch_by_title_author(
        self, title: str, authors: set[str]
    ) -> dict[str, Any] | None:
        """
        Fetch book data using a title and author(s).

        Args:
            title: The title of the book.
            authors: A tuple of author names.

        Returns:
            A dictionary containing the book data, or None if no data is found.
        """
        return self.aggregator.fetch_data(
            title=title, authors=authors, existing_goodreads_data=self.goodreads_cache
        )

    def fetch_by_goodreads_url(self, url: str) -> dict[str, Any] | None:
        """
        Fetch book data from a Goodreads URL.

        This method first fetches data from Goodreads, then attempts to fetch
        additional data from other sources using the ISBN or title and author(s).

        Args:
            url: The Goodreads URL of the book.

        Returns:
            A dictionary containing the book data, or None if no data is found.
        """
        logger.debug(f"Fetching data from Goodreads URL: {url}")
        goodreads_data: dict[str, Any] | None = self.goodreads.fetch_by_url(url)

        if not goodreads_data or "compiled_data" not in goodreads_data:
            logger.warning(f"No valid data found for Goodreads URL: {url}")
            return None

        logger.debug(
            f"Raw Goodreads data: {goodreads_data.get('raw_data', 'No raw data')}"
        )

        self.goodreads_cache = goodreads_data

        compiled_data = goodreads_data["compiled_data"]
        logger.debug(f"Compiled data from Goodreads: {compiled_data}")

        # Save Goodreads raw data
        folder_name: str = self.aggregator._generate_folder_name(
            isbn=compiled_data.get("isbn"),
            title=compiled_data.get("title"),
            authors=set(compiled_data.get("authors", [])),
        )
        self.aggregator._save_raw_data(
            folder_name, "Goodreads", goodreads_data.get("raw_data")
        )

        isbn = compiled_data.get("isbn")
        title = compiled_data.get("title")
        authors = compiled_data.get("authors", ())
        logger.info(f"ISBN: {isbn}, Title: {title}, Authors: {authors}")

        result = None
        if isbn:
            logger.debug(f"ISBN found: {isbn}. Fetching data from all sources.")
            result: dict[str, Any] | None = self.fetch_by_isbn(isbn)
        elif title and authors:
            logger.debug(f"Title and author(s) found. Fetching data from all sources.")
            result = self.fetch_by_title_author(title, set(authors))
        else:
            logger.warning(
                "Insufficient data from Goodreads to fetch from other sources."
            )
            result = compiled_data

        # Clear the Goodreads cache after we're done with this book
        self.goodreads_cache = None

        return result
