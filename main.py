import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import argparse
import logging
from typing import Any, Callable, LiteralString
from agent_notion.uploader import upload_books_to_notion
from cloning_machine.cloner import NotionCloner
from golden_book_retriever.retriever import Retriever

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set default level to DEBUG
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def process_book_data(book_data: dict[str, Any] | None, search_term: str) -> None:
    """
    Process and save book data to a JSON file.

    Args:
        book_data (dict[str, Any]): The book data to process.
        search_term (str): The search term used to find the book.
    """
    if not book_data:
        logger.warning(f"No data found for {search_term!r}")
        return

    title = book_data.get("title")
    if not title:
        logger.warning(f"No title found for {search_term!r}. Skipping save.")
        return

    # Sanitize the title for use as a filename
    safe_title: LiteralString = "".join(
        c for c in title if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    output_dir = Path("data/books")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file: Path = output_dir / f"{safe_title}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Data for {search_term!r} saved to {output_file}")


def process_file(file_path: str, process_func: Callable, retriever: Retriever) -> None:
    """
    Process a file containing ISBNs or Goodreads URLs.

    Args:
        file_path (str): Path to the file containing ISBNs or URLs.
        process_func (callable): Function to process each line (ISBN or URL).
        retriever (Retriever): Retriever instance to fetch book data.
    """
    error_log = Path("error_log.txt")
    with open(file_path, "r") as file, open(error_log, "a") as log:
        for line in file:
            item: str = line.strip()
            try:
                process_func(item, retriever)
            except Exception as e:
                error_message: str = f"Error processing {item}: {str(e)}\n"
                log.write(error_message)
                logger.error(error_message)


def process_isbn(isbn: str, retriever: Retriever) -> None:
    """
    Process a single ISBN.

    Args:
        isbn (str): The ISBN to process.
        retriever (Retriever): Retriever instance to fetch book data.
    """
    logger.debug(f"Fetching data for ISBN: {isbn}")
    book_data: dict[str, Any] | None = retriever.fetch_by_isbn(isbn)
    process_book_data(book_data, f"ISBN {isbn}")


def process_goodreads_url(url: str, retriever: Retriever) -> None:
    """
    Process a single Goodreads URL.

    Args:
        url (str): The Goodreads URL to process.
        retriever (Retriever): Retriever instance to fetch book data.
    """
    logger.debug(f"Fetching data for Goodreads URL: {url}")
    book_data: dict[str, Any] | None = retriever.fetch_by_goodreads_url(url)
    if book_data:
        process_book_data(book_data, f"Goodreads URL {url}")
    else:
        logger.warning(f"No data found for Goodreads URL: {url}")


def clone_staging() -> None:
    """Clone the live Notion page to a staging area."""
    cloner = NotionCloner()
    try:
        cloner.cleanup_staging()
        new_staging_id: str = cloner.clone_page()
        logger.info(f"Created new staging clone with ID: {new_staging_id}")
    except Exception as e:
        logger.error(f"Error creating staging clone: {str(e)}")
        sys.exit(1)


def main() -> None:
    """
    Main function to run the Golden Book Retriever.

    This function parses command-line arguments and executes the appropriate actions,
    such as fetching book data or uploading books to Notion.
    """
    parser = argparse.ArgumentParser(description="Golden Book Retriever")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", type=str)
    parser.add_argument("--title", help="Book title for fetching data")
    parser.add_argument("--author", help="Book author for fetching data")
    parser.add_argument("--isbn-file", help="File containing list of ISBNs", type=str)
    parser.add_argument(
        "--goodreads-file", help="File containing list of Goodreads URLs", type=str
    )
    parser.add_argument("--upload", action="store_true", help="Upload books to Notion")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging")
    parser.add_argument(
        "--clone-staging",
        action="store_true",
        help="Clone the live Notion page to a staging area",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.no_debug:
        logger.setLevel(logging.INFO)

    try:
        retriever = Retriever()

        match args:
            case argparse.Namespace(upload=True):
                logger.info("Uploading books to Notion")
                upload_books_to_notion("data/books")

            case argparse.Namespace(isbn_file=str(file_path)):
                logger.info(f"Processing ISBNs from file: {file_path}")
                process_file(file_path, process_isbn, retriever)

            case argparse.Namespace(goodreads_file=str(file_path)):
                logger.info(f"Processing Goodreads URLs from file: {file_path}")
                process_file(file_path, process_goodreads_url, retriever)

            case argparse.Namespace(isbn=str(isbn)):
                process_isbn(isbn, retriever)

            case argparse.Namespace(title=str(title), author=str(author)):
                logger.debug(f"Fetching data for title: {title!r}, author: {author!r}")
                book_data: dict[str, Any] | None = retriever.fetch_by_title_author(
                    title, author
                )
                process_book_data(book_data, f"{title!r} by {author!r}")

            case argparse.Namespace(clone_staging=True):
                clone_staging()

            case _:
                logger.error("Invalid arguments. Use --help for usage information.")
                sys.exit(1)

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
