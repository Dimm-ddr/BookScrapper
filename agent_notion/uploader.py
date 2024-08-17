# agent_notion/uploader.py

import logging
from .mission_control import MissionControl

logger: logging.Logger = logging.getLogger(__name__)


def upload_books_to_notion(books_dir: str) -> None:
    """
    Upload books from a directory to Notion.

    This function orchestrates the process of reading JSON files from the specified directory,
    each representing a book, and uploading them to Notion if they don't already exist in the database.

    Args:
        books_dir (str): Path to the directory containing book JSON files.
    """
    mission_control = MissionControl()

    logger.info(f"Starting to process books from directory: {books_dir}")

    processed_books, uploaded_books = mission_control.process_books_from_directory(
        books_dir
    )

    logger.info(
        f"Book upload mission completed. Processed {processed_books} books,"
        f"uploaded {uploaded_books} books."
    )
