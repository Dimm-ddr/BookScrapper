import json
from notion_client import Client
from data.datamodel import BookData


class NotionUploader:
    def __init__(self, secret: str, database_id: str) -> None:
        self.notion = Client(auth=secret)
        self.database_id: str = database_id

    def upload_from_json(self, json_file: str) -> None:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            book_data = BookData(**data)
            self.upload_book_data(book_data)

    def upload_book_data(self, book_data: BookData) -> None:
        properties = {
            "Title": {"title": [{"text": {"content": book_data.title}}]},
            "Authors": {
                "multi_select": [{"name": author} for author in book_data.authors]
            },
            "Cover": {"url": book_data.cover},
            "Tags": {"multi_select": [{"name": tag} for tag in book_data.tags]},
            "Description": {
                "rich_text": [{"text": {"content": book_data.description}}]
            },
            "Page Count": {"number": book_data.page_count},
            "Link": {"url": book_data.link},
            "First Publish Year": {"number": book_data.first_publish_year},
            "Languages": {
                "multi_select": [{"name": lang} for lang in book_data.languages]
            },
            "ISBN": {"number": book_data.isbn},
            "Editions count": {"number": book_data.editions_count},
        }
        self.notion.pages.create(
            parent={"database_id": self.database_id}, properties=properties
        )
