import re
import sys

import requests
from bs4 import BeautifulSoup
import json


def scrape_goodreads(goodreads_url):
    """Scrapes book data from a Goodreads book page, including tags."""
    response = requests.get(goodreads_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    print(goodreads_url)
    title = soup.select_one('.Text__title1').get_text()

    author = soup.select_one('.ContributorLink__name').text.strip()
    cover_image = soup.select_one('.BookPage__leftColumn .BookCover__image img')['src']
    description = soup.select_one(
        '.BookPageMetadataSection__description .DetailsLayoutRightParagraph__widthConstrained span.Formatted').get_text(
        strip=True)

    # Find the section containing the tags/genres
    genres = soup.find_all('a', class_='Button Button--tag-inline Button--small')
    tags = [genre.text.strip() for genre in genres if '/genres/' in genre.get('href', '')]

    pages_element = soup.find('p', attrs={'data-testid': 'pagesFormat'})

    if pages_element:
        # Extract the text from the element
        pages_text = pages_element.get_text(strip=True)

        # Use regular expression to find all numbers in the text
        numbers = re.findall(r'\d+', pages_text)

        # Assuming there's only one number in the text, which is the number of pages
        if numbers:
            number_of_pages = int(numbers[0])
        else:
            number_of_pages = None
    else:
        number_of_pages = None

    return {
        'title': title,
        'author': author,
        'cover_image': cover_image,
        'description': description,
        'tags': tags,
        'number_of_pages': number_of_pages,
        'link': goodreads_url,
    }


def scrape_wikipedia(wikipedia_url):
    """Scrapes data from a Wikipedia page."""
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1', id='firstHeading').text.strip()
    summary = soup.find('div', class_='mw-parser-output').p.text.strip()

    return {
        'title': title,
        'summary': summary
    }


def save_data_to_json(data, filename='data.json'):
    """Saves scraped data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    url = sys.argv[1]
    data = None

    if "goodreads.com" in url:
        data = scrape_goodreads(url)
    elif "wikipedia.org" in url:
        data = scrape_wikipedia(url)

    if data:
        # Replace characters in title that are invalid for filenames
        safe_title = "".join(
            [c for c in data['title'] if c.isalpha() or c.isdigit() or c in " _-"]).rstrip()
        filename = f"{safe_title}.json"
        save_data_to_json(data, filename)
        print(f"Data saved to {filename}")
    else:
        print("Failed to scrape data.")
