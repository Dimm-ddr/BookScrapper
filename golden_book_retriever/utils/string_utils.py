import re
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
