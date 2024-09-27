import os
import sys
import argparse
import logging
from typing import Any

from notion_client import Client
from agent_notion.uploader import upload_books_to_notion
from golden_book_retriever.retriever import Retriever
from ook_keeper.book_updater import BookUpdater
from utils.error_handler import setup_error_handling
from ook_keeper.book_processor import BookProcessor


def setup_logging(debug: bool = True) -> None:
    log_level: int = logging.DEBUG if debug else logging.INFO

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("golden_book_retriever.log", encoding="utf-8"),
        ],
    )

    # Set the log level for all loggers
    for logger_name in logging.root.manager.loggerDict:
        logger: logging.Logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

    # Ensure that the main logger is also set to the correct level
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)


setup_error_handling(
    [
        "golden_book_retriever",
        "agent_notion",
        "main",
    ]
)

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main function to run the Golden Book Retriever.

    This function parses command-line arguments and executes the appropriate actions,
    such as fetching book data or uploading books to Notion.
    """
    parser = argparse.ArgumentParser(description="Golden Book Retriever")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", type=str)
    parser.add_argument("--title", help="Book title for fetching data")
    parser.add_argument("--author", help="Book author(s) for fetching data", nargs="+")
    parser.add_argument("--isbn-file", help="File containing list of ISBNs", type=str)
    parser.add_argument(
        "--goodreads-file", help="File containing list of Goodreads URLs", type=str
    )
    parser.add_argument("--upload", action="store_true", help="Upload books to Notion")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging")
    parser.add_argument(
        "--update-books", help="JSON file containing book updates", type=str
    )

    args: argparse.Namespace = parser.parse_args()

    setup_logging(not args.no_debug)

    try:
        retriever = Retriever()
        processor = BookProcessor(retriever)

        if args.upload:
            logger.info("Uploading books to Notion")
            upload_books_to_notion("data/books")
        elif args.isbn_file:
            logger.info(f"Processing ISBNs from file: {args.isbn_file}")
            processor.process_file(args.isbn_file, processor.process_isbn)
        elif args.goodreads_file:
            logger.info(f"Processing Goodreads URLs from file: {args.goodreads_file}")
            processor.process_file(args.goodreads_file, processor.process_goodreads_url)
        elif args.isbn:
            processor.process_isbn(args.isbn)
        elif args.title and args.author:
            processor.process_title_author(args.title, set(args.author))
        elif args.update_books:
            logger.info(f"Updating books from file: {args.update_books}")
            notion_client = Client(auth=os.environ["NOTION_SECRET"])
            updater = BookUpdater(notion_client)
            updater.update_books_from_file(args.update_books)
        else:
            logger.error("Invalid arguments. Use --help for usage information.")
            sys.exit(1)

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
