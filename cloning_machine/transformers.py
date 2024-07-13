import logging
from typing import Any
from .notion_types import BlockContent
from .notion_constants import NotionBlockType

logger: logging.Logger = logging.getLogger(__name__)


def to_rich_text(text: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a string or existing rich text to the Notion API rich text format."""
    if isinstance(text, str):
        return [{"type": "text", "text": {"content": text}}]
    elif isinstance(text, list) and all(isinstance(item, dict) for item in text):
        return text
    else:
        raise ValueError(
            "Invalid input: must be a string or a list of rich text objects"
        )


def transform_block_content(
    block_type: NotionBlockType, content: BlockContent
) -> dict[str, Any]:
    """Transform block content to the format expected by Notion API."""
    transformed_content: dict[str, Any] = {}
    for key, value in content.items():
        if key in ["text", "title", "caption"]:
            if isinstance(value, (str, list)):
                transformed_content[key] = to_rich_text(value)
            else:
                logger.warning(
                    f"Unexpected type for {key}: {type(value)}. Using as-is."
                )
                transformed_content[key] = value
        else:
            transformed_content[key] = value
    return {
        "type": block_type.name.lower(),
        block_type.name.lower(): transformed_content,
    }


def transform_database_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Transform database properties to the format expected by Notion API."""
    transformed_properties = {}
    for prop_name, prop_value in properties.items():
        if prop_value["type"] in ["title", "rich_text"]:
            transformed_properties[prop_name] = {prop_value["type"]: {}}
        else:
            transformed_properties[prop_name] = prop_value
    return transformed_properties
