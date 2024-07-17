import json
from venv import logger
import requests
from typing import Any, TypeGuard
from bs4 import BeautifulSoup, Tag
import sys
from datetime import datetime
from ..interface.data_source import DataSourceInterface


def is_valid_script_tag(tag: Any) -> TypeGuard[Tag]:
    return isinstance(tag, Tag) and hasattr(tag, "string")


class GoodreadsScraper(DataSourceInterface):
    BASE_URL: str = "https://www.goodreads.com/book/isbn/"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        url: str = f"{self.BASE_URL}{isbn}"
        return self._scrape_data(url)

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        # This method is not implemented for Goodreads
        return None

    def fetch_by_url(self, url: str) -> dict[str, Any] | None:
        return self._scrape_data(url)

    def _scrape_data(self, url: str) -> dict[str, Any] | None:
        response: requests.Response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")

        if not script_tag:
            self._save_response_and_exit(response)
        elif not is_valid_script_tag(script_tag):
            logger.error("Script tag is not valid.")
            self._save_response_and_exit(response)

        try:
            json_data = json.loads(script_tag.string)  # type: ignore
        except json.JSONDecodeError:
            self._save_response_and_exit(response)

        apollo_state = json_data["props"]["pageProps"]["apolloState"]

        # Find book data
        book_key = next(
            (key for key in apollo_state.keys() if key.startswith("Book:")), None
        )
        if not book_key:
            logger.error("No book data found in the response.")
            self._save_response_and_exit(response)

        book_data = apollo_state[book_key]
        print(f"book data: {book_data}")

        # Find series data
        series_key = next(
            (key for key in apollo_state.keys() if key.startswith("Series:")), None
        )
        series_data = apollo_state.get(series_key) if series_key else None

        publisher = book_data.get("details", {}).get("publisher")
        publishers = [publisher] if publisher else []

        # Extract relevant information
        result: dict[str, Any] = {
            "title": book_data.get("title"),
            "authors": (
                [
                    book_data.get("primaryContributorEdge", {})
                    .get("node", {})
                    .get("name", "Unknown")
                ]
                if book_data.get("primaryContributorEdge")
                else []
            ),
            "cover": book_data.get("imageUrl"),
            "description": book_data.get("description"),
            "tags": [
                genre["genre"]["name"] for genre in book_data.get("bookGenres", [])
            ],
            "page_count": book_data.get("details", {}).get("numPages"),
            "link": url,
            "isbn": book_data.get("details", {}).get("isbn13")
            or book_data.get("details", {}).get("isbn"),
            "language": book_data.get("details", {}).get("language", {}).get("name"),
            "publish_date": book_data.get("details", {}).get("publicationTime"),
            "publishers": publishers,
            "series": None,  # Default to None
        }

        # Add series information if available
        if series_data:
            result["series"] = series_data.get("title")

        return result

    def _save_response_and_exit(self, response: requests.Response) -> None:
        """
        Save the response content to a file and exit the program.
        """
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename: str = f"goodreads_response_{timestamp}.html"

        soup = BeautifulSoup(response.text, "html.parser")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        print(f"Goodreads page structure has changed. Response saved to {filename}")
        print("Please check the file and update the scraper accordingly.")
        sys.exit(1)  # Exit the entire program

    # The rest of the class remains the same
