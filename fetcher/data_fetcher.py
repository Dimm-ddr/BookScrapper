import requests
from data.datamodel import BookData


class DataFetcher:
    """
    A class to fetch book data from Open Library and Google Books.
    """

    def __init__(self, isbn: str) -> None:
        self.isbn: str = isbn

    def fetch_by_isbn(self) -> BookData | None:
        ol_data = self._fetch_ol_data(self.isbn)
        gb_data = self._fetch_gb_data(self.isbn)
        return self._combine_data(ol_data, gb_data)

    def _fetch_ol_data(self, isbn: str) -> dict | None:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if f"ISBN:{isbn}" in data:
                return data[f"ISBN:{isbn}"]
        return None

    def _fetch_gb_data(self, isbn: str) -> dict | None:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                return data["items"][0]
        return None

    def _combine_data(self, ol_data: dict | None, gb_data: dict | None) -> BookData | None:
        title = authors = first_publish_year = languages = isbn = tags = link = description = cover = None

        if ol_data:
            title = ol_data.get("title")
            authors = [author["name"] for author in ol_data.get("authors", [])]
            first_publish_year = ol_data.get("publish_date")
            languages = ol_data.get("languages", [])
            isbn = [self.isbn]
            tags = ol_data.get("subjects", [])
            link = ol_data.get("url")
            description = ol_data.get("description")
            cover = ol_data.get("cover", {}).get("large")

        if gb_data:
            gb_title = gb_data.get("volumeInfo", {}).get("title")
            gb_authors = gb_data.get("volumeInfo", {}).get("authors", [])
            gb_first_publish_year = gb_data.get("volumeInfo", {}).get("publishedDate")
            gb_languages = gb_data.get("volumeInfo", {}).get("language")
            gb_tags = gb_data.get("volumeInfo", {}).get("categories", [])
            gb_link = gb_data.get("volumeInfo", {}).get("infoLink")
            gb_description = gb_data.get("volumeInfo", {}).get("description")
            gb_cover = gb_data.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail")

            title = title or gb_title
            authors = authors or gb_authors
            first_publish_year = first_publish_year or gb_first_publish_year
            languages = languages or gb_languages
            tags = tags or gb_tags
            link = link or gb_link
            description = description or gb_description
            cover = cover or gb_cover

        if not title:
            print(f"Error: Could not fetch title for ISBN {self.isbn}. Skipping this book.")
            return None

        return BookData(
            title=title,
            authors=authors or [],
            first_publish_year=first_publish_year,
            languages=[languages] if languages else [],
            isbn=[self.isbn],
            tags=tags or [],
            link=link,
            description=description,
            cover=cover,
        )

    def save_to_json(self, book_data: BookData, output_filename: str) -> None:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(book_data.to_json())
