"""
Command-line interface for the Queer Books Data Pipeline.

This module provides a CLI for fetching book data by ISBN,
scraping data from Goodreads URLs, and uploading data to Notion.
"""

import click
import logging
from typing import List
from data.datamodel import BookData
from golden_book_retriever.sources.goodreads_scraper import GoodreadsScraper
from golden_book_retriever.fetcher import DataFetcher
from agent_notion.uploader import NotionUploader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@click.group()
def cli() -> None:
    """Main entry point for the CLI."""
    pass


def process_isbn(isbn: str, fetcher: DataFetcher) -> BookData | None:
    """
    Process a single ISBN to fetch book data.

    Args:
        isbn (str): The ISBN to process.
        fetcher (DataFetcher): The DataFetcher instance to use.

    Returns:
        BookData | None: The fetched book data or None if not found.
    """
    try:
        book_data: BookData | None = fetcher.fetch_by_isbn()
        if not book_data:
            logging.warning(f"Data for ISBN {isbn} not found")
        return book_data
    except Exception as e:
        logging.error(f"Error processing ISBN {isbn}: {str(e)}")
        return None


@click.command()
@click.argument("isbn_file", type=click.Path(exists=True))
@click.option("--output", default=None, help="Output JSON file for book data")
def fetch_isbn(isbn_file: str, output: str | None) -> None:
    """
    Fetch book data for ISBNs listed in a file.

    Args:
        isbn_file (str): Path to the file containing ISBNs.
        output (str | None): Path to the output JSON file.
    """
    try:
        with open(isbn_file, "r") as f:
            isbns: List[str] = f.read().splitlines()

        for isbn in isbns:
            fetcher = DataFetcher(isbn)
            book_data: BookData | None = process_isbn(isbn, fetcher)
            if book_data:
                output_filename: str = (
                    output or f"{book_data.title.replace(' ', '_')}.json"
                )
                fetcher.save_to_json(book_data, output_filename)
                logging.info(f"Data saved to {output_filename}")
    except Exception as e:
        logging.error(f"Error in fetch_isbn: {str(e)}")


@click.command()
@click.argument("url", type=str)
@click.option("--output", default=None, help="Output JSON file for book data")
def scrape_url(url: str, output: str | None) -> None:
    """
    Scrape book data from a Goodreads URL.

    Args:
        url (str): The Goodreads URL to scrape.
        output (str | None): Path to the output JSON file.
    """
    try:
        scraper = GoodreadsScraper(url)
        book_data: BookData = scraper.scrape()
        if book_data:
            output_filename: str = output or f"{book_data.title.replace(' ', '_')}.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(book_data.to_json())
            logging.info(f"Data saved to {output_filename}")
        else:
            logging.warning(f"Failed to scrape data from {url}")
    except Exception as e:
        logging.error(f"Error in scrape_url: {str(e)}")


@click.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--notion_secret", envvar="NOTION_SECRET", help="Notion API Secret")
@click.option("--database_id", envvar="DATABASE_ID", help="Notion Database ID")
def upload(json_file: str, notion_secret: str, database_id: str) -> None:
    """
    Upload book data from a JSON file to Notion.

    Args:
        json_file (str): Path to the JSON file containing book data.
        notion_secret (str): Notion API secret.
        database_id (str): Notion database ID.
    """
    try:
        uploader = NotionUploader(secret=notion_secret, database_id=database_id)
        uploader.upload_from_json(json_file)
        logging.info(f"Data from {json_file} uploaded to Notion")
    except Exception as e:
        logging.error(f"Error in upload: {str(e)}")


cli.add_command(fetch_isbn)
cli.add_command(scrape_url)
cli.add_command(upload)

if __name__ == "__main__":
    cli()
