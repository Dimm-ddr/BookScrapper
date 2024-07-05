import click
import logging
from typing import Any, List
from data.datamodel import BookData
from golden_book_retriever.retriever import Retriever

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@click.group()
def cli() -> None:
    """Main entry point for the CLI."""
    pass


def process_isbn(isbn: str, retriever: Retriever) -> BookData | None:
    """
    Process a single ISBN to fetch book data.

    Args:
        isbn (str): The ISBN to process.
        retriever (Retriever): The Retriever instance to use.

    Returns:
        BookData | None: The fetched book data or None if not found.
    """
    try:
        book_data: dict[str, Any] | None = retriever.fetch_by_isbn(isbn)
        if not book_data:
            logging.warning(f"Data for ISBN {isbn!r} not found")
            return None
        return BookData(**book_data)
    except Exception as e:
        logging.error(f"Error processing ISBN {isbn!r}: {str(e)!r}")
        return None


@click.command()
@click.argument("isbn_file", type=click.Path(exists=True))
@click.option("--output", default=None, help="Output JSON file for book data")
def fetch_isbn(isbn_file: str, output: str | None = None) -> None:
    """
    Fetch book data for ISBNs listed in a file.

    Args:
        isbn_file (str): Path to the file containing ISBNs.
        output (str | None): Path to the output JSON file.
    """
    try:
        with open(isbn_file, "r") as f:
            isbns: List[str] = f.read().splitlines()

        retriever = Retriever()
        for isbn in isbns:
            book_data: BookData | None = process_isbn(isbn, retriever)
            if book_data:
                output_filename: str = (
                    output or f"{book_data.title.replace(' ', '_')}.json"
                )
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(book_data.to_json())
                logging.info(f"Data saved to {output_filename}")
    except Exception as e:
        logging.error(f"Error in fetch_isbn: {str(e)!r}")


@click.command()
@click.argument("title", type=str)
@click.argument("author", type=str)
@click.option("--output", default=None, help="Output JSON file for book data")
def fetch_by_title_author(title: str, author: str, output: str | None) -> None:
    """
    Fetch book data by title and author.

    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        output (str | None): Path to the output JSON file.
    """
    try:
        retriever = Retriever()
        book_data: dict[str, Any] | None = retriever.fetch_by_title_author(
            title, author
        )
        if book_data:
            book = BookData(**book_data)
            output_filename: str = output or f"{book.title.replace(' ', '_')}.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(book.to_json())
            logging.info(f"Data saved to {output_filename!r}")
        else:
            logging.warning(f"No data found for {title!r} by {author!r}")
    except Exception as e:
        logging.error(f"Error in fetch_by_title_author: {str(e)!r}")


cli.add_command(fetch_isbn)
cli.add_command(fetch_by_title_author)

if __name__ == "__main__":
    cli()
