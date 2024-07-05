"""
Data model for book information in the Queer Books Data Pipeline.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, List, Optional
import json

@dataclass
class BookData:
    """
    Represents book data with various attributes.
    """
    title: str
    first_publish_year: Optional[int]
    link: Optional[str]
    description: Optional[str]
    cover: Optional[str]
    page_count: Optional[int]
    editions_count: Optional[int]
    isbn: Optional[str]
    authors: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate data after initialization.
        """
        if self.first_publish_year is not None and self.first_publish_year < 0:
            raise ValueError("First publish year cannot be negative")
        
        if self.page_count is not None and self.page_count <= 0:
            raise ValueError("Page count must be positive")
        
        if self.editions_count is not None and self.editions_count < 0:
            raise ValueError("Editions count cannot be negative")

    def to_json(self) -> str:
        """
        Convert the BookData object to a JSON string.

        Returns:
            str: JSON representation of the BookData object.
        """
        return json.dumps(asdict(self), ensure_ascii=False, indent=4)

    @classmethod
    def from_json(cls, json_str: str) -> 'BookData':
        """
        Create a BookData object from a JSON string.

        Args:
            json_str (str): JSON string representing a BookData object.

        Returns:
            BookData: Instance created from the JSON data.
        """
        data: dict[str, Any] = json.loads(json_str)
        return cls(**data)