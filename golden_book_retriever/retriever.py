from typing import Any
from .data_aggregator import DataAggregator
from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .sources.goodreads import GoodreadsScraper
import logging

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self) -> None:
        self.aggregator = DataAggregator()
        self.goodreads = GoodreadsScraper()
        self.openlibrary = OpenLibraryAPI()
        self.googlebooks = GoogleBooksAPI()
        self.goodreads_cache: dict[str, Any] | None = None

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        return self.aggregator.fetch_data(
            isbn=isbn, goodreads_data=self.goodreads_cache
        )

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        return self.aggregator.fetch_data(
            title=title, author=author, goodreads_data=self.goodreads_cache
        )

    def fetch_by_goodreads_url(self, url: str) -> dict[str, Any] | None:
        logger.debug(f"Fetching data from Goodreads URL: {url}")
        self.goodreads_cache: dict[str, Any] | None = self.goodreads.fetch_by_url(url)

        if not self.goodreads_cache:
            logger.warning(f"No data found for Goodreads URL: {url}")
            return None

        isbn = self.goodreads_cache.get("isbn")
        title = self.goodreads_cache.get("title")
        author = self.goodreads_cache.get("authors", [None])[0]

        if isbn:
            logger.debug(f"ISBN found: {isbn}. Fetching data from all sources.")
            combined_data: dict[str, Any] | None = self.fetch_by_isbn(isbn)
        elif title and author:
            logger.debug("Title and author found. Fetching data from all sources.")
            combined_data = self.fetch_by_title_author(title, author)
        else:
            logger.warning(
                "Insufficient data from Goodreads to fetch from other sources."
            )
            return self.goodreads_cache

        if combined_data:
            # Prioritize Goodreads data for certain fields
            for field in ["link", "description", "cover"]:
                if self.goodreads_cache.get(field):
                    combined_data[field] = self.goodreads_cache[field]

            # Merge tags and authors
            combined_data["tags"] = list(
                set(
                    combined_data.get("tags", []) + self.goodreads_cache.get("tags", [])
                )
            )
            combined_data["authors"] = list(
                set(
                    combined_data.get("authors", [])
                    + self.goodreads_cache.get("authors", [])
                )
            )

            return combined_data
        else:
            logger.warning("No additional data found from other sources.")
            return self.goodreads_cache
