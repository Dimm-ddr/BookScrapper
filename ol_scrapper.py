import os
import requests
import json
from urllib.parse import quote

# Variable to specify the desired language
DESIRED_LANGUAGE = "ru"

def read_input_file(filename):
    """Reads the input JSON file containing titles and authors."""
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def search_book(title, author, language):
    """Searches for a book by title and author on Open Library."""
    title_encoded = quote(title)
    author_encoded = quote(author)
    query = f"title={title_encoded}&author={author_encoded}&lang={language}"
    url = f"https://openlibrary.org/search.json?{query}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['docs']:
            return data['docs'][0]  # Return the first matching result
    return None

def fetch_book_description(work_key):
    """Fetches the book description from Open Library using the work key."""
    url = f"https://openlibrary.org{work_key}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("description", {}).get("value", "") if isinstance(data.get("description"), dict) else data.get("description", "")
    else:
        return ""

def extract_book_fields(book_data):
    """Extracts relevant fields from book data."""
    return {
        "title": book_data.get("title"),
        "authors": book_data.get("author_name", []),
        "first_publish_year": book_data.get("first_publish_year"),
        "edition_count": book_data.get("edition_count"),
        "languages": book_data.get("language", []),
        "isbn": book_data.get("isbn", []),
        "tags": book_data.get("subject", []),
        "link": f"https://openlibrary.org{book_data.get('key')}",
        "description": fetch_book_description(book_data.get("key")),
        "cover": f"https://covers.openlibrary.org/b/id/{book_data.get('cover_i', 'placeholder')}-L.jpg"  # Placeholder for cover image URL
    }

def save_to_json_file(data, filename):
    """Saves the extracted book data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    input_filename = "input_books.json"  # JSON file with titles and authors
    items = read_input_file(input_filename)

    for item in items:
        title = item.get("title")
        author = item.get("author")
        if title and author:
            print(f"Searching for: {title} by {author}")
            book_data = search_book(title, author, DESIRED_LANGUAGE)
            if book_data:
                extracted_data = extract_book_fields(book_data)
                output_filename = f"{quote(title.replace(' ', '_'))}_{quote(author.replace(' ', '_'))}.json"
                save_to_json_file(extracted_data, output_filename)
            else:
                print(f"No data found for: {title} by {author}")
        else:
            print(f"Invalid entry: {item}")
