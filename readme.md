# Queer Books Data Pipeline

This project is designed to create and manage a database of queer books, with a focus on books that are translated into or originally written in Russian. The project fetches data from multiple sources (Open Library, Google Books, and Goodreads), processes the data, and uploads it to a Notion database.

## Features

1. **Data Scraping:** Extracts book information from Goodreads.
2. **Data Fetching:** Fetches book information from Open Library and Google Books APIs.
3. **Data Uploading:** Uploads processed data to a Notion database.
4. **Command Line Interface (CLI):** Provides an easy way to run the different components of the project.

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

4. Create a Notion Integration:
   - Navigate to [My Integrations](https://www.notion.so/my-integrations) on Notion.
   - Click the **"+ New integration"** button.
   - Fill out the form with your integration's name and associate it with your
   workspace.
   - Note the **"Internal Integration Token"** provided after creation for later
   use.
5. Share Your Database with the Integration:
   - Open the Notion database you want to integrate with.
   - Click the **"Share"** button on the top right.
   - Choose the integration you created and share the database with it.
6. Find Your Database ID:
   - Open your database as a page, the URL will look like:
   `https://www.notion.so/{workspace}/{database_id}?v={view_id}`
   - The Database ID is the part between the last `/` and `?v=`.
7. Set up environment variables for Notion API:

   ```bash
   export NOTION_SECRET='your-notion-secret'
   export DATABASE_ID='your-database-id'
   ```

   > **⚠️ Warning**:Remember to never share your Internal Integration Token publicly to maintain the
security of your Notion integration.

## Setting Up Your Notion Database for Book Metadata Import

To utilize the provided scripts for uploading book metadata into your Notion database, ensure your database is set up with the following properties:

- **Title** (Title type): For the book title.
- **Authors** (Multi-select type): For the book's authors.
- **Cover** (Files & media type): To store a link to the book's cover image.
- **Tags** (Multi-select type): For various tags associated with the book, like genre.
- **Description** (Text type): For a brief description or synopsis of the book.
- **Page count** (number): Book page count.
- **Link** (URL type): For a link to more information about the book.
- **First Publish Year** (Number type): For the year the book was first published.
- **Languages** (Multi-select type): For the languages the book is available in.
- **ISBN** (Text type): For the book's ISBN numbers.
- **Editions count** (number): Number of known editions.

## Usage

### Command Line Interface

You can use the provided CLI to run different components of the project.

1. **Fetch book data by ISBN:**

   ```bash
   python main.py --isbn --input isbn.txt --output output.json
   ```

2. **Scrape book data from Goodreads URL:**

   ```bash
   python main.py --url --input goodreads_url.txt --output output.json
   ```

3. **Upload data to Notion:**

   ```bash
   python main.py --upload --output output.json
   ```

### Fetching Data

1. **Fetching by ISBN:**
   - Create a text file (`isbn.txt`) with one ISBN per line.
   - Run the following command to fetch data for each ISBN and save it to `output.json`:

     ```bash
     python main.py --isbn --input isbn.txt --output output.json
     ```

2. **Scraping from Goodreads:**
   - Create a text file (`goodreads_url.txt`) with one Goodreads book URL per line.
   - Run the following command to scrape data from each URL and save it to `output.json`:

     ```bash
     python main.py --url --input goodreads_url.txt --output output.json
     ```

### Uploading Data

- Ensure `output.json` contains the data you want to upload.
- Run the following command to upload the data to Notion:

  ```bash
  python main.py --upload --output output.json
  ```

## Contributing

Contributions are welcome! Please create an issue or a pull request.

## License

This project is licensed under the MIT License.
