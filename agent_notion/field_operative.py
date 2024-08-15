# agent_notion/field_operative.py

import re
from typing import Any

from agent_notion.language_utils import standardize_language_code
from agent_notion.notion_utils import prepare_description_blocks


def sanitize_field_value(value: str) -> str:
    """
    Sanitize a field value by removing commas and other problematic characters.
    """
    # Remove commas, quotation marks, and other potentially problematic characters
    sanitized: str = re.sub(r'[,"\'\(\)\[\]{}]', "", value)
    # Replace multiple spaces with a single space and trim
    return re.sub(r"\s+", " ", sanitized).strip()


def sanitize_list(items: list[str]) -> list[str]:
    """
    Sanitize a list of items, removing duplicates and empty values.
    """
    return list(set(sanitize_field_value(item) for item in items if item))


def prepare_multiselect_field(field_name: str, values: list[str]) -> dict:
    """
    Prepare a multi-select field for Notion, sanitizing values.
    """
    sanitized_values: list[str] = sanitize_list(values)
    return {
        field_name: {"multi_select": [{"name": value} for value in sanitized_values]}
    }


def prepare_select_field(field_name: str, value: str) -> dict:
    """
    Prepare a select field for Notion, sanitizing the value.
    """
    sanitized_value: str = sanitize_field_value(value)
    return {field_name: {"select": {"name": sanitized_value}}}


def enhance_title(title: str) -> str:
    """
    Enhance a title by capitalizing each word.

    Args:
        title (str): The title to enhance.

    Returns:
        str: The enhanced title.
    """
    return " ".join(word.capitalize() for word in title.split())


def extract_brief(description: str) -> str:
    """
    Extract a brief description from the full text.

    Args:
        description (str): The full description.

    Returns:
        str: A brief description, truncated to about 200 characters.
    """
    sentences: list[str | Any] = re.split(r"(?<=[.!?])\s+", description.strip())
    brief: str = " ".join(sentences[:2])
    if len(brief) > 200:
        brief = brief[:197].rsplit(" ", 1)[0] + "..."
    return brief


def prepare_book_intel(book_data: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare book data for Notion upload.
    """
    description: str = book_data.get("description", "")
    brief: str = extract_brief(description)
    isbn: str = book_data.get("isbn", "") or ""

    authors: list[str] = book_data.get("authors", [])
    languages: list[str] = book_data.get("languages", [])
    tags: list[str] = book_data.get("tags", [])
    publishers: list[str] = book_data.get("publishers", [])

    standardized_languages: list[str] = [
        standardize_language_code(lang, book_data) for lang in languages
    ]

    sanitized_tags: list[str] = [sanitize_field_value(tag) for tag in tags]

    prepared_data = {
        "Название": {
            "title": [{"text": {"content": enhance_title(book_data.get("title", ""))}}]
        },
        "ISBN": {"rich_text": [{"text": {"content": isbn}}]},
        "Год первой публикации": {"number": book_data.get("first_publish_year")},
        "Кратко": {"rich_text": [{"text": {"content": brief}}]},
        "Количество страниц": {"number": book_data.get("page_count")},
        "Cover": {
            "type": "files",
            "files": [
                {
                    "name": "Cover Image",
                    "type": "external",
                    "external": {"url": book_data.get("cover", "")},
                }
            ],
        },
        "Link": {"url": book_data.get("link", "")},
        "Editions count": {"number": book_data.get("editions_count")},
    }

    prepared_data.update(prepare_multiselect_field("Авторы", authors))
    prepared_data.update(prepare_multiselect_field("Языки", standardized_languages))
    prepared_data.update(prepare_multiselect_field("Тэги", sanitized_tags))
    prepared_data.update(prepare_multiselect_field("Издатель", publishers))

    russian_translation = (
        "Есть" if "Русский" in standardized_languages else "Неизвестно"
    )
    prepared_data.update(
        prepare_select_field("Перевод на русский", russian_translation)
    )

    series: str | None = book_data.get("series")
    if series is not None:
        prepared_data["Серия"] = {"select": {"name": sanitize_field_value(series)}}

    return prepared_data


def prepare_description_for_notion(description: str) -> list[dict[str, Any]]:
    """
    Prepare the book description for Notion upload.
    """
    return prepare_description_blocks(description)
