import requests
from bs4 import BeautifulSoup
from ..interface.data_source import DataSourceInterface

class GoodreadsScraper(DataSourceInterface):
    BASE_URL = "https://www.goodreads.com/book/isbn/"

    def fetch_by_isbn(self, isbn):
        response = requests.get(f"{self.BASE_URL}{isbn}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._scrape_data(soup)
        return None

    def fetch_by_title_author(self, title, author):
        # Goodreads doesn't have a public API, so we'd need to scrape search results
        # This is a placeholder and would require more complex implementation
        return None

    def _scrape_data(self, soup):
        return {
            "title": soup.find("h1", id="bookTitle").text.strip() if soup.find("h1", id="bookTitle") else None,
            "authors": [a.text.strip() for a in soup.find_all("a", class_="authorName")],
            "isbn": soup.find("span", itemprop="isbn").text.strip() if soup.find("span", itemprop="isbn") else None,
            "description": soup.find("div", id="description").text.strip() if soup.find("div", id="description") else None,
            "cover": soup.find("img", id="coverImage")["src"] if soup.find("img", id="coverImage") else None,
            "publish_date": soup.find("div", id="details").find("div", class_="row").text.strip() if soup.find("div", id="details") else None,
            "publisher": soup.find("div", id="details").find_all("div", class_="row")[1].text.strip() if soup.find("div", id="details") else None,
            "page_count": soup.find("span", itemprop="numberOfPages").text.strip().split()[0] if soup.find("span", itemprop="numberOfPages") else None
        }