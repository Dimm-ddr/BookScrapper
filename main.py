import json
import os
from pathlib import Path
import sys
import traceback
from dotenv import load_dotenv
import argparse
import logging
from typing import Any, List, LiteralString
from data.datamodel import BookData
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


def process_isbn(isbn: str, retriever: Retriever) -> None:
    try:
        logger.debug(f"Fetching data for ISBN: {isbn}")
        book_data: dict[str, Any] | None = retriever.fetch_by_isbn(isbn)
        if not book_data:
            logger.warning(f"Data for ISBN {isbn!r} not found")
            return

        title = book_data.get("title")
        if not title:
            logger.warning(f"No title found for ISBN {isbn!r}. Skipping save.")
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

        logger.info(f"Data for ISBN {isbn!r} saved to {output_file}")
    except Exception as e:
        logger.exception(f"Error processing ISBN {isbn!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Golden Book Retriever")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", type=str)
    parser.add_argument("--title", help="Book title for fetching data")
    parser.add_argument("--author", help="Book author for fetching data")
    parser.add_argument("--input", type=str, help="Input file with ISBNs")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging")

    args: argparse.Namespace = parser.parse_args()

    if args.no_debug:
        logger.setLevel(logging.INFO)

    if not (args.isbn or (args.title and args.author)):
        logger.error("Either --isbn or both --title and --author must be specified")
        sys.exit(1)

    try:
        retriever = Retriever()

        if args.isbn:
            process_isbn(args.isbn, retriever)
        elif args.title and args.author:
            try:
                logger.debug(
                    f"Fetching data for title: {args.title!r}, author: {args.author!r}"
                )
                book_data = retriever.fetch_by_title_author(args.title, args.author)
                if book_data:
                    book = BookData(**book_data)
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(book.to_json())
                    logger.info(
                        f"Data for {args.title!r} by {args.author!r} saved to {args.output!r}"
                    )
                else:
                    logger.warning(
                        f"No data found for {args.title!r} by {args.author!r}"
                    )
            except Exception as e:
                logger.exception(
                    f"Error processing title {args.title!r} by author {args.author!r}"
                )

    except Exception as e:
        logger.exception("An unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
