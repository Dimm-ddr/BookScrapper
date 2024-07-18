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
        return self.fetch_by_url(url)

    def fetch_by_title_author(
        self, title: str, authors: list[str]
    ) -> dict[str, Any] | None:
        # This method is not implemented for Goodreads
        return None

    def fetch_by_url(self, url: str) -> dict[str, Any] | None:
        try:
            response = self._fetch_page(url)
            json_data = self._extract_json_data(response)
            apollo_state = json_data["props"]["pageProps"]["apolloState"]
            combined_book_data = self._combine_book_data(apollo_state)
            series_data = self._extract_series_data(apollo_state)
            return self._compile_result(combined_book_data, series_data, url)
        except Exception as e:
            logger.error(f"Error scraping data from {url}: {str(e)}", exc_info=True)
            self._save_response_and_exit(response)
            return None

    def _fetch_page(self, url: str) -> requests.Response:
        response = requests.get(url)
        response.raise_for_status()
        return response

    def _extract_json_data(self, response: requests.Response) -> dict[str, Any]:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag or not isinstance(script_tag, Tag) or not script_tag.string:
            raise ValueError("Invalid or missing script tag")
        return json.loads(script_tag.string)

    def _combine_book_data(self, apollo_state: dict[str, Any]) -> dict[str, Any]:
        book_keys = [key for key in apollo_state.keys() if key.startswith("Book:")]
        if not book_keys:
            raise ValueError("No book data found in the response")
        combined_book_data: dict[str, Any] = {}
        for key in book_keys:
            self._update_combined_data(combined_book_data, apollo_state[key])
        return combined_book_data

    def _extract_series_data(
        self, apollo_state: dict[str, Any]
    ) -> dict[str, Any] | None:
        series_key: str | None = next(
            (key for key in apollo_state.keys() if key.startswith("Series:")), None
        )
        return apollo_state.get(series_key) if series_key else None

    def _compile_result(
        self, book_data: dict[str, Any], series_data: dict[str, Any] | None, url: str
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": book_data.get("title"),
            "authors": self._get_authors(book_data),
            "cover": book_data.get("imageUrl"),
            "description": book_data.get("description"),
            "tags": list(
                set(genre["genre"]["name"] for genre in book_data.get("bookGenres", []))
            ),
            "page_count": book_data.get("details", {}).get("numPages"),
            "link": url,
            "isbn": book_data.get("details", {}).get("isbn13")
            or book_data.get("details", {}).get("isbn"),
            "language": book_data.get("details", {}).get("language", {}).get("name"),
            "publish_date": book_data.get("details", {}).get("publicationTime"),
            "publishers": list(
                set(filter(None, [book_data.get("details", {}).get("publisher")]))
            ),
            "series": series_data.get("title") if series_data else None,
        }
        return {k: v for k, v in result.items() if v is not None and v != []}

    def _update_combined_data(
        self, combined_data: dict[str, Any], new_data: dict[str, Any]
    ) -> None:
        for key, value in new_data.items():
            if value is None or value == [] or value == {}:
                continue
            if key not in combined_data:
                combined_data[key] = value
            elif isinstance(value, list):
                if isinstance(combined_data[key], list):
                    combined_data[key] = list(set(combined_data[key] + value))
                else:
                    combined_data[key] = [combined_data[key], value]
            elif isinstance(value, dict):
                if not isinstance(combined_data[key], dict):
                    combined_data[key] = {}
                self._update_combined_data(combined_data[key], value)
            elif combined_data[key] != value:
                if not isinstance(combined_data[key], list):
                    combined_data[key] = [combined_data[key]]
                if value not in combined_data[key]:
                    combined_data[key].append(value)

    def _get_authors(self, book_data: dict[str, Any]) -> list[str]:
        authors = []
        if "primaryContributorEdge" in book_data:
            primary_author = (
                book_data["primaryContributorEdge"].get("node", {}).get("name")
            )
            if primary_author:
                authors.append(primary_author)
        if "secondaryContributorEdges" in book_data:
            secondary_authors = [
                edge.get("node", {}).get("name")
                for edge in book_data["secondaryContributorEdges"]
            ]
            authors.extend(filter(None, secondary_authors))
        return list(set(authors))

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
