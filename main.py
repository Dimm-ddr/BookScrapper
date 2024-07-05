import argparse
import logging
from typing import List
from data.datamodel import BookData
from golden_book_retriever.retriever import Retriever

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_isbn(isbn: str, retriever: Retriever, output: str) -> None:
    """
    Process a single ISBN to fetch and save book data.

    Args:
        isbn (str): The ISBN to process.
        retriever (Retriever): The Retriever instance to use.
        output (str): Path to the output JSON file.
    """
    book_data = retriever.fetch_by_isbn(isbn)
    if not book_data:
        logging.warning(f"Data for ISBN {isbn!r} not found")
        return
    book = BookData(**book_data)
    with open(output, "w", encoding="utf-8") as f:
        f.write(book.to_json())
    logging.info(f"Data for ISBN {isbn!r} saved to {output!r}")


def process_title_author(
    title: str, author: str, retriever: Retriever, output: str
) -> None:
    """
    Process a title and author to fetch and save book data.

    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        retriever (Retriever): The Retriever instance to use.
        output (str): Path to the output JSON file.
    """
    book_data = retriever.fetch_by_title_author(title, author)
    if book_data:
        book = BookData(**book_data)
        with open(output, "w", encoding="utf-8") as f:
            f.write(book.to_json())
        logging.info(f"Data for {title!r} by {author!r} saved to {output!r}")
    else:
        logging.warning(f"No data found for {title!r} by {author!r}")


def main() -> None:
    """
    Main function to run the Golden Book Retriever.

    Parses command-line arguments and executes the appropriate actions.
    """
    parser = argparse.ArgumentParser(description="Golden Book Retriever")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", action="store_true")
    parser.add_argument("--title", help="Book title for fetching data")
    parser.add_argument("--author", help="Book author for fetching data")
    parser.add_argument("--input", type=str, help="Input file with ISBNs")
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="Output JSON file for book data",
    )

    args: argparse.Namespace = parser.parse_args()

    if not (args.isbn or (args.title and args.author)):
        logging.error("Either --isbn or both --title and --author must be specified")
        return

    retriever = Retriever()

    try:
        if args.isbn:
            if args.input:
                with open(args.input, "r") as f:
                    isbns: List[str] = f.read().splitlines()
                for isbn in isbns:
                    process_isbn(isbn, retriever, args.output)
            else:
                logging.error("--input must be specified when using --isbn")
        elif args.title and args.author:
            process_title_author(args.title, args.author, retriever, args.output)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)!r}")


if __name__ == "__main__":
    main()
