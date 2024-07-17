from typing import Any
from .data_aggregator import DataAggregator
from .sources.goodreads import GoodreadsScraper
import logging

logger: logging.Logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self) -> None:
        self.aggregator = DataAggregator()
        self.goodreads = GoodreadsScraper()
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
            return self.fetch_by_isbn(isbn)
        elif title and author:
            logger.debug("Title and author found. Fetching data from all sources.")
            return self.fetch_by_title_author(title, author)
        else:
            logger.warning(
                "Insufficient data from Goodreads to fetch from other sources."
            )
            return self.goodreads_cache
