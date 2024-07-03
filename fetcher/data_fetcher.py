import requests
from data.datamodel import BookData


class DataFetcher:
    """
    A class to fetch book data from OpenLibrary and Google Books.
    """

    def __init__(self, isbn: str) -> None:
        self.isbn: str = isbn

    def fetch_by_isbn(self) -> BookData | None:
        ol_data: dict | None = self._fetch_ol_data()
        gb_data: dict | None = self._fetch_gb_data()
        if not ol_data and not gb_data:
            return None
        return self._combine_data(ol_data, gb_data)

    def _fetch_ol_data(self) -> dict | None:
        url: str = f"https://openlibrary.org/api/books?bibkeys=ISBN:{self.isbn}&format=json&jscmd=data"
        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            data: dict = response.json()
            return data.get(f"ISBN:{self.isbn}")
        return None

    def _fetch_gb_data(self) -> dict | None:
        url: str = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{self.isbn}"
        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            data: dict = response.json()
            if data["totalItems"] > 0:
                return data["items"][0]
        return None

    def _combine_data(self, ol_data: dict | None, gb_data: dict | None) -> BookData:
        title: str | None = None
        authors: list[str] = []
        first_publish_year: int | None = None
        languages: list[str] = []
        isbn: str = self.isbn
        tags: list[str] = []
        link: str | None = None
        description: str | None = None
        cover: str | None = None
        page_count: int | None = None
        editions_count: int | None = None

        if ol_data:
            title = ol_data.get("title")
            authors = [author["name"] for author in ol_data.get("authors", [])]
            first_publish_year_str = ol_data.get("publish_date")
            first_publish_year = (
                int(first_publish_year_str) if first_publish_year_str and first_publish_year_str.isdigit() else None
            )
            languages = [lang.get("key") for lang in ol_data.get("languages", []) if lang.get("key")]
            tags = ol_data.get("subjects", [])
            link = ol_data.get("url")
            description = ol_data.get("description")
            cover = ol_data.get("cover", {}).get("large")
            page_count = ol_data.get("number_of_pages")
            editions_count = ol_data.get("edition_count")

        if gb_data:
            title = title or gb_data.get("volumeInfo", {}).get("title")
            authors = authors or gb_data.get("volumeInfo", {}).get("authors", [])
            first_publish_year_str = first_publish_year_str or gb_data.get("volumeInfo", {}).get("publishedDate")
            first_publish_year = (
                int(first_publish_year_str) if first_publish_year_str and first_publish_year_str.isdigit() else None
            )
            gb_languages = gb_data.get("volumeInfo", {}).get("language")
            if gb_languages and not languages:
                languages = [gb_languages] if isinstance(gb_languages, str) else gb_languages
            tags = tags or gb_data.get("volumeInfo", {}).get("categories", [])
            link = link or gb_data.get("volumeInfo", {}).get("infoLink")
            description = description or gb_data.get("volumeInfo", {}).get("description")
            cover = cover or gb_data.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail")
            page_count = page_count or gb_data.get("volumeInfo", {}).get("pageCount")
            editions_count = editions_count or gb_data.get("volumeInfo", {}).get("editionsCount")

        if not title:
            raise ValueError("Title is missing, cannot process the book without a title")

        return BookData(
            title=title,
            authors=authors,
            first_publish_year=first_publish_year,
            languages=languages,
            isbn=isbn,
            tags=tags,
            link=link,
            description=description,
            cover=cover,
            page_count=page_count,
            editions_count=editions_count,
        )

    def save_to_json(self, book_data: BookData, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(book_data.to_json())
