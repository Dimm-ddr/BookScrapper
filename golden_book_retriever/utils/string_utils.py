import re
from typing import Any
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and converting to ASCII.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned and normalized text.
    """
    if not text:
        return ""
    # Normalize Unicode characters to their closest ASCII equivalent
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    # Remove extra whitespace
    return re.sub(r"\s+", " ", text).strip()


def normalize_author_name(name: str) -> str:
    """
    Normalize author name to "Lastname, Firstname" format.

    Args:
        name (str): The author name to normalize.

    Returns:
        str: The normalized author name.
    """
    name = clean_text(name)
    parts: list[str] = name.split(",")
    if len(parts) == 2:
        return f"{parts[0].strip()}, {parts[1].strip()}"
    parts = name.split()
    if len(parts) > 1:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name


def is_useful_tag(tag: str) -> bool:
    """
    Check if a tag is useful based on certain criteria.
    """
    # Filter out tags that start with "nyt:" or contain "=YYYY-MM-DD"
    if tag.startswith("nyt:") or re.search(r"=\d{4}-\d{2}-\d{2}", tag):
        return False

    # Filter out tags related to American reading levels
    if re.match(r"reading level-grade \d+", tag, re.IGNORECASE):
        return False

    # Add more filtering rules here if needed

    return True


def normalize_tags(tags: list[str], max_tags: int = 50) -> list[str]:
    """
    Normalize tags by splitting on commas, trimming whitespace,
    converting to lowercase, removing duplicates, and filtering out useless tags.
    """
    normalized_tags = set()
    for tag in tags:
        # Split tags containing commas
        split_tags: list[str | Any] = re.split(r"\s*,\s*", tag)
        for split_tag in split_tags:
            # Normalize each tag
            normalized_tag: str = re.sub(r"\s+", " ", split_tag.strip().lower())
            if normalized_tag and is_useful_tag(normalized_tag):
                normalized_tags.add(normalized_tag)

    # Sort tags alphabetically and limit to max_tags
    return sorted(list(normalized_tags))[:max_tags]
