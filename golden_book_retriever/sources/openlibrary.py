import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class OpenLibraryAPI(DataSourceInterface):
    BASE_URL = "https://openlibrary.org/search.json"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book data from OpenLibrary by ISBN.

        Args:
            isbn: The ISBN of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        params: dict[str, str] = {"q": f"isbn:{isbn}"}
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("numFound", 0) > 0:
                return self._parse_data(data["docs"][0])
        return None

    def fetch_by_title_author(
        self, title: str, authors: list[str]
    ) -> dict[str, Any] | None:
        """
        Fetch book data from OpenLibrary by title and author.

        Args:
            title: The title of the book to fetch.
            author: The author of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        # Use the first author for the search, but keep all authors in the result
        author: str = authors[0] if authors else ""
        params: dict[str, str] = {"q": f"title:{title} author:{author}"}
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("numFound", 0) > 0:
                return self._parse_data(data["docs"][0])
        return None

    def _parse_data(self, data: dict[str, Any]) -> dict[str, Any]:
        # Enrich description with first_sentence if available
        description = data.get("description")
        first_sentence = data.get("first_sentence")
        if description and first_sentence and first_sentence not in description:
            description = f"{first_sentence} {description}"

        # Combine subject, person, place, and time for a richer tags field
        tags = (
            data.get("subject", [])
            + data.get("person", [])
            + data.get("place", [])
            + data.get("time", [])
        )

        # Use alternative_title if title is not available
        title = data.get("title") or data.get("alternative_title")

        # Combine author_name and author_alternative_name for a more comprehensive authors list
        authors = list(
            set(
                data.get("author_name", [])
                + data.get("author_alternative_name", [])
                + [data.get("by_statement")]
                if data.get("by_statement")
                else []
            )
        )

        # Use the median number of pages if available
        page_count = data.get("number_of_pages_median")

        publishers = data.get("publisher", [])
        if isinstance(publishers, str):
            publishers = [publishers]

        return {
            "title": title,
            "first_publish_year": data.get("first_publish_year"),
            "link": (
                f"https://openlibrary.org{data.get('key')}" if data.get("key") else None
            ),
            "description": description,
            "cover": (
                f"https://covers.openlibrary.org/b/id/{data.get('cover_i')}-L.jpg"
                if data.get("cover_i")
                else None
            ),
            "page_count": page_count,
            "editions_count": data.get("edition_count"),
            "isbn": (
                data.get("isbn", [None])[0]
                if isinstance(data.get("isbn"), list)
                else data.get("isbn")
            ),
            "authors": authors,
            "languages": data.get("language", []),
            "tags": tags,
            "publishers": publishers,
            # OpenLibrary doesn't provide series information
            "series": None,
        }
