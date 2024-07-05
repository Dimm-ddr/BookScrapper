import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class GoogleBooksAPI(DataSourceInterface):
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book data from Google Books by ISBN.

        Args:
            isbn: The ISBN of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        response: requests.Response = requests.get(f"{self.BASE_URL}?q=isbn:{isbn}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
        return None

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        """
        Fetch book data from Google Books by title and author.

        Args:
            title: The title of the book to fetch.
            author: The author of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        query: str = f"intitle:{title}+inauthor:{author}"
        response: requests.Response = requests.get(f"{self.BASE_URL}?q={query}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
        return None

    def _parse_data(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the raw data from Google Books into a standardized format.

        Args:
            item: The raw data from Google Books.

        Returns:
            A dictionary containing parsed book information.
        """
        volume_info = item.get("volumeInfo", {})
        return {
            "title": volume_info.get("title"),
            "authors": volume_info.get("authors", []),
            "isbn": next(
                (
                    id["identifier"]
                    for id in volume_info.get("industryIdentifiers", [])
                    if id["type"] == "ISBN_13"
                ),
                None,
            ),
            "description": volume_info.get("description"),
            "cover": volume_info.get("imageLinks", {}).get("thumbnail"),
            "publish_date": volume_info.get("publishedDate"),
            "publisher": volume_info.get("publisher"),
            "page_count": volume_info.get("pageCount"),
        }
