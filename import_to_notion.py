import glob
import json
import os

from notion_client import Client

# Initialize the Notion client with your integration token
notion_secret = os.getenv('NOTION_SECRET')
database_id = os.getenv('DATABASE_ID')
notion = Client(auth=notion_secret)


def add_book_to_notion(data):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {
                "title": [{"text": {"content": data["title"]}}]
            },
            "Author": {
                "rich_text": [{"text": {"content": data["author"]}}]
            },
            "Cover Image": {
                "type": "files",
                "files": [{"name": "Cover Image", "type": "external",
                           "external": {"url": data["cover_image"]}}]
            },
            "Description": {
                "rich_text": [{"text": {"content": data["description"]}}]
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in data["tags"]]
            },
            "Page count": {
                "number": data["number_of_pages"]
            },
            "Link": {
                "url": book_data.get("link"),
            },
            "Russian translation": {
                "select": {"name": "Неизвестно"},
            },
            "Статус": {
                "select": {"name": "Непрочитано"},
            },
        }
    )


# List of your JSON files
json_files = glob.glob('./*.json')

for json_file in json_files:
    print(json_file)
    with open(json_file, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
        add_book_to_notion(book_data)
        print(f"Added book from {json_file} to Notion")
