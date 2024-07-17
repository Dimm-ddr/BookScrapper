# agent_notion/uploader.py

import json
from pathlib import Path
import logging
from .mission_control import MissionControl

logger: logging.Logger = logging.getLogger(__name__)


def upload_books_to_notion(books_dir: str) -> None:
    """
    Upload books from a directory to Notion.

    This function reads JSON files from the specified directory,
    each representing a book, and uploads them to Notion if they
    don't already exist in the database.

    Args:
        books_dir (str): Path to the directory containing book JSON files.
    """
    mission_control = MissionControl()
    books_path = Path(books_dir)

    for book_file in books_path.glob("*.json"):
        with open(book_file, "r", encoding="utf-8") as f:
            book_data = json.load(f)

        asset_title: str = book_data.get("title", "Unknown Asset")
        if not mission_control.check_book_existence(book_data.get("title", "")):
            mission_control.upload_book(book_data)
            logger.info(f"Intelligence on {asset_title} uploaded.")
        else:
            logger.info(
                f"Intelligence on {asset_title} already exists. Mission aborted."
            )
