import os
import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class GoogleBooksAPI(DataSourceInterface):
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self) -> None:
        self.API_KEY: str | None = os.getenv("GOOGLE_BOOKS_API_KEY")
        if not self.API_KEY:
            raise ValueError("GOOGLE_BOOKS_API_KEY environment variable is not set")

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        params: dict[str, Any] = {"q": f"isbn:{isbn}", "key": self.API_KEY}
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            raw_data = response.json()
            compiled_data: dict[str, Any] | None = (
                self._parse_data(raw_data.get("items", [{}])[0])
                if raw_data.get("items")
                else None
            )
            return {"raw_data": raw_data, "compiled_data": compiled_data}
        return None

    def fetch_by_title_author(
        self, title: str, authors: set[str]
    ) -> dict[str, Any] | None:
        # Construct a query that includes the title and any of the authors
        author_query: str = " OR ".join(f"inauthor:{author}" for author in authors)
        query: str = f"intitle:{title} AND ({author_query})"

        params: dict[str, Any] = {
            "q": query,
            "key": self.API_KEY,
        }

        response: requests.Response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            raw_data = response.json()
            if raw_data.get("items"):
                for item in raw_data["items"]:
                    parsed_data: dict[str, Any] = self._parse_data(item)
                    if (
                        parsed_data.get("title")
                        and set(parsed_data.get("authors", [])) & authors
                    ):
                        return {"raw_data": raw_data, "compiled_data": parsed_data}

        return None

    def _parse_data(self, item: dict[str, Any]) -> dict[str, Any]:
        volume_info = item.get("volumeInfo", {})

        # Extract ISBN-13 if available, otherwise use ISBN-10
        isbn = next(
            (
                id["identifier"]
                for id in volume_info.get("industryIdentifiers", [])
                if id["type"] == "ISBN_13"
            ),
            None,
        )
        if not isbn:
            isbn = next(
                (
                    id["identifier"]
                    for id in volume_info.get("industryIdentifiers", [])
                    if id["type"] == "ISBN_10"
                ),
                None,
            )

        # Enrich description with subtitle if available
        description = volume_info.get("description", "")
        subtitle = volume_info.get("subtitle")
        if subtitle and subtitle not in description:
            description: str = f"{subtitle}\n\n{description}".strip()

        # Use categories as tags
        tags = volume_info.get("categories", [])

        # Extract year from publishedDate
        publish_year = None
        published_date = volume_info.get("publishedDate")
        if published_date:
            publish_year = int(published_date.split("-")[0])

        publisher = volume_info.get("publisher")
        publishers: list[Any] = [publisher] if publisher else []

        return {
            "title": volume_info.get("title"),
            "first_publish_year": publish_year,
            "link": volume_info.get("infoLink"),
            "description": description,
            "cover": volume_info.get("imageLinks", {}).get("thumbnail"),
            "page_count": volume_info.get("pageCount"),
            "editions_count": None,  # Not available in Google Books API
            "isbn": isbn,
            "authors": volume_info.get("authors", []),
            "languages": (
                [volume_info.get("language")] if volume_info.get("language") else []
            ),
            "tags": tags,
            "publishers": publishers,
            "series": None,  # Google Books API doesn't provide series information
        }
