# text_utils.py

import re
from typing import List


def sanitize_field_value(value: str) -> str:
    """
    Sanitize a field value by removing commas and other problematic characters.
    """
    sanitized: str = re.sub(r'[,"\'\(\)\[\]{}]', "", value)
    return re.sub(r"\s+", " ", sanitized).strip()


def sanitize_list(items: List[str]) -> List[str]:
    """
    Sanitize a list of items, removing duplicates and empty values.
    """
    return list(set(sanitize_field_value(item) for item in items if item))


def enhance_title(title: str) -> str:
    """
    Enhance a title by capitalizing each word.
    """
    return " ".join(word.capitalize() for word in title.split())


def extract_brief(description: str) -> str:
    """
    Extract a brief description from the full text.
    """
    sentences: List[str] = re.split(r"(?<=[.!?])\s+", description.strip())
    brief: str = " ".join(sentences[:2])
    if len(brief) > 200:
        brief = brief[:197].rsplit(" ", 1)[0] + "..."
    return brief
