import logging
from typing import Sequence, Any, cast
from notion_client import Client
from .config import config
from .notion_types import (
    BlockContent,
    NotionPage,
    NotionBlock,
    is_notion_database_page,
    is_notion_page,
    is_notion_list_response,
    is_notion_database,
)

logger: logging.Logger = logging.getLogger(__name__)


class NotionCloner:
    def __init__(self) -> None:
        self.client = Client(auth=config["NOTION_TOKEN"])
        self.live_page_id: str = config["LIVE_PAGE_ID"]
        self.staging_parent_id: str = config["STAGING_PARENT_PAGE_ID"]
        self.database_id: str = config["DATABASE_ID"]

    def clone_page(self) -> str:
        """Clone the live page and its main database to the staging area."""
        try:
            live_page: NotionPage = self._get_page(self.live_page_id)
            new_page: NotionPage = self._create_page(live_page)
            logger.info(f"Created new page with ID: {new_page['id']}")

            self._clone_page_content(self.live_page_id, new_page["id"])
            logger.info("Cloned page content")

            self._clone_database(self.database_id, new_page["id"])
            logger.info("Cloned database")

            logger.info(f"Successfully cloned live page to staging: {new_page['id']}")
            return new_page["id"]
        except Exception as e:
            logger.error(f"Error in clone_page: {str(e)}")
            raise

    def _get_page(self, page_id: str) -> NotionPage:
        """Retrieve a page from Notion."""
        response = self.client.pages.retrieve(page_id)
        if not is_notion_page(response):
            raise ValueError("Invalid response from Notion API")
        return response

    def _create_page(
        self, source_page: NotionPage, parent_id: str | None = None
    ) -> NotionPage:
        """Create a new page based on the source page."""
        new_page = self.client.pages.create(
            parent={"page_id": parent_id or self.staging_parent_id},
            properties=source_page["properties"],
        )
        if not is_notion_page(new_page):
            raise ValueError("Invalid response from Notion API")
        return new_page

    def _clone_page_content(self, source_id: str, target_id: str) -> None:
        """Clone the content from the source page to the target page."""
        blocks: Sequence[NotionBlock] = self._get_blocks(source_id)
        for block in blocks:
            self._clone_block(block, target_id)

    def _get_blocks(self, page_id: str) -> Sequence[NotionBlock]:
        """Get all blocks from a page."""
        response = self.client.blocks.children.list(page_id)
        if not is_notion_list_response(response):
            raise ValueError("Invalid response from Notion API")

        blocks: list[NotionBlock] = []
        for item in response["results"]:
            if "type" in item and "has_children" in item:
                blocks.append(cast(NotionBlock, item))
            else:
                logger.warning(f"Skipping non-block item in response: {item}")

        return blocks

    def _clone_block(self, block: NotionBlock, target_id: str) -> None:
        """Clone a single block to the target page."""
        block_type: str = block["type"]
        block_content = block.get(block_type)

        if block_type == "child_database":
            self._clone_child_database(cast(BlockContent, block_content), target_id)
        else:
            # Prepare the new block content
            new_block_content: dict[str, Any] = {
                "type": block_type,
                block_type: block_content,
            }

            try:
                new_block_response = self.client.blocks.children.append(
                    target_id, children=[new_block_content]
                )
                if not is_notion_list_response(new_block_response):
                    raise ValueError("Invalid response from Notion API")
                new_block = new_block_response["results"][0]

                if block.get("has_children"):
                    self._clone_block_children(block["id"], new_block["id"])
            except Exception as e:
                logger.error(f"Error cloning block of type {block_type}: {str(e)}")
                logger.debug(f"Block content: {new_block_content}")
                raise

    def _clone_child_database(
        self, database_content: BlockContent, target_id: str
    ) -> None:
        """Clone a child database."""
        try:
            new_database = self.client.databases.create(
                parent={"type": "page_id", "page_id": target_id},
                title=database_content.get(
                    "title", [{"text": {"content": "Untitled"}}]
                ),
                properties=database_content.get("properties", {}),
            )
            if not is_notion_database(new_database):
                raise ValueError(
                    "Invalid response from Notion API when creating database"
                )

            # If the original database had an ID, clone its contents
            if "id" in database_content:
                self._clone_database_contents(
                    database_content["id"], new_database["id"]
                )
        except Exception as e:
            logger.error(f"Error cloning child database: {str(e)}")
            logger.debug(f"Database content: {database_content}")
            raise

    def _clone_block_children(self, source_block_id: str, target_block_id: str) -> None:
        """Clone children of a block."""
        children: Sequence[NotionBlock] = self._get_blocks(source_block_id)
        for child in children:
            self._clone_block(child, target_block_id)

    def _clone_database(self, source_db_id: str, target_page_id: str) -> None:
        """Clone the specified database to the target page."""
        source_db = self.client.databases.retrieve(source_db_id)
        if not is_notion_database(source_db):
            raise ValueError("Invalid response from Notion API")
        new_db = self.client.databases.create(
            parent={"page_id": target_page_id},
            title=source_db["title"],
            properties=source_db["properties"],
        )
        if not is_notion_database(new_db):
            raise ValueError("Invalid response from Notion API")
        self._clone_database_contents(source_db_id, new_db["id"])
        logger.info(f"Cloned database {source_db_id} to {new_db['id']}")

    def _clone_database_contents(self, source_db_id: str, target_db_id: str) -> None:
        """Clone the contents of the source database to the target database."""
        start_cursor: str | None = None
        while True:
            response = self.client.databases.query(
                database_id=source_db_id, start_cursor=start_cursor
            )
            if not is_notion_list_response(response):
                raise ValueError("Invalid response from Notion API")

            for page in response["results"]:
                if not is_notion_database_page(page):
                    raise ValueError("Invalid page structure in database response")
                new_page = self.client.pages.create(
                    parent={"database_id": target_db_id}, properties=page["properties"]
                )
                if not is_notion_page(new_page):
                    raise ValueError("Invalid response from Notion API")
                self._clone_page_content(page["id"], new_page["id"])

            if not response["has_more"]:
                break

            start_cursor = response.get("next_cursor")
            if start_cursor is None:
                logger.warning(
                    "Expected next_cursor but received None. Stopping pagination."
                )
                break

    def cleanup_staging(self) -> None:
        """Remove all existing pages in the staging area."""
        try:
            staging_pages: Sequence[NotionBlock] = self._get_blocks(
                self.staging_parent_id
            )
            for page in staging_pages:
                self.client.blocks.delete(page["id"])
            logger.info("Cleaned up existing staging clones")
        except Exception as e:
            logger.error(f"Error cleaning up staging area: {str(e)}")
            raise
