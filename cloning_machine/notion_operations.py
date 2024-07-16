import logging
from typing import Any, Sequence, TypeGuard, cast
from notion_client import Client
from exceptions import NotionResponseTypeError
from .notion_types import (
    NotionPage,
    NotionBlock,
    NotionDatabase,
    NotionListResponse,
    is_notion_block,
    is_notion_page,
    is_notion_list_response,
    is_notion_database,
)
from .config import config

logger: logging.Logger = logging.getLogger(__name__)


class NotionOperations:
    def __init__(self) -> None:
        self.client = Client(auth=config["NOTION_TOKEN"])
        self.property_id_map = {}  # Cache for property ID mapping

    def get_page(self, page_id: str) -> NotionPage:
        """Retrieve a page from Notion."""
        response = self.client.pages.retrieve(page_id)
        if not is_notion_page(response):
            raise NotionResponseTypeError(response)
        return response

    def get_database_schema(self, database_id: str) -> None:
        """Retrieve the database schema and cache property ID mapping."""
        response = self.client.databases.retrieve(database_id)
        if not is_notion_database(response):
            raise NotionResponseTypeError(response)

        database: NotionDatabase = response
        self.property_id_map: dict[str, Any] = {
            name: prop["id"] for name, prop in database["properties"].items()
        }

    def create_page(self, parent_id: str, properties: dict[str, Any]) -> NotionPage:
        """Create a new page in Notion with the given properties."""
        if not self.property_id_map:
            self.get_database_schema(parent_id)

        formatted_properties: dict[str, Any] = self._format_properties(properties)
        logger.debug(f"Formatted properties for new page: {formatted_properties}")

        new_page = self.client.pages.create(
            parent={"database_id": parent_id},
            properties=formatted_properties,
        )

        if not is_notion_page(new_page):
            raise NotionResponseTypeError(new_page)
        return new_page

    def get_blocks(self, page_id: str) -> Sequence[NotionBlock]:
        """Get all blocks (content) of a page."""
        response = self.client.blocks.children.list(page_id)
        if not is_notion_list_response(response):
            raise NotionResponseTypeError(response)

        def is_notion_block_sequence(
            blocks: Sequence[Any],
        ) -> TypeGuard[Sequence[NotionBlock]]:
            return all(isinstance(block, dict) and "type" in block for block in blocks)

        if not is_notion_block_sequence(response["results"]):
            raise NotionResponseTypeError(response["results"])

        return response["results"]

    def append_block(
        self, parent_id: str, block_content: dict[str, Any]
    ) -> NotionBlock:
        """Append a new block to a page or block."""
        response = self.client.blocks.children.append(
            parent_id, children=[block_content]
        )
        if not is_notion_list_response(response) or not response["results"]:
            raise NotionResponseTypeError(response)

        result = response["results"][0]
        if not is_notion_block(result):
            raise NotionResponseTypeError(result)

        return result

    def create_database(
        self, parent_id: str, title: list[dict[str, Any]], properties: dict[str, Any]
    ) -> NotionDatabase:
        """Create a new database in Notion."""
        new_database = self.client.databases.create(
            parent={"page_id": parent_id},
            title=title,
            properties=properties,
        )
        if not is_notion_database(new_database):
            raise NotionResponseTypeError(new_database)
        return new_database

    def query_database(
        self, database_id: str, start_cursor: str | None = None
    ) -> NotionListResponse:
        """Query a Notion database."""
        response = self.client.databases.query(
            database_id=database_id, start_cursor=start_cursor
        )
        if not is_notion_list_response(response):
            raise NotionResponseTypeError(response)
        return cast(NotionListResponse, response)

    def delete_block(self, block_id: str) -> None:
        """Delete a block from Notion."""
        self.client.blocks.delete(block_id)

    def _format_properties(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Format properties for Notion API."""
        formatted_properties = {}
        for key, value in properties.items():
            logger.debug(f"Formatting property: {key}")
            if isinstance(value, dict) and "type" in value:
                # This is already in Notion API format, keep as is
                formatted_properties[key] = value
            else:
                # Assume it's a text property if not specified
                formatted_properties[key] = {
                    "type": "rich_text",
                    "rich_text": [{"type": "text", "text": {"content": str(value)}}],
                }

        return formatted_properties

    def get_database(self, database_id: str) -> NotionDatabase:
        """Retrieve a database from Notion."""
        response = self.client.databases.retrieve(database_id)
        if not is_notion_database(response):
            raise NotionResponseTypeError(response)
        return response
