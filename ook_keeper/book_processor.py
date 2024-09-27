import hashlib
import json
import logging
import re
import traceback
from pathlib import Path
from typing import Any, Callable

from golden_book_retriever.retriever import Retriever

logger: logging.Logger = logging.getLogger(__name__)


class SetEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle sets."""

    def default(self, obj: Any) -> Any:
        """Convert set to list for JSON serialization."""
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class BookProcessor:
    """Handles processing and saving of book data."""

    def __init__(self, retriever: Retriever) -> None:
        """
        Initialize BookProcessor with a retriever.

        Args:
            retriever: An instance of a book data retriever.
        """
        self.retriever: Retriever = retriever

    def generate_filename(self, title: str, authors: set[str]) -> str:
        # Sanitize the title
        safe_title: str = re.sub(r"[^\w\-_\. ]", "_", title)
        safe_title = safe_title.replace(" ", "_")

        # Get the first author's full name, or "Unknown" if no authors
        sorted_authors: list[str] = sorted(authors) if authors else ["Unknown"]
        first_author: str = sorted_authors[0]

        # Sanitize the author name
        safe_author: str = re.sub(r"[^\w\-_\. ]", "_", first_author)
        safe_author = safe_author.replace(" ", "_")

        # Create a base filename
        base_filename: str = f"{safe_title}_by_{safe_author}"

        # If the base_filename is too long, truncate it
        if len(base_filename) > 50:
            base_filename = base_filename[:50]

        # Create a hash of the full title and all authors
        full_hash: str = hashlib.md5(f"{title}{'|'.join(authors)}".encode()).hexdigest()

        # Use the first 8 characters of the hash to ensure uniqueness
        unique_filename: str = f"{base_filename}_{full_hash[:8]}"

        return unique_filename

    def process_book_data(
        self, book_data: dict[str, Any] | None, search_term: str
    ) -> None:
        if not book_data:
            logger.warning(f"No data found for {search_term!r}")
            return

        title = book_data.get("title")
        authors: set[str] = book_data.get("authors", set())

        if not title:
            logger.warning(f"No title found for {search_term!r}. Raw data: {book_data}")
            return

        filename: str = self.generate_filename(title, authors)
        output_dir = Path("data/books")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file: Path = output_dir / f"{filename}.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2, cls=SetEncoder)
            logger.info(f"Data for {search_term!r} saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving data for {search_term!r}: {str(e)}")
            logger.debug(f"Problematic data: {book_data}")

    def process_isbn(self, isbn: str) -> None:
        """
        Process a single ISBN.

        Args:
            isbn: The ISBN to process.
        """
        logger.debug(f"Fetching data for ISBN: {isbn}")
        book_data: dict[str, Any] | None = self.retriever.fetch_by_isbn(isbn)
        self.process_book_data(book_data, f"ISBN {isbn}")

    def process_goodreads_url(self, url: str) -> None:
        """
        Process a single Goodreads URL.

        Args:
            url: The Goodreads URL to process.
        """
        logger.debug(f"Fetching data for Goodreads URL: {url}")
        book_data: dict[str, Any] | None = self.retriever.fetch_by_goodreads_url(url)
        if book_data:
            self.process_book_data(book_data, f"Goodreads URL {url}")
        else:
            logger.warning(f"No data found for Goodreads URL: {url}")

        # Ensure Goodreads cache is cleared after processing each book
        self.retriever.goodreads_cache = None

    def process_title_author(self, title: str, authors: set[str]) -> None:
        """
        Process a book by title and author(s).

        Args:
            title: The book title.
            authors: A tuple of author names.
        """
        authors_str: str = ", ".join(authors)
        logger.debug(f"Fetching data for title: {title!r}, author(s): {authors_str!r}")
        book_data: dict[str, Any] | None = self.retriever.fetch_by_title_author(
            title, authors
        )
        self.process_book_data(book_data, f"{title!r} by {authors_str!r}")

    def process_file(self, file_path: str, process_func: Callable[[str], None]) -> None:
        """
        Process a file containing ISBNs or Goodreads URLs.

        Args:
            file_path: Path to the file to process.
            process_func: Function to process each line of the file.
        """
        error_log = Path("error_log.txt")
        with open(file_path, "r") as file, open(error_log, "a") as log:
            for line_number, line in enumerate(file, 1):
                item: str = line.strip()
                try:
                    process_func(item)
                except Exception as e:
                    self._log_error(e, line_number, item, log)

        logger.info(f"Finished processing file: {file_path}")

        # Ensure Goodreads cache is cleared after processing each book
        self.retriever.goodreads_cache = None

    def _log_error(
        self, e: Exception, line_number: int, item: str, log_file: Any
    ) -> None:
        """
        Log an error that occurred during file processing.

        Args:
            e: The exception that occurred.
            line_number: The line number where the error occurred.
            item: The item being processed when the error occurred.
            log_file: The file to write the error log to.
        """
        tb: str = traceback.format_exc()
        error_message: str = (
            f"Error processing item at line {line_number}: {item}\n"
            f"Error type: {type(e).__name__}\n"
            f"Error message: {str(e)}\n"
            f"Traceback:\n{tb}\n"
            f"{'-'*60}\n"
        )
        log_file.write(error_message)
        logger.error(
            f"Error processing item at line {line_number}: {item}. Error: {str(e)}"
        )
        logger.debug(f"Detailed error for item at line {line_number}:\n{error_message}")
