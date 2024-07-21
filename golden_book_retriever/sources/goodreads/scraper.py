import requests
from bs4 import BeautifulSoup, Tag
import json
import logging
from typing import Any

from golden_book_retriever.interface.data_source import DataSourceInterface
from .extractors import BookDataExtractor

logger: logging.Logger = logging.getLogger(__name__)


class GoodreadsScraper(DataSourceInterface):
    BASE_URL: str = "https://www.goodreads.com/book/isbn/"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        url: str = f"{self.BASE_URL}{isbn}"
        return self.fetch_by_url(url)

    def fetch_by_title_author(
        self, title: str, authors: list[str]
    ) -> dict[str, Any] | None:
        # This method is not implemented for Goodreads
        logger.warning("fetch_by_title_author is not implemented for Goodreads")
        return None

    def fetch_by_url(self, url: str) -> dict[str, Any] | None:
        try:
            response: requests.Response = self._fetch_page(url)
            apollo_state: dict[str, Any] = self._extract_apollo_state(response)
            extractor = BookDataExtractor(apollo_state)
            book_data: dict[str, Any] = extractor.extract()
            logger.info(f"compiled_data: {book_data}")
            return {"raw_data": apollo_state, "compiled_data": book_data}
        except Exception as e:
            logger.error(f"Error scraping data from {url}: {str(e)}", exc_info=True)
            return None

    def _fetch_page(self, url: str) -> requests.Response:
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        return response

    def _extract_apollo_state(self, response: requests.Response) -> dict[str, Any]:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag or not isinstance(script_tag, Tag) or not script_tag.string:
            raise ValueError("Invalid or missing script tag")
        json_data = json.loads(script_tag.string)
        return json_data["props"]["pageProps"]["apolloState"]
