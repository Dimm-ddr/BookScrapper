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

    def fetch_by_title_author(
        self, title: str, authors: list[str]
    ) -> dict[str, Any] | None:
        return self.aggregator.fetch_data(
            title=title, authors=authors, goodreads_data=self.goodreads_cache
        )

    def fetch_by_goodreads_url(self, url: str) -> dict[str, Any] | None:
        logger.debug(f"Fetching data from Goodreads URL: {url}")
        goodreads_data: dict[str, Any] | None = self.goodreads.fetch_by_url(url)

        if not goodreads_data or "compiled_data" not in goodreads_data:
            logger.warning(f"No valid data found for Goodreads URL: {url}")
            return None

        self.goodreads_cache = goodreads_data

        compiled_data = goodreads_data["compiled_data"]
        isbn = compiled_data.get("isbn")
        title = compiled_data.get("title")
        authors = compiled_data.get("authors", [])
        logger.info(f"ISBN: {isbn}, Title: {title}, Authors: {authors}")

        if isbn:
            logger.debug(f"ISBN found: {isbn}. Fetching data from all sources.")
            return self.fetch_by_isbn(isbn)
        elif title and authors:
            logger.debug(f"Title and author(s) found. Fetching data from all sources.")
            return self.fetch_by_title_author(
                title, authors[0]
            )  # Using first author for now
        else:
            logger.warning(
                "Insufficient data from Goodreads to fetch from other sources."
            )
            return self.goodreads_cache
