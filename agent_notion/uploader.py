# agent_notion/uploader.py

import os
import json
from pathlib import Path
import time
from typing import Any, TypeGuard
from notion_client import APIResponseError, Client
import logging

from agent_notion.normalizer import normalize_multiselect, prettify_title

logger = logging.getLogger(__name__)


class NotionUploader:
    """
    A class to handle uploading book data to Notion.
    """

    def __init__(self) -> None:
        """
        Initialize the NotionUploader with Notion client and database ID.
        """
        self.notion = Client(auth=os.environ["NOTION_SECRET"])
        self.database_id: str = os.environ["DATABASE_ID"]

    def upload_books(self, books_dir: str) -> None:
        """
        Upload books from a directory to Notion.

        Args:
            books_dir (str): Path to the directory containing book JSON files.
        """
        books_path = Path(books_dir)
        for book_file in books_path.glob("*.json"):
            with open(book_file, "r", encoding="utf-8") as f:
                book_data = json.load(f)

            if not self._book_exists(book_data["title"]):
                self._upload_book(book_data)
                logger.info(f"Uploaded book: {book_data['title']}")
            else:
                logger.info(f"Book already exists, skipping: {book_data['title']}")

    def _is_dict(self, obj: Any) -> TypeGuard[dict[str, Any]]:
        """
        Type guard to check if an object is a dictionary.

        Args:
            obj (Any): The object to check.

        Returns:
            bool: True if the object is a dictionary, False otherwise.
        """
        return isinstance(obj, dict)

    def _book_exists(self, title: str) -> bool:
        """
        Check if a book with the given title already exists in the Notion database.
        Implements retry logic for rate limit (HTTP 429) responses.

        Args:
            title (str): The title of the book to check.

        Returns:
            bool: True if the book exists, False otherwise.
        """
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                query_filter: dict[str, Any] = {
                    "property": "Title",
                    "title": {"equals": title},
                }
                response = self.notion.databases.query(
                    database_id=self.database_id, filter=query_filter
                )

                if self._is_dict(response):
                    return len(response.get("results", [])) > 0
                else:
                    # Handle the case where response is not a dict (e.g., it's a coroutine)
                    raise TypeError("Unexpected response type from Notion API")

            except APIResponseError as e:
                if e.code == "rate_limited":
                    print(
                        f"Request rate limited. Retrying in 2 seconds... "
                        f"Attempt {retries + 1}/{max_retries}"
                    )
                    time.sleep(2)
                    retries += 1
                else:
                    print(f"An error occurred: {e}")
                    break
            except TypeError as e:
                print(f"Unexpected response type: {e}")
                break

        else:
            print("Max retries reached. Exiting script.")
            exit()  # or handle it in a way that fits your script's flow

        return False

    def _upload_book(self, book_data: dict[str, Any]) -> None:
        """
        Upload a single book to Notion.

        Args:
            book_data (dict[str, Any]): The book data to upload.
        """
        properties: dict[str, Any] = self._prepare_properties(book_data)
        self.notion.pages.create(
            parent={"database_id": self.database_id}, properties=properties
        )

    def _prepare_properties(self, book_data: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare book properties for Notion upload.

        Args:
            book_data (dict[str, Any]): The book data to prepare.

        Returns:
            dict[str, Any]: Prepared properties for Notion upload.
        """
        return {
            "Title": {
                "title": [{"text": {"content": prettify_title(book_data["title"])}}]
            },
            "Authors": {
                "multi_select": [
                    {"name": author}
                    for author in normalize_multiselect(book_data["authors"])
                ]
            },
            "ISBN": {"rich_text": [{"text": {"content": book_data["isbn"]}}]},
            "First publish year": {"number": book_data["first_publish_year"]},
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": (
                                book_data["description"][:2000]
                                if book_data["description"]
                                else ""
                            )
                        }
                    }
                ]
            },
            "Page count": {"number": book_data["page_count"]},
            "Languages": {
                "multi_select": [
                    {"name": lang}
                    for lang in normalize_multiselect(book_data["languages"])
                ]
            },
            "Tags": {
                "multi_select": [
                    {"name": tag}
                    for tag in normalize_multiselect(book_data["tags"][:100])
                ]
            },  # Notion has a limit of 100 multi-select options
            "Cover": {
                "type": "files",
                "files": [
                    {
                        "name": "Cover Image",
                        "type": "external",
                        "external": {"url": book_data["cover"]},
                    }
                ],
            },
            "Link": {"url": book_data["link"]},
        }


def upload_books_to_notion(books_dir: str) -> None:
    """
    Upload books from a directory to Notion.

    Args:
        books_dir (str): Path to the directory containing book JSON files.
    """
    uploader = NotionUploader()
    uploader.upload_books(books_dir)
