import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import argparse
import logging
from typing import Any, LiteralString
from agent_notion.uploader import upload_books_to_notion
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
    parser.add_argument("--input", type=str, help="Input file with ISBNs")
    parser.add_argument("--upload", action="store_true", help="Upload books to Notion")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging")

    args: argparse.Namespace = parser.parse_args()

    if args.no_debug:
        logger.setLevel(logging.INFO)

    if args.upload:
        logger.info("Uploading books to Notion")
        upload_books_to_notion("data/books")
    elif not (args.isbn or (args.title and args.author)):
        logger.error("Either --isbn or both --title and --author must be specified")
        sys.exit(1)
    else:
        try:
            retriever = Retriever()

            if args.isbn:
                logger.debug(f"Fetching data for ISBN: {args.isbn}")
                book_data = retriever.fetch_by_isbn(args.isbn)
                process_book_data(book_data, f"ISBN {args.isbn}")
            elif args.title and args.author:
                logger.debug(
                    f"Fetching data for title: {args.title!r}, author: {args.author!r}"
                )
                book_data: dict[str, Any] | None = retriever.fetch_by_title_author(
                    args.title, args.author
                )
                process_book_data(book_data, f"{args.title!r} by {args.author!r}")

        except Exception as e:
            logger.exception(f"An unexpected error occurred: {str(e)!r}")
            sys.exit(1)


if __name__ == "__main__":
    main()
