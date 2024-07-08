# agent_notion/normalizer.py


def normalize_multiselect(items: list[str]) -> list[str]:
    """
    Normalize items for a multi-select field by removing commas and trimming whitespace.

    Args:
        items (list[str]): List of items to normalize.

    Returns:
        list[str]: Normalized list of items.
    """
    return [item.replace(",", "").strip() for item in items]


def prettify_title(title: str) -> str:
    """
    Prettify a title by capitalizing each word.

    Args:
        title (str): The title to prettify.

    Returns:
        str: The prettified title.
    """
    return " ".join(word.capitalize() for word in title.split())


# Add more normalization functions as needed
