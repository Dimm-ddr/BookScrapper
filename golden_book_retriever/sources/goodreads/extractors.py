# extractors.py

import logging
import re
from typing import Any, Dict
from bs4 import BeautifulSoup

logger: logging.Logger = logging.getLogger(__name__)


class BookDataExtractor:
    def __init__(self, apollo_state: Dict[str, Any]) -> None:
        self.apollo_state: Dict[str, Any] = apollo_state
        self.combined_book_data: Dict[str, Any] = self._combine_book_data()

    def extract(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "title": self._extract_title(),
            "authors": self._extract_authors(),
            "cover": self._extract_cover(),
            "description": self._extract_description(),
            "tags": self._extract_tags(),
            "page_count": self._extract_page_count(),
            "link": self._extract_link(),
            "isbn": self._extract_isbn(),
            "languages": self._extract_languages(),
            "publish_date": self._extract_publish_date(),
            "publishers": self._extract_publishers(),
            "series": self._extract_series(),
        }
        return {k: v for k, v in result.items() if v is not None and v != set()}

    def _combine_book_data(self) -> Dict[str, Any]:
        combined_data: Dict[str, Any] = {}
        for key, value in self.apollo_state.items():
            if key.startswith("Book:"):
                combined_data.update(value)
        return combined_data

    def _extract_title(self) -> str:
        return self.combined_book_data.get("title", "")

    def _extract_cover(self) -> str:
        return self.combined_book_data.get("imageUrl", "")

    def _extract_description(self) -> str:
        description = self.combined_book_data.get("description", "")
        return self._clean_html(description)

    def _clean_html(self, html_content: str) -> str:
        # Remove HTML tags
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        # Fix spacing after punctuation
        text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _extract_page_count(self) -> int:
        return self.combined_book_data.get("details", {}).get("numPages", 0)

    def _extract_link(self) -> str:
        return self.combined_book_data.get("webUrl", "")

    def _extract_isbn(self) -> str:
        details = self.combined_book_data.get("details", {})
        return details.get("isbn13", "") or details.get("isbn", "")

    def _extract_publish_date(self) -> str:
        return self.combined_book_data.get("details", {}).get("publicationTime", "")

    def _extract_authors(self) -> set[str]:
        authors = set()
        for key, value in self.apollo_state.items():
            if key.startswith("Contributor:"):
                author_name = value.get("name", "")
                if author_name:
                    authors.add(author_name)
                    logger.debug(f"Added author: {author_name}")
        return authors

    def _extract_tags(self) -> set[str]:
        return {
            genre["genre"]["name"]
            for genre in self.combined_book_data.get("bookGenres", [])
            if genre.get("genre", {}).get("name")
        }

    def _extract_languages(self) -> set[str]:
        language = (
            self.combined_book_data.get("details", {})
            .get("language", {})
            .get("name", "")
        )
        return {language} if language else set()

    def _extract_publishers(self) -> set[str]:
        publisher = self.combined_book_data.get("details", {}).get("publisher", "")
        return {publisher} if publisher else set()

    def _extract_series(self) -> str:
        for key, value in self.apollo_state.items():
            if key.startswith("Series:"):
                return value.get("title", "")
        return ""
