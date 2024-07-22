import click
from typing import Any
from data.datamodel import BookData
from golden_book_retriever.retriever import Retriever
from book_processor import BookProcessor
from agent_notion.uploader import upload_books_to_notion


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Main entry point for the CLI."""
    ctx.ensure_object(dict)


@click.command()
@click.argument("isbn_file", type=click.Path(exists=True))
@click.option("--output", default=None, help="Output JSON file for book data")
@click.pass_context
def fetch_isbn(ctx: click.Context, isbn_file: str, output: str | None = None) -> None:
    """Fetch book data for ISBNs listed in a file."""
    processor: BookProcessor = ctx.obj["processor"]
    processor.process_file(isbn_file, processor.process_isbn)


@click.command()
@click.argument("title", type=str)
@click.argument("author", type=str, nargs=-1)
@click.option("--output", default=None, help="Output JSON file for book data")
@click.pass_context
def fetch_by_title_author(
    ctx: click.Context, title: str, authors: set[str], output: str | None
) -> None:
    """Fetch book data by title and author(s)."""
    processor: BookProcessor = ctx.obj["processor"]
    processor.process_title_author(title, authors)


@click.command()
@click.argument("goodreads_file", type=click.Path(exists=True))
@click.pass_context
def fetch_goodreads(ctx: click.Context, goodreads_file: str) -> None:
    """Fetch book data for Goodreads URLs listed in a file."""
    processor: BookProcessor = ctx.obj["processor"]
    processor.process_file(goodreads_file, processor.process_goodreads_url)


@click.command()
def upload_to_notion() -> None:
    """Upload books to Notion."""
    upload_books_to_notion("data/books")


cli.add_command(fetch_isbn)
cli.add_command(fetch_by_title_author)
cli.add_command(fetch_goodreads)
cli.add_command(upload_to_notion)


def run_cli(retriever: Retriever, processor: BookProcessor) -> None:
    """
    Run the CLI with the given retriever and processor.

    Args:
        retriever: An instance of Retriever.
        processor: An instance of BookProcessor.
    """
    ctx = click.Context(cli)
    ctx.obj = {"retriever": retriever, "processor": processor}
    cli(obj=ctx.obj)
