import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import re
from typing import Any, TypeGuard
from ..interface.data_source import DataSourceInterface


class GoodreadsScraper(DataSourceInterface):
    BASE_URL: str = "https://www.goodreads.com/book/isbn/"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        Fetch book data from Goodreads by ISBN.

        Args:
            isbn: The ISBN of the book to fetch.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        url: str = f"{self.BASE_URL}{isbn}"
        return self._scrape_data(url)

    def fetch_by_title_author(self, title: str, author: str) -> dict[str, Any] | None:
        """
        Fetch book data from Goodreads by title and author.

        This method is not implemented for Goodreads due to the complexity of search results.

        Args:
            title: The title of the book to fetch.
            author: The author of the book to fetch.

        Returns:
            None
        """
        return None

    def fetch_by_url(self, url: str) -> dict[str, Any] | None:
        """
        Fetch book data from a specific Goodreads URL.

        Args:
            url: The Goodreads book page URL.

        Returns:
            A dictionary containing book information, or None if not found.
        """
        return self._scrape_data(url)

    def _scrape_data(self, url: str) -> dict[str, Any] | None:
        """
        Scrape and parse the data from Goodreads into a standardized format.

        Args:
            url: The URL of the Goodreads book page.

        Returns:
            A dictionary containing parsed book information, or None if scraping fails.
        """
        response: requests.Response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one('[data-testid="bookTitle"]')
        title = title.get_text(strip=True) if title else None

        authors_set: set[str] = set()
        for contributor in soup.select('span[data-testid="name"]'):
            authors_set.add(contributor.get_text(strip=True))
        authors = list(authors_set)

        cover_image = soup.select_one("div.BookCover__image img.ResponsiveImage")
        cover_image = cover_image["src"] if cover_image else None

        description = soup.select_one('[data-testid="description"]')
        description = description.get_text(strip=True) if description else None

        genres_list: Tag | None = soup.select_one('[data-testid="genresList"]')
        genres = (
            genres_list.select("a.Button--tag-inline span.Button__labelItem")
            if genres_list
            else []
        )
        tags: list[str] = [genre.get_text(strip=True) for genre in genres]

        pages_element: Tag | NavigableString | None = soup.find(
            "p", attrs={"data-testid": "pagesFormat"}
        )
        if pages_element:
            pages_text: str = pages_element.get_text(strip=True)
            numbers: list[Any] = re.findall(r"\d+", pages_text)
            number_of_pages: int | None = int(numbers[0]) if numbers else None
        else:
            number_of_pages = None

        isbn: str | None = self._fetch_isbn_from_script(soup)

        return {
            "title": title,
            "authors": authors,
            "cover": cover_image,
            "description": description,
            "tags": tags,
            "page_count": number_of_pages,
            "link": url,
            "isbn": isbn,
        }

    @staticmethod
    def _is_valid_script_content(content: Any) -> TypeGuard[str]:
        return content is not None and isinstance(content.string, str)

    @staticmethod
    def _is_valid_script_tag(tag: Any) -> TypeGuard[Tag]:
        return isinstance(tag, Tag) and hasattr(tag, "string")

    def _fetch_isbn_from_script(self, soup: BeautifulSoup) -> str | None:
        """
        Extract ISBN from the ld+json script tag in the Goodreads page.

        Args:
            soup: BeautifulSoup object of the Goodreads page.

        Returns:
            The ISBN if found, None otherwise.

        Raises:
            ValueError: If the script tag is not found or is of unexpected type.
        """
        script_tag = soup.find("script", type="application/ld+json")

        if not script_tag:
            return None  # Script tag not found, but this isn't necessarily an error

        if not self._is_valid_script_tag(script_tag):
            raise ValueError("Unexpected script tag structure in Goodreads page")

        try:
            json_content = json.loads(script_tag.string)  # type: ignore
            return json_content.get("isbn")
        except json.JSONDecodeError:
            # Log this error if you have logging set up
            return None
        except AttributeError:
            # This should never happen due to the _is_valid_script_tag check, but just in case:
            raise ValueError("Unexpected script tag content in Goodreads page")
