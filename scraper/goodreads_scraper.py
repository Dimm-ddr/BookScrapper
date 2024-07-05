from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
import requests
import json

from data.datamodel import BookData


class GoodreadsScraper:
    """
    A class to scrape book data from Goodreads.
    """

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.soup: BeautifulSoup = self._fetch_page()

    def _fetch_page(self) -> BeautifulSoup:
        response: requests.Response = requests.get(self.url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def scrape(self) -> BookData:
        title: str = self.get_title()
        authors: list[str] = self.get_author()
        isbn: str | None = self.get_isbn()
        description: str | None = self.get_description()

        # Ensure the title is always a string
        if not title:
            raise ValueError("The title of the book could not be found.")

        return BookData(
            title=title,
            authors=authors,
            first_publish_year=None,
            languages=[],
            isbn=isbn if isbn else "",
            tags=[],
            link=self.url,
            description=description,
            cover=None,
            page_count=None,
            editions_count=None,
        )

    def get_title(self) -> str:
        element: Tag | None = self.soup.select_one('[data-testid="bookTitle"]')
        return element.get_text(strip=True) if element else ""

    def get_author(self) -> list[str]:
        elements: ResultSet[Tag] = self.soup.select('[data-testid="name"]')
        return [
            element.get_text(strip=True)
            for element in elements
            if "Contributor" in (element.get("class") or [])
        ]

    def get_isbn(self) -> str | None:
        script_tag: Tag | NavigableString | None = self.soup.find(
            "script", type="application/ld+json"
        )
        if isinstance(script_tag, Tag) and script_tag.string:
            json_data = json.loads(script_tag.string)
            return json_data.get("isbn")
        return None

    def get_description(self) -> str | None:
        element: Tag | None = self.soup.select_one('[data-testid="description"]')
        return element.get_text(strip=True) if element else None
