import os
import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class GoogleBooksAPI(DataSourceInterface):
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    API_KEY: str | None = os.getenv("GOOGLE_BOOKS_API_KEY")

    def __init__(self) -> None:
        if not self.API_KEY:
            raise ValueError("GOOGLE_BOOKS_API_KEY environment variable is not set")

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        params: dict[str, Any] = {"q": f"isbn:{isbn}", "key": self.API_KEY}
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
        return None

    def fetch_by_title_author(self, title: str, authors: list[str]) -> dict[str, Any] | None:
        author = authors[0] if authors else ""
        params: dict[str, Any] = {
            "q": f"intitle:{title}+inauthor:{author}",
            "key": self.API_KEY,
        }
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
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
            description = f"{subtitle}\n\n{description}".strip()

        # Use categories as tags
        tags = volume_info.get("categories", [])

        # Extract year from publishedDate
        publish_year = None
        published_date = volume_info.get("publishedDate")
        if published_date:
            publish_year = int(published_date.split("-")[0])

        publisher = volume_info.get("publisher")
        publishers = [publisher] if publisher else []

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
