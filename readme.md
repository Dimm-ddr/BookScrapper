# Queer Books Data Pipeline

This project is designed to create and manage a database of queer books, with a focus on books that are translated into or originally written in Russian. The project fetches data from multiple sources (Open Library, Google Books, and Goodreads), processes the data, and uploads it to a Notion database.

## Features

1. **Data Retrieval:** Fetches book information from Open Library, Google Books APIs, and Goodreads.
2. **Data Processing:** Processes and standardizes book data from various sources.
3. **Data Uploading:** Uploads processed data to a Notion database.
4. **Command Line Interface (CLI):** Provides an easy way to run different components of the project.

## Prerequisites

- Python 3.12
- Notion API Token
- Notion Database ID

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Dimm-ddr/BookScrapper.git
   cd queer-books-data-pipeline
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:

   ``` env
   NOTION_SECRET=your_notion_secret_key
   Database_ID=your_notion_database_id
   ```

   Replace `your_notion_secret_key` and `your_notion_database_id` with your actual Notion API secret and database ID.

## Setting Up Your Notion Database

Ensure your Notion database has the following properties:

- **Title** (Title type): For the book title.
- **Authors** (Multi-select type): For the book's authors.
- **Cover** (Files & media type): To store a link to the book's cover image.
- **Tags** (Multi-select type): For various tags associated with the book.
- **Description** (Text type): For a brief description or synopsis of the book.
- **Page count** (Number type): Book page count.
- **Link** (URL type): For a link to more information about the book.
- **First Publish Year** (Number type): For the year the book was first published.
- **Languages** (Multi-select type): For the languages the book is available in.
- **ISBN** (Text type): For the book's ISBN numbers.
- **Editions count** (Number type): Number of known editions.

## Usage

The project provides a command-line interface with various options:

```bash
python main.py [OPTIONS]
```

### Options

- `--isbn ISBN`: Fetch book data by ISBN
- `--title TITLE`: Book title for fetching data
- `--author AUTHOR`: Book author for fetching data
- `--isbn-file FILE`: File containing a list of ISBNs
- `--goodreads-file FILE`: File containing a list of Goodreads URLs
- `--upload`: Upload books to Notion
- `--no-debug`: Disable debug logging

### Examples

1. Fetch data for a single ISBN:

   ```bash
   python main.py --isbn 9781234567890
   ```

2. Fetch data by title and author:

   ```bash
   python main.py --title "Book Title" --author "Author Name"
   ```

3. Process ISBNs from a file:

   ```bash
   python main.py --isbn-file path/to/isbn_list.txt
   ```

4. Process Goodreads URLs from a file:

   ```bash
   python main.py --goodreads-file path/to/goodreads_urls.txt
   ```

5. Upload processed books to Notion:

   ```bash
   python main.py --upload
   ```

6. Run with debug logging disabled:

   ```bash
   python main.py --isbn 9781234567890 --no-debug
   ```

## Data Storage

Processed book data is stored in JSON format in the `data/books` directory. Each book is saved in a separate file named after its title.

## Error Handling

Errors during processing are logged in `error_log.txt` in the project root directory.

## Contributing

Contributions are welcome! Please create an issue or a pull request.

## License

This project is licensed under the MIT License.
