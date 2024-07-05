"""
Main module for the Queer Books Data Pipeline.

This module provides the main functionality for fetching book data by ISBN,
scraping data from Goodreads URLs, and uploading data to Notion.
"""

import argparse
import os
import logging
from typing import List
from data.datamodel import BookData
from golden_book_retriever.fetcher import DataFetcher
from golden_book_retriever.sources.goodreads_scraper import GoodreadsScraper
from agent_notion.uploader import NotionUploader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_isbn(isbn: str, output: str) -> None:
    """
    Process a single ISBN to fetch and save book data.

    Args:
        isbn (str): The ISBN to process.
        output (str): Path to the output JSON file.
    """
    fetcher = DataFetcher(isbn)
    book_data: BookData | None = fetcher.fetch_by_isbn()
    if not book_data:
        logging.warning(f"Data for ISBN {isbn} not found")
        return
    fetcher.save_to_json(book_data, output)
    logging.info(f"Data for ISBN {isbn} saved to {output}")


def process_url(url: str, output: str) -> None:
    """
    Process a Goodreads URL to scrape and save book data.

    Args:
        url (str): The Goodreads URL to scrape.
        output (str): Path to the output JSON file.
    """
    scraper = GoodreadsScraper(url)
    book_data: BookData = scraper.scrape()
    if book_data:
        with open(output, "w", encoding="utf-8") as f:
            f.write(book_data.to_json())
        logging.info(f"Data from {url} saved to {output}")
    else:
        logging.warning(f"Failed to scrape data from {url}")


def upload_to_notion(output: str) -> None:
    """
    Upload book data from a JSON file to Notion.

    Args:
        output (str): Path to the JSON file containing book data.
    """
    notion_secret: str | None = os.getenv("NOTION_SECRET")
    database_id: str | None = os.getenv("DATABASE_ID")
    if not notion_secret or not database_id:
        logging.error("NOTION_SECRET and DATABASE_ID environment variables must be set")
        return

    uploader = NotionUploader(secret=notion_secret, database_id=database_id)
    uploader.upload_from_json(output)
    logging.info(f"Data from {output} uploaded to Notion")


def main() -> None:
    """
    Main function to run the Queer Books Data Pipeline.

    Parses command-line arguments and executes the appropriate actions.
    """
    parser = argparse.ArgumentParser(description="Queer Books Data Pipeline")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", action="store_true")
    parser.add_argument(
        "--url", help="Scrape book data from Goodreads URL", action="store_true"
    )
    parser.add_argument(
        "--input", type=str, help="Input file with ISBNs or Goodreads URL"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="Output JSON file for book data",
    )
    parser.add_argument("--upload", help="Upload data to Notion", action="store_true")

    args: argparse.Namespace = parser.parse_args()

    if not (args.isbn or args.url):
        logging.error("Either --isbn or --url must be specified")
        return

    if not args.input:
        logging.error("--input must be specified")
        return

    try:
        if args.isbn:
            with open(args.input, "r") as f:
                isbns: List[str] = f.read().splitlines()
            for isbn in isbns:
                process_isbn(isbn, args.output)

        elif args.url:
            with open(args.input, "r") as f:
                url = f.read().strip()
            process_url(url, args.output)

        if args.upload:
            upload_to_notion(args.output)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
