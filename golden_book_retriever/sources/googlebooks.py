from typing import Any
import requests
from ..interface.data_source import DataSourceInterface

class GoogleBooksAPI(DataSourceInterface):
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def fetch_by_isbn(self, isbn) -> dict[str, Any] | None:
        response = requests.get(f"{self.BASE_URL}?q=isbn:{isbn}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
        return None

    def fetch_by_title_author(self, title, author) -> dict[str, Any] | None:
        query = f"intitle:{title}+inauthor:{author}"
        response = requests.get(f"{self.BASE_URL}?q={query}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return self._parse_data(items[0])
        return None

    def _parse_data(self, item) -> dict[str, Any]:
        volume_info = item.get("volumeInfo", {})
        return {
            "title": volume_info.get("title"),
            "authors": volume_info.get("authors", []),
            "isbn": next((id for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"), {}).get("identifier"),
            "description": volume_info.get("description"),
            "cover": volume_info.get("imageLinks", {}).get("thumbnail"),
            "publish_date": volume_info.get("publishedDate"),
            "publisher": volume_info.get("publisher"),
            "page_count": volume_info.get("pageCount")
        }
