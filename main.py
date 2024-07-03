import argparse
import os
from data.datamodel import BookData
from fetcher.data_fetcher import DataFetcher
from scrapper.goodreads_scrapper import GoodreadsScraper
from uploader.notion_uploader import NotionUploader


def main() -> None:
    parser = argparse.ArgumentParser(description="Queer Books Data Pipeline")
    parser.add_argument("--isbn", help="Fetch book data by ISBN", action="store_true")
    parser.add_argument(
        "--url", help="Scrape book data from Goodreads URL", action="store_true"
    )
    parser.add_argument(
        "--input", type=str, help="Input JSON file with titles and authors"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="Output JSON file for book data",
    )
    parser.add_argument("--upload", help="Upload data to Notion", action="store_true")

    args: argparse.Namespace = parser.parse_args()

    if args.isbn:
        with open(args.input, "r") as f:
            isbns: list[str] = f.read().splitlines()
        for isbn in isbns:
            fetcher = DataFetcher(isbn)
            book_data: BookData | None = fetcher.fetch_by_isbn()
            if not book_data:
                print(f"Data for ISBN {isbn} not found")
                continue
            fetcher.save_to_json(book_data, args.output)

    if args.url:
        scraper = GoodreadsScraper(args.input)
        book_data = scraper.scrape()
        with open(args.output, "w") as f:
            f.write(book_data.to_json())

    if args.upload:
        notion_secret: str | None = os.getenv("NOTION_SECRET")
        database_id: str | None = os.getenv("DATABASE_ID")
        if not notion_secret or not database_id:
            print("Error: NOTION_SECRET and DATABASE_ID environment variables must be set")
            return

        uploader = NotionUploader(secret=notion_secret, database_id=database_id)
        uploader.upload_from_json(args.output)


if __name__ == "__main__":
    main()
