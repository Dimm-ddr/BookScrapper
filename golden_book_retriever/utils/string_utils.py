import re
import unicodedata

def clean_text(text):
    """
    Clean and normalize text by removing extra whitespace and converting to ASCII.
    """
    if not text:
        return ""
    # Normalize Unicode characters to their closest ASCII equivalent
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_author_name(name):
    """
    Normalize author name to "Lastname, Firstname" format.
    """
    name = clean_text(name)
    parts = name.split(',')
    if len(parts) == 2:
        return f"{parts[0].strip()}, {parts[1].strip()}"
    parts = name.split()
    if len(parts) > 1:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name