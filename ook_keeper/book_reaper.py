import os
from notion_client import Client

from utils.constants import NOTION_DATABASE_ID


class BookReaper:
    def __init__(self) -> None:
        self.notion = Client(auth=os.environ["NOTION_SECRET"])
        self.database_id: str = NOTION_DATABASE_ID

    def reap_all_books(self) -> list[dict]:
        """Reap all books from the Notion database."""
        results = []
        has_more = True
        next_cursor = None

        while has_more:
            response = self.notion.databases.query(
                database_id=self.database_id, start_cursor=next_cursor
            )
            if isinstance(response, dict) and "results" in response:
                results.extend(response["results"])
                has_more = response["has_more"]
                next_cursor = response["next_cursor"]
            else:
                raise TypeError(
                    f"Unexpected response type from Notion API: {response!r}"
                )

        return [self._parse_page(page) for page in results]

    def reap_specific_book(
        self,
        isbn: str | None = None,
        title: str | None = None,
        author: str | None = None,
    ) -> dict:
        """
        Reap a specific book from the Notion database.
        Either isbn or author and title must be provided.
        """
        if isbn is not None:
            query_filter = self._build_query_filter(isbn)
        elif title and author:
            query_filter = self._build_query_filter(title, author)
        else:
            raise ValueError("Either ISBN or both title and author must be provided")
        response = self.notion.databases.query(
            database_id=self.database_id, filter=query_filter
        )
        if isinstance(response, dict) and "results" in response:
            return self._parse_page(response["results"][0])
        else:
            raise TypeError(f"Unexpected response type from Notion API: {response!r}")
        return {}

    def _build_query_filter(
        self,
        isbn: str | None = None,
        title: str | None = None,
        author: str | None = None,
    ) -> dict:
        """Build a query filter for reaping a specific book."""
        if isbn:
            return {"property": "ISBN", "rich_text": {"equals": isbn}}
        elif title and author:
            return {
                "and": [
                    {"property": "Название", "title": {"equals": title}},
                    {"property": "Авторы", "multi_select": {"contains": author}},
                ]
            }
        else:
            raise ValueError("Either ISBN or both title and author must be provided")

    def _parse_page(self, page: dict) -> dict:
        """Parse a Notion page into a dictionary."""
        properties = page["properties"]
        return {
            "id": page["id"],
            "title": (
                properties["Название"]["title"][0]["text"]["content"]
                if properties["Название"]["title"]
                else ""
            ),
            "authors": [
                author["name"] for author in properties["Авторы"]["multi_select"]
            ],
            "isbn": (
                properties["ISBN"]["rich_text"][0]["text"]["content"]
                if properties["ISBN"]["rich_text"]
                else ""
            ),
            "tags": [tag["name"] for tag in properties["Тэги"]["multi_select"]],
            "description": (
                properties["Кратко"]["rich_text"][0]["text"]["content"]
                if properties["Кратко"]["rich_text"]
                else ""
            ),
            "page_count": properties["Количество страниц"]["number"],
            "publish_year": properties["Год первой публикации"]["number"],
            "cover_url": (
                properties["Cover"]["files"][0]["external"]["url"]
                if properties["Cover"]["files"]
                else ""
            ),
            "link": properties["Link"]["url"],
        }


book_reaper = BookReaper()
