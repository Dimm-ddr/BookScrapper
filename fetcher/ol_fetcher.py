from typing import Any, Literal
import requests
import json

# Variable to specify the desired language
DESIRED_LANGUAGE = "ru"


def read_isbn_file(filename: str) -> list[str]:
    """Reads the input text file containing ISBNs, one per line."""
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]


def search_book_by_isbn(isbn: str, language: str) -> Any | None:
    """Searches for a book by ISBN on Open Library."""
    query: str = f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data&lang={language}"
    url: str = f"https://openlibrary.org/api/books{query}"
    print(url)
    response: requests.Response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get(f"ISBN:{isbn}")
    return None


def fetch_book_description(work_key: str) -> Any | Literal[""]:
    """Fetches the book description from Open Library using the work key."""
    url: str = f"https://openlibrary.org{work_key}.json"
    response: requests.Response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return (
            data.get("description", {}).get("value", "")
            if isinstance(data.get("description"), dict)
            else data.get("description", "")
        )
    else:
        return ""


def extract_book_fields(book_data) -> dict[str, Any]:
    """Extracts relevant fields from book data."""
    return {
        "title": book_data.get("title"),
        "authors": [author.get("name") for author in book_data.get("authors", [])],
        "first_publish_year": book_data.get("publish_date"),
        "edition_count": len(book_data.get("identifiers", {}).get("isbn_13", [])),
        "languages": [
            lang.get("key").split("/")[-1] for lang in book_data.get("languages", [])
        ],
        "isbn": book_data.get("identifiers", {}).get("isbn_13", []),
        "tags": [subject.get("name") for subject in book_data.get("subjects", [])],
        "link": f"https://openlibrary.org{book_data.get('key')}",
        "description": fetch_book_description(book_data.get("key")),
        "cover": book_data.get("cover", {}).get("large"),
    }


def save_to_json_file(data, filename) -> None:
    """Saves the extracted book data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}")


def save_missing_isbns_to_file(missing_isbns, filename="missing_books.txt") -> None:
    """Saves the list of missing ISBNs to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        for isbn in missing_isbns:
            file.write(isbn + "\n")
    print(f"Missing ISBNs saved to {filename}")


if __name__ == "__main__":
    input_filename = "isbns.txt"  # Text file with ISBNs, one per line
    isbns: list[str] = read_isbn_file(input_filename)

    missing_isbns = []

    for isbn in isbns:
        print(f"Searching for ISBN: {isbn}")
        book_data = search_book_by_isbn(isbn, DESIRED_LANGUAGE)
        if book_data:
            extracted_data: dict[str, Any] = extract_book_fields(book_data)
            output_filename: str = f"{isbn}.json"
            save_to_json_file(extracted_data, output_filename)
        else:
            print(f"No data found for ISBN: {isbn}")
            missing_isbns.append(isbn)

    # Save missing ISBNs to a file
    save_missing_isbns_to_file(missing_isbns)
