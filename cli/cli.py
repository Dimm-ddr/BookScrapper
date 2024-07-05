import click
from data.datamodel import BookData
from scraper.goodreads_scraper import GoodreadsScraper
from fetcher.data_fetcher import DataFetcher
from agent_notion.uploader import NotionUploader


@click.group()
def cli() -> None:
    pass


@click.command()
@click.argument("isbn_file", type=click.Path(exists=True))
@click.option("--output", default=None, help="Output JSON file for book data")
def fetch_isbn(isbn_file: str, output: str | None) -> None:
    with open(isbn_file, "r") as f:
        isbns: list[str] = f.read().splitlines()
    for isbn in isbns:
        fetcher = DataFetcher(isbn)
        book_data: BookData | None = fetcher.fetch_by_isbn()
        if not book_data:
            click.echo(f"Data for ISBN {isbn} not found")
            continue
        output_filename: str = output or f"{book_data.title.replace(' ', '_')}.json"
        fetcher.save_to_json(book_data, output_filename)
    click.echo(f"Data saved to {output_filename}")


@click.command()
@click.argument("url", type=str)
@click.option("--output", default=None, help="Output JSON file for book data")
def scrape_url(url: str, output: str | None) -> None:
    scraper = GoodreadsScraper(url)
    book_data: BookData = scraper.scrape()
    output_filename: str = output or f"{book_data.title.replace(' ', '_')}.json"
    with open(output_filename, "w") as f:
        f.write(book_data.to_json())
    click.echo(f"Data saved to {output_filename}")


@click.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--notion_secret", envvar="NOTION_SECRET", help="Notion API Secret")
@click.option("--database_id", envvar="DATABASE_ID", help="Notion Database ID")
def upload(json_file: str, notion_secret: str, database_id: str) -> None:
    uploader = NotionUploader(secret=notion_secret, database_id=database_id)
    uploader.upload_from_json(json_file)
    click.echo(f"Data from {json_file} uploaded to Notion")


cli.add_command(fetch_isbn)
cli.add_command(scrape_url)
cli.add_command(upload)

if __name__ == "__main__":
    cli()
