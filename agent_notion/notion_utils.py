# notion_utils.py

from typing import Any


def prepare_multiselect_field(field_name: str, values: list[str]) -> dict[str, Any]:
    """
    Prepare a multi-select field for Notion, sanitizing values.
    """
    sanitized_values: list[str] = sanitize_list(values)
    return {
        field_name: {"multi_select": [{"name": value} for value in sanitized_values]}
    }


def prepare_select_field(field_name: str, value: str) -> dict[str, Any]:
    """
    Prepare a select field for Notion, sanitizing the value.
    """
    sanitized_value: str = sanitize_field_value(value)
    return {field_name: {"select": {"name": sanitized_value}}}


def prepare_description_blocks(description: str) -> list[dict[str, Any]]:
    """
    Prepare Notion blocks for the book description.
    """
    return [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Полное описание"}}]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": description}}]
            },
        },
    ]


# Import these functions from text_utils.py
from text_utils import sanitize_field_value, sanitize_list
