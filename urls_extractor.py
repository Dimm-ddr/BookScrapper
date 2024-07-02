import os
import requests
import json
from notion_client import Client

# Fetch Notion API token and database ID from environment variables
NOTION_SECRET = os.getenv("NOTION_SECRET")
OLD_DATABASE_ID = os.getenv("OLD_DATABASE_ID")

# Initialize Notion client
notion = Client(auth=NOTION_SECRET)

def fetch_all_notion_database_items(database_id):
    """Fetches all items from a Notion database handling pagination."""
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        if start_cursor:
            response = notion.databases.query(database_id=database_id, start_cursor=start_cursor)
        else:
            response = notion.databases.query(database_id=database_id)

        if 'results' not in response:
            raise Exception("Failed to fetch database")

        all_results.extend(response['results'])
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor', None)

    return all_results

def extract_urls_from_database(database_data):
    """Extracts URLs from Notion database data."""
    urls = []
    for result in database_data:
        link_property = result['properties'].get('Link')
        if link_property and link_property['type'] == 'url':
            urls.append(link_property['url'])
    return urls

def save_urls_to_file(urls, filename="urls.txt"):
    """Saves a list of URLs to a text file."""
    with open(filename, 'w') as file:
        for url in urls:
            file.write(url + "\n")
    print(f"URLs saved to {filename}")

if __name__ == "__main__":
    # Fetch all data from Notion database
    database_data = fetch_all_notion_database_items(OLD_DATABASE_ID)
    
    # Extract URLs
    urls = extract_urls_from_database(database_data)
    
    # Save URLs to a file
    save_urls_to_file(urls)
