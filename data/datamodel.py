from dataclasses import asdict, dataclass, field
import json


@dataclass
class BookData:
    title: str
    first_publish_year: int | None
    link: str | None
    description: str | None
    cover: str | None
    authors: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    isbn: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=4)
