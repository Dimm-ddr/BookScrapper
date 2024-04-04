import glob
import json
import os
import time

from notion_client import Client, APIResponseError

# Initialize the Notion client with your integration token
notion_secret = os.getenv("NOTION_SECRET")
database_id = os.getenv("DATABASE_ID")
notion = Client(auth=notion_secret)


def is_book_already_exist(title):
    """
    Checks if a book with the given title already exists in the Notion database.
    Implements retry logic for rate limit (HTTP 429) responses.

    Returns True if the book exists, False otherwise.
    """
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            query_filter = {"property": "Title", "title": {"equals": title}}
            response = notion.databases.query(
                database_id=database_id, filter=query_filter
            )

            # Assuming the response is a dictionary that includes a 'results' key
            return len(response.get("results", [])) > 0

        except APIResponseError as e:
            if e.code.RateLimited:
                print(
                    f"""Request rate limited. Retrying in 2 seconds...
                    Attempt {retries + 1}/{max_retries}"""
                )
                time.sleep(2)
                retries += 1
            else:
                print(f"An error occurred: {e}")
                break
    else:
        print("Max retries reached. Exiting script.")
        exit()  # or handle it in a way that fits your script's flow

    return False


def add_book_to_notion(data):
    if is_book_already_exist(data["title"]):
        print(f"Book titled '{data['title']}' already exists in the database.")
        return

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": data["title"]}}]},
            "Author": {"rich_text": [{"text": {"content": data["author"]}}]},
            "Cover Image": {
                "type": "files",
                "files": [
                    {
                        "name": "Cover Image",
                        "type": "external",
                        "external": {"url": data["cover_image"]},
                    }
                ],
            },
            "Description": {"rich_text": [{"text": {"content": data["description"]}}]},
            "Tags": {"multi_select": [{"name": tag} for tag in data["tags"]]},
            "Page count": {"number": data["number_of_pages"]},
            "Link": {
                "url": book_data.get("link"),
            },
            "Russian translation": {
                "select": {"name": "Неизвестно"},
            },
            "Статус": {
                "select": {"name": "Непрочитано"},
            },
        },
    )


# List of your JSON files
json_files = glob.glob("./*.json")

for json_file in json_files:
    print(json_file)
    with open(json_file, "r", encoding="utf-8") as f:
        book_data = json.load(f)
        add_book_to_notion(book_data)
        print(f"Added book from {json_file} to Notion")
