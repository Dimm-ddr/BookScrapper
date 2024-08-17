import re
from bs4 import BeautifulSoup


class Jan_Itor:
    def __init__(self) -> None:
        self.unwanted_tags: set[str] = {
            "to-read",
            "currently-reading",
            "owned",
            "favorites",
            "books-i-own",
            "my-books",
            "default",
            "kindle",
            "library",
            "audiobook",
            "ebook",
            "e-book",
            "hardcover",
            "paperback",
            "audible",
            "audio",
            "to-buy",
            "english",
            "fiction",
            "non-fiction",
            "nonfiction",
        }

    def clean_html(self, text: str) -> str:
        """Remove HTML tags from the text."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()

    def fix_spaces(self, text: str) -> str:
        """Fix extra spaces and newlines in the text."""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_author(self, author: str) -> str:
        """Normalize author name."""
        author = re.sub(r"\([^)]*\)", "", author)
        return " ".join(word.capitalize() for word in author.split())

    def normalize_tag(self, tag: str) -> str:
        """Normalize a single tag."""
        tag = re.sub(r"[^\w\s-]", "", tag.lower())
        return re.sub(r"\s+", "-", tag)

    def filter_tags(self, tags: list[str]) -> list[str]:
        """Remove unwanted tags and duplicates."""
        normalized_tags: list[str] = [self.normalize_tag(tag) for tag in tags]
        filtered_tags: list[str] = [
            tag for tag in normalized_tags if tag not in self.unwanted_tags
        ]
        return list(set(filtered_tags))

    def normalize_isbn(self, isbn: str) -> str:
        """Normalize ISBN by removing hyphens and spaces."""
        return re.sub(r"[-\s]", "", isbn)

    def extract_brief(self, description: str, max_length: int = 200) -> str:
        """Extract a brief description from the full text."""
        sentences: list[str] = description.split(".")
        brief: str = ". ".join(sentences[:2])
        if len(brief) > max_length:
            brief = brief[: max_length - 3] + "..."
        return brief.strip()

    def enhance_title(self, title: str) -> str:
        """Enhance a title by capitalizing each word."""
        return " ".join(word.capitalize() for word in title.split())


jan_itor = Jan_Itor()
