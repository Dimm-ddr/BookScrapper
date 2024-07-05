from .sources.openlibrary import OpenLibraryAPI
from .sources.googlebooks import GoogleBooksAPI
from .sources.goodreads import GoodreadsScraper

class DataAggregator:
    def __init__(self):
        self.sources = [
            OpenLibraryAPI(),
            GoogleBooksAPI(),
            GoodreadsScraper()
        ]

    def fetch_data(self, isbn=None, title=None, author=None):
        book_data = {}
        for source in self.sources:
            if isbn:
                new_data = source.fetch_by_isbn(isbn)
            else:
                new_data = source.fetch_by_title_author(title, author)
            
            if new_data:
                book_data.update(new_data)
                if self._is_data_complete(book_data):
                    break
        
        return book_data

    def _is_data_complete(self, data):
        # Define what constitutes complete data
        required_fields = ['title', 'authors', 'isbn', 'description']
        return all(field in data for field in required_fields)