import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class OpenLibraryAPI(DataSourceInterface):
    BASE_URL = "https://openlibrary.org/api/books"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book data from OpenLibrary by ISBN.

        Args:
            isbn: The ISBN of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        response: requests.Response = requests.get(
            f"{self.BASE_URL}?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        )
        if response.status_code == 200:
            data = response.json().get(f"ISBN:{isbn}")
            if data:
                return self._parse_data(data)
        return None

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        """
        Fetch book data from OpenLibrary by title and author.

        Args:
            title: The title of the book to fetch.
            author: The author of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        search_url: str = (
            f"https://openlibrary.org/search.json?title={title}&author={author}"
        )
        response: requests.Response = requests.get(search_url)
        if response.status_code == 200:
            results = response.json().get("docs", [])
            if results:
                isbn = results[0].get("isbn", [])
                if isbn:
                    return self.fetch_by_isbn(isbn[0])
        return None

    def _parse_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the raw data from OpenLibrary into a standardized format.

        Args:
            data: The raw data from OpenLibrary.

        Returns:
            A dictionary containing parsed book information.
        """
        return {
            "title": data.get("title"),
            "authors": [author.get("name") for author in data.get("authors", [])],
            "isbn": data.get("identifiers", {}).get("isbn_13", [None])[0],
            "description": (
                data.get("description", {}).get("value")
                if isinstance(data.get("description"), dict)
                else data.get("description")
            ),
            "cover": data.get("cover", {}).get("large"),
            "publish_date": data.get("publish_date"),
            "publisher": data.get("publishers", [{}])[0].get("name"),
            "page_count": data.get("number_of_pages"),
        }
