# cloner.py
import logging
from typing import Sequence, Any

from cloning_machine.notion_types import NotionDatabase, NotionPage
from exceptions import NotionOperationError
from .notion_types import (
    BlockContent,
    NotionBlock,
    NotionListResponse,
    is_notion_block,
    is_notion_database_page,
)
from .notion_constants import NotionBlockType
from .transformers import transform_block_content, transform_database_properties
from .notion_operations import NotionOperations
from .config import config

logger: logging.Logger = logging.getLogger(__name__)


class NotionCloner:
    def __init__(self) -> None:
        self.notion_ops = NotionOperations()
        self.live_page_id: str = config["LIVE_PAGE_ID"]
        self.staging_parent_id: str = config["STAGING_PARENT_PAGE_ID"]
        self.database_id: str = config["DATABASE_ID"]

    def clone_page(self) -> str:
        try:
            # First, clean the target page
            self._clean_target_page()

            live_page: NotionPage = self.notion_ops.get_page(self.live_page_id)
            new_page: NotionPage = self.notion_ops.create_page(
                self.staging_parent_id, live_page["properties"]
            )
            logger.info(f"Created new page with ID: {new_page['id']}")

            self._clone_page_content(self.live_page_id, new_page["id"])
            logger.info("Cloned page content")

            self._clone_database_contents(self.database_id, new_page["id"])
            logger.info("Cloned database")

            logger.info(f"Successfully cloned live page to staging: {new_page['id']}")
            return new_page["id"]
        except Exception as e:
            logger.error(f"Error in clone_page: {str(e)}")
            raise NotionOperationError(f"Failed to clone page: {str(e)}") from e

    def _clean_target_page(self) -> None:
        try:
            # Get all blocks (subpages and content) in the staging parent page
            blocks: Sequence[NotionBlock] = self.notion_ops.get_blocks(
                self.staging_parent_id
            )

            # Delete each block
            for block in blocks:
                self.notion_ops.delete_block(block["id"])
                logger.info(f"Deleted block with ID: {block['id']}")

            logger.info("Cleaned up existing content in the staging area")
        except Exception as e:
            logger.error(f"Error cleaning target page: {str(e)}")
            raise NotionOperationError(f"Failed to clean target page: {str(e)}") from e

    def _clone_page_content(self, source_id: str, target_id: str) -> None:
        blocks: Sequence[NotionBlock] = self.notion_ops.get_blocks(source_id)
        for block in blocks:
            self._clone_block(block, target_id)

    def _clone_block(self, block: NotionBlock, target_id: str) -> None:
        if not is_notion_block(block):
            logger.warning(f"Invalid block structure: {block}")
            return

        block_type: NotionBlockType = block["type"]
        block_content: BlockContent | None = block["content"].get(block_type)

        if block_content is None:
            logger.warning(f"No content found for block type: {block_type}")
            return

        if block_type == NotionBlockType.CHILD_DATABASE:
            self._clone_child_database(block_content, target_id)
        else:
            new_block_content: dict[str, Any] = transform_block_content(
                block_type, block_content
            )
            try:
                new_block: NotionBlock = self.notion_ops.append_block(
                    target_id, new_block_content
                )
                if block.get("has_children"):
                    self._clone_block_children(block["id"], new_block["id"])
            except Exception as e:
                logger.error(f"Error cloning block of type {block_type}: {str(e)}")
                logger.debug(f"Block content: {new_block_content}")
                raise

    def _clone_child_database(
        self, database_content: BlockContent, target_id: str
    ) -> None:
        try:
            title_content: BlockContent = {
                "text": [
                    {
                        "type": "text",
                        "text": {
                            "content": database_content.get(
                                "title",
                                [{"type": "text", "text": {"content": "Untitled"}}],
                            )[0]["text"]["content"]
                        },
                    }
                ]
            }
            title = transform_block_content(NotionBlockType.PARAGRAPH, title_content)[
                "paragraph"
            ]["text"]
            properties: dict[str, Any] = transform_database_properties(
                database_content.get("properties", {})
            )
            new_database: NotionDatabase = self.notion_ops.create_database(
                target_id, title, properties
            )
            if "id" in database_content:
                self._clone_database_contents(
                    database_content["id"], new_database["id"]
                )
        except Exception as e:
            logger.error(f"Error cloning child database: {str(e)}")
            logger.debug(f"Database content: {database_content}")
            raise

    def _clone_database_contents(self, source_db_id: str, target_db_id: str) -> None:
        start_cursor = None
        while True:
            response: NotionListResponse = self.notion_ops.query_database(
                source_db_id, start_cursor
            )
            for page in response["results"]:
                if not is_notion_database_page(page):
                    raise ValueError("Invalid page structure in database response")
                new_page: NotionPage = self.notion_ops.create_page(
                    target_db_id, page["properties"]
                )
                self._clone_page_content(page["id"], new_page["id"])
            if not response["has_more"]:
                break
            start_cursor: str | None = response.get("next_cursor")
            if start_cursor is None:
                logger.warning(
                    "Expected next_cursor but received None. Stopping pagination."
                )
                break

    def cleanup_staging(self) -> None:
        try:
            staging_pages: Sequence[NotionBlock] = self.notion_ops.get_blocks(
                self.staging_parent_id
            )
            for page in staging_pages:
                self.notion_ops.delete_block(page["id"])
            logger.info("Cleaned up existing staging clones")
        except Exception as e:
            logger.error(f"Error cleaning up staging area: {str(e)}")
            raise

    def _clone_block_children(self, source_block_id: str, target_block_id: str) -> None:
        children: Sequence[NotionBlock] = self.notion_ops.get_blocks(source_block_id)
        for child in children:
            self._clone_block(child, target_block_id)
