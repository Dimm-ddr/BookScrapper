# agent_notion/mission_control.py

import os
import time
from typing import Any, Awaitable, TypeGuard, List
from notion_client import APIResponseError, Client
import logging
import re
from .field_operative import prepare_book_intel

# Set up package-specific logger
logger: logging.Logger = logging.getLogger("agent_notion")
logger.setLevel(logging.ERROR)

# Create a file handler
error_log_file = "agent_notion_errors.log"
file_handler = logging.FileHandler(error_log_file)
file_handler.setLevel(logging.ERROR)

# Create a formatting configuration
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


class MissionControl:
    """
    Handles interactions with the Notion API for book data upload.
    """

    def __init__(self) -> None:
        """
        Initialize MissionControl with Notion client and database ID.
        """
        self.notion = Client(auth=os.environ["NOTION_SECRET"])
        self.database_id: str = os.environ["DATABASE_ID"]

    def _is_dict_response(self, obj: Any) -> TypeGuard[dict[str, Any]]:
        """
        Type guard to check if an object is a dictionary response from Notion API.

        Args:
            obj (Any): The object to check.

        Returns:
            bool: True if the object is a dictionary with an "id" key, False otherwise.
        """
        return isinstance(obj, dict) and "id" in obj

    def check_book_existence(self, title: str) -> bool:
        """
        Check if a book with the given title already exists in the Notion database.

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
                    "property": "Название",
                    "title": {"equals": title},
                }
                response = self.notion.databases.query(
                    database_id=self.database_id, filter=query_filter
                )

                if self._is_dict_response(response):
                    return len(response.get("results", [])) > 0
                else:
                    raise TypeError("Unexpected response type from Notion API")

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

        else:
            logger.error("Max retries reached. Exiting mission.")
            exit()

        return False

    def upload_book(self, book_data: dict[str, Any]) -> None:
        """
        Upload a single book to Notion.

        Args:
            book_data (Dict[str, Any]): The book data to upload.
        """
        try:
            properties: dict[str, Any] = prepare_book_intel(book_data)

            new_page: Any | Awaitable[Any] = self.notion.pages.create(
                parent={"database_id": self.database_id}, properties=properties
            )

            if self._is_dict_response(new_page):
                self._add_description_to_page(
                    new_page["id"], book_data.get("description", "")
                )
            else:
                raise TypeError(
                    "Unexpected response type from Notion API when creating page"
                )
        except Exception as e:
            logger.error(
                f"Error uploading book {book_data.get('title', 'Unknown')!r}: {str(e)!r}",
                exc_info=True,
            )

    def _add_description_to_page(self, page_id: str, description: str) -> None:
        """
        Add the full description as content to the Notion page,
            split into blocks of 2000 characters or less.

        Args:
            page_id (str): The ID of the Notion page.
            description (str): The full description to add.
        """
        if not description or not page_id:
            return

        blocks: List[dict[str, Any]] = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Полное описание"}}
                    ]
                },
            }
        ]

        # Split description into sentences
        sentences: List[str | Any] = re.split(r"(?<=[.!?])\s+", description)
        current_block = ""

        for sentence in sentences:
            if len(current_block) + len(sentence) > 2000:
                # Add the current block to the blocks list
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": current_block.strip()},
                                }
                            ]
                        },
                    }
                )
                current_block: str | Any = sentence
            else:
                current_block += " " + sentence

        # Add the last block
        if current_block:
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": current_block.strip()}}
                        ]
                    },
                }
            )

        try:
            self.notion.blocks.children.append(page_id, children=blocks)
        except Exception as e:
            logger.error(
                f"Error adding description to page {page_id}: {str(e)}", exc_info=True
            )
