import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import json

def scrape_goodreads(goodreads_url):
    """Scrapes book data from a Goodreads book page, including tags."""
    response = requests.get(goodreads_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    print(f"Collecting data from the {goodreads_url}")
    title = soup.select_one('[data-testid="bookTitle"]').get_text(strip=True)
    
    # Use a set to avoid duplicates
    authors_set = set()
    for contributor in soup.select('span[data-testid="name"]'):
        authors_set.add(contributor.get_text(strip=True))
    authors = list(authors_set)

    cover_image = soup.select_one('div.BookCover__image img.ResponsiveImage')['src']
    description = soup.select_one('[data-testid="description"]').get_text(strip=True)

    # Find the section containing the tags/genres
    genres_list = soup.select_one('[data-testid="genresList"]')
    genres = genres_list.select('a.Button--tag-inline span.Button__labelItem') if genres_list else []
    tags = [genre.get_text(strip=True) for genre in genres]

    pages_element = soup.find('p', attrs={'data-testid': 'pagesFormat'})
    if pages_element:
        pages_text = pages_element.get_text(strip=True)
        numbers = re.findall(r'\d+', pages_text)
        number_of_pages = int(numbers[0]) if numbers else None
    else:
        number_of_pages = None

    return {
        'title': title,
        'authors': authors,
        'cover_image': cover_image,
        'description': description,
        'tags': tags,
        'number_of_pages': number_of_pages,
        'link': goodreads_url,
    }

def save_data_to_json(data, filename='data.json'):
    """Saves scraped data to a JSON file."""
    if os.path.exists(filename):
        print(f"File '{filename}' already exists. Skipping writing.")
        return
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def scrape_url(url):
    if "goodreads.com" in url:
        return scrape_goodreads(url)
    else:
        print("Unable to scrape from anything but goodreads at the moment. If you require "
              "scrapping for another website, please create an issue, PR or fork the repo "
              "at https://github.com/Dimm-ddr/BookScrapper")
        sys.exit()

def scrape_txt_file(input_file):
    with open(input_file, 'r') as file:
        for line in file:
            url = line.strip()
            data = scrape_url(url)
            save_to_json_file(data)

def save_to_json_file(data):
    if data:
        safe_title = "".join([c for c in data['title'] if c.isalpha() or c.isdigit() or c in " _-"]).rstrip()
        filename = f"{safe_title}.json"
        save_data_to_json(data, filename)
        print(f"Data saved to {filename}")
    else:
        print("Failed to scrape data.")

if __name__ == "__main__":
    argument = sys.argv[1]
    url = None
    input_file = None
    if "https" in argument:
        url = argument
    elif ".txt" in argument:
        input_file = argument
    else:
        print("Incorrect script parameter. Pass either goodreads URL or text file with goodreads urls")
        sys.exit()

    data = None
    if url is not None:
        print(f"Scrapping single URL")
        data = scrape_url(url)
        save_to_json_file(data)
    else:
        print(f"Scrapping URLs from the {input_file} file")
        scrape_txt_file(input_file)
