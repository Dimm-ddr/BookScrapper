# agent_notion/uploader.py

import json
from pathlib import Path
import logging
from .mission_control import MissionControl

logger: logging.Logger = logging.getLogger(__name__)


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
        try:
            with open(book_file, "r", encoding="utf-8") as f:
                book_data = json.load(f)

            title: str = book_data.get("title", "Unknown Asset")
            isbn: str = book_data.get("isbn", "")
            authors: list[str] = book_data.get("authors", [])

            if not mission_control.check_book_existence(title, isbn, authors):
                mission_control.upload_book(book_data)
                logger.info(f"Intelligence on '{title}' uploaded.")
            else:
                logger.info(
                    f"Intelligence on '{title}' already exists. Mission aborted."
                )

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {book_file}")
        except Exception as e:
            logger.error(f"Error processing file {book_file}: {str(e)}")

    logger.info("Book upload mission completed.")
