# agent_notion/mission_control.py

import os
import time
from typing import Any, Awaitable, TypeGuard
from notion_client import APIResponseError, Client
import logging
import json
from pathlib import Path

from utils.constants import NOTION_DATABASE_ID
from .field_operative import prepare_book_intel, prepare_description_for_notion

logger: logging.Logger = logging.getLogger(__name__)


class MissionControl:
    def __init__(self) -> None:
        self.notion = Client(auth=os.environ["NOTION_SECRET"])
        self.database_id: str = NOTION_DATABASE_ID

    def _is_dict_response(self, obj: Any) -> TypeGuard[dict[str, Any]]:
        return isinstance(obj, dict) and "id" in obj

    def check_book_existence(self, title: str, isbn: str, authors: list[str]) -> bool:
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                if isbn:
                    query_filter = {"property": "ISBN", "rich_text": {"equals": isbn}}
                elif title and authors:
                    query_filter = {
                        "and": [
                            {"property": "Название", "title": {"equals": title}},
                            {
                                "property": "Авторы",
                                "multi_select": {
                                    "contains": authors[0] if authors else ""
                                },
                            },
                        ]
                    }
                else:
                    logger.warning(
                        "Insufficient data to check book existence. Returning False."
                    )
                    return False

                logger.debug(
                    f"Checking book existence with filter: {json.dumps(query_filter, indent=2)}"
                )

                response = self.notion.databases.query(
                    database_id=self.database_id, filter=query_filter
                )

                if isinstance(response, dict) and "results" in response:
                    exists = len(response["results"]) > 0
                    logger.debug(
                        f"Book existence check result: {'Exists' if exists else 'Does not exist'}"
                    )
                    logger.debug(
                        f"Response from Notion API: {json.dumps(response, indent=2)}"
                    )
                    return exists
                else:
                    raise TypeError(
                        f"Unexpected response type from Notion API: {response!r}"
                    )

            except APIResponseError as e:
                if e.code == "rate_limited":
                    logger.warning(
                        f"Request rate limited. Retrying in 2 seconds... "
                        f"Attempt {retries + 1}/{max_retries}"
                    )
                    time.sleep(2)
                    retries += 1
                else:
                    logger.error(
                        f"An error occurred while checking book existence: {e}",
                        exc_info=True,
                    )
                    break
            except TypeError as e:
                logger.error(
                    f"Unexpected response type while checking book existence: {e}",
                    exc_info=True,
                )
                break

        logger.error("Max retries reached or an error occurred. Exiting mission.")
        return False

    def process_book(self, book_data: dict[str, Any]) -> bool:
        try:
            title: str = book_data.get("title", "")
            isbn: str = book_data.get("isbn", "")
            authors: list[str] = book_data.get("authors", [])

            logger.info(f"Processing book: {title}")

            if not self.check_book_existence(title, isbn, authors):
                self.upload_book(book_data)
                logger.info(f"Book '{title}' successfully processed and uploaded.")
                return True
            else:
                logger.info(
                    f"Book '{title}' already exists in the database. Skipping upload."
                )
                return False

        except Exception as e:
            logger.exception(
                f"Error processing book {book_data.get('title', 'Unknown')!r}: {str(e)!r}"
            )
            return False

    def upload_book(self, book_data: dict[str, Any]) -> None:
        properties: dict[str, Any] = prepare_book_intel(book_data)
        new_page: Any | Awaitable[Any] = self.notion.pages.create(
            parent={"database_id": self.database_id}, properties=properties
        )

        if isinstance(new_page, dict) and "id" in new_page:
            description_blocks = prepare_description_for_notion(
                book_data.get("description", "")
            )
            self.notion.blocks.children.append(
                new_page["id"], children=description_blocks
            )
        else:
            raise TypeError(
                f"Unexpected response type from Notion API when creating page: {type(new_page)}"
            )

    def process_books_from_directory(self, books_dir: str) -> tuple[int, int]:
        books_path = Path(books_dir)
        total_books = len(list(books_path.glob("*.json")))
        processed_books = 0
        uploaded_books = 0

        for book_file in books_path.glob("*.json"):
            processed_books += 1
            logger.info(f"Processing file {processed_books}/{total_books}: {book_file}")
            try:
                with open(book_file, "r", encoding="utf-8") as f:
                    book_data = json.load(f)

                if self.process_book(book_data):
                    uploaded_books += 1

            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from file: {book_file}")
            except Exception as e:
                logger.error(
                    f"Error processing file {book_file}: {str(e)}", exc_info=True
                )

        return processed_books, uploaded_books
