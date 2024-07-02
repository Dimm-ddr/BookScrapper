import os
import requests
from bs4 import BeautifulSoup
import json

def read_urls(filename):
    """Reads URLs from a text file."""
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def fetch_isbn_from_goodreads(url, output_html_filename="response.html"):
    """Fetches ISBN from a Goodreads book page and saves raw HTML response for debugging."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Locate the ld+json script tag
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            json_content = json.loads(script_tag.string)
            isbn = json_content.get('isbn', None)
            if isbn:
                return isbn
    return None

def save_isbns_to_file(isbns, filename="isbns.txt"):
    """Saves a list of ISBNs to a text file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for isbn in isbns:
            file.write(isbn + "\n")
    print(f"ISBNs saved to {filename}")

def save_debug_output(urls, filename="debug_output.txt"):
    """Saves a list of URLs for which ISBN was not found to a text file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + "\n")
    print(f"Debug output saved to {filename}")

if __name__ == "__main__":
    urls_file = "urls.txt"  # File with Goodreads URLs
    urls = read_urls(urls_file)

    isbns = []
    debug_urls = []

    for url in urls:
        print(f"Fetching ISBN from: {url}")
        isbn = fetch_isbn_from_goodreads(url, output_html_filename="response.html")
        if isbn:
            print(f"Found ISBN: {isbn}")
            isbns.append(isbn)
        else:
            print(f"ISBN not found for: {url}")
            debug_urls.append(url)

    # Save ISBNs to a file
    save_isbns_to_file(isbns)
    # Save debug output to a file
    save_debug_output(debug_urls)
