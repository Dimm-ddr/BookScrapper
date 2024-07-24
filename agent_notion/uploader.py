# agent_notion/uploader.py

from datetime import datetime
import json
from pathlib import Path
import logging
from typing import Literal
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
    Upload books from a directory to Notion and log the uploaded books.

    This function reads JSON files from the specified directory,
    each representing a book, and uploads them to Notion if they
    don't already exist in the database. It also logs the uploaded books.

    Args:
        books_dir (str): Path to the directory containing book JSON files.
    """
    mission_control = MissionControl()
    books_path = Path(books_dir)
    uploaded_books = []

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
                uploaded_books.append((title, authors))
            else:
                logger.info(
                    f"Intelligence on '{title}' already exists. Mission aborted."
                )

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {book_file}")
        except Exception as e:
            logger.error(f"Error processing file {book_file}: {str(e)}")

    logger.info("Book upload mission completed.")

    # Log uploaded books
    if uploaded_books:
        log_uploaded_books(uploaded_books)


def log_uploaded_books(uploaded_books: list[tuple[str, list[str]]]) -> None:
    """
    Log the uploaded books to a file.

    Args:
        uploaded_books (list[tuple[str, list[str]]]): List of tuples containing book title and authors.
    """
    today: str = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("data/logs/upload")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"uploaded_books_{today}.txt"

    mode: Literal['a'] | Literal['w'] = "a" if log_file.exists() else "w"

    with open(log_file, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(f"Books uploaded on {today}:\n\n")
        else:
            f.write("\n")  # Add a newline for separation if appending

        for title, authors in uploaded_books:
            authors_str: str = ", ".join(authors) if authors else "Unknown Author"
            f.write(f"Title: {title}\n")
            f.write(f"Author(s): {authors_str}\n")
            f.write("-" * 50 + "\n")

    logger.info(f"Uploaded books logged to {log_file}")
