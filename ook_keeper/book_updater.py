# ook_keeper/book_updater.py

import json
import logging
from typing import Any
from notion_client import Client
from notion_client.errors import APIResponseError
from utils.constants import NOTION_DATABASE_ID
from agent_notion.notion_utils import prepare_multiselect_field, prepare_select_field
from agent_notion.text_utils import sanitize_field_value

logger: logging.Logger = logging.getLogger(__name__)


class BookUpdater:
    def __init__(self, notion_client: Client) -> None:
        self.notion = notion_client
        self.database_id = NOTION_DATABASE_ID

    def update_books_from_file(self, file_path: str) -> None:
        updates = self._read_update_file(file_path)
        for update in updates:
            self._process_update(update)

    def _read_update_file(self, file_path: str) -> list[dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as jsonfile:
                return json.load(jsonfile)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in file: {file_path}")
            raise
        except IOError:
            logger.error(f"Error reading file: {file_path}")
            raise

    def _process_update(self, update: dict[str, Any]):
        try:
            book_page = self._find_book(update)
            if book_page:
                self._update_book(book_page, update)
            else:
                logger.warning(
                    f"Book not found: {update.get('isbn') or update.get('title')}"
                )
        except Exception as e:
            logger.error(f"Error processing update: {e}")

    def _find_book(self, update: dict[str, Any]) -> dict[str, Any] | None:
        if "isbn" in update:
            query_filter = {"property": "ISBN", "rich_text": {"equals": update["isbn"]}}
        elif "title" in update and "author" in update:
            query_filter = {
                "and": [
                    {"property": "Название", "title": {"equals": update["title"]}},
                    {
                        "property": "Авторы",
                        "multi_select": {"contains": update["author"]},
                    },
                ]
            }
        else:
            raise ValueError("Update must contain either ISBN or both Title and Author")

        try:
            response = self.notion.databases.query(
                database_id=self.database_id, filter=query_filter
            )
            return response["results"][0] if response["results"] else None
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            raise

    def _update_book(self, book_page: dict[str, Any], update: dict[str, Any]):
        properties_to_update = {}
        non_updatable_fields = {
            "isbn",
            "title",
            "author",
            "authors",
            "Название",
            "Авторы",
            "ISBN",
        }

        for key, value in update.items():
            if key not in non_updatable_fields:
                if key == "tags":
                    properties_to_update.update(
                        prepare_multiselect_field("Тэги", value.split(","))
                    )
                elif key == "page_count":
                    properties_to_update["Количество страниц"] = {"number": int(value)}
                else:
                    properties_to_update[key] = {
                        "rich_text": [
                            {"text": {"content": sanitize_field_value(str(value))}}
                        ]
                    }

        if properties_to_update:
            try:
                self.notion.pages.update(
                    page_id=book_page["id"], properties=properties_to_update
                )
                logger.info(
                    f"Updated book: {book_page['properties']['Название']['title'][0]['text']['content']}"
                )
            except APIResponseError as e:
                logger.error(f"Error updating book: {e}")
        else:
            logger.warning(
                f"No valid fields to update for book: {book_page['properties']['Название']['title'][0]['text']['content']}"
            )
