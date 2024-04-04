# Setting Up Notion Integration

1. **Create a Notion Integration**
   - Navigate to [My Integrations](https://www.notion.so/my-integrations) on Notion.
   - Click the **"+ New integration"** button.
   - Fill out the form with your integration's name and associate it with your
   workspace.
   - Note the **"Internal Integration Token"** provided after creation for later
   use.

2. **Share Your Database with the Integration**
   - Open the Notion database you want to integrate with.
   - Click the **"Share"** button on the top right.
   - Choose the integration you created and share the database with it.

3. **Find Your Database ID**
   - Open your database as a page, the URL will look like:
   `https://www.notion.so/{workspace}/{database_id}?v={view_id}`
   - The Database ID is the part between the last `/` and `?v=`.

4. **Use Environment Variables for Security**
   - Store your **Internal Integration Token** and **Database ID** as
   environment variables in your development environment for secure access.

5. **Access Database via API**
   - Use the stored environment variables in your code to authenticate and
   interact with your Notion database using the API.

Remember to never share your Internal Integration Token publicly to maintain the
security of your Notion integration.

## Setting Up Environment Variables

To securely use the scripts, you need to set up environment variables for your
Notion integration secret and database ID:

1. **Prepare the Script**:
   - Duplicate the `set-env-vars-example.ps1` (for Windows) or
   `set-env-vars-example.sh` (for Linux/Mac) file.
   - Rename the duplicate to something like `set-env-vars.ps1` or
   `set-env-vars.sh`.

2. **Edit the Script**:
   - Open your duplicated script in a text editor.
   - Replace the placeholder values with your actual Notion integration secret
   and database ID.

3. **Run the Script**:
   - On Windows, execute `.\set-env-vars.ps1` in PowerShell.
   - On Linux/Mac, run `source ./set-env-vars.sh` in the terminal.

> **⚠️ Warning**: Never add the script with your actual credentials to a
repository or share it. Always keep your Notion secret safe.

This setup will enable the scripts to access your Notion database securely.

## Setting Up Your Notion Database for Book Metadata Import

To utilize the provided scripts for uploading book metadata into your Notion
database, ensure your database is set up with the following properties:

- **Title** (Title type): For the book title.
- **Author** (Text type): For the book's author.
- **Cover Image** (Files & media type): To store a link to the book's cover
image.
- **Description** (Text type): For a brief description or synopsis of the book.
- **Tags** (Multi-select type): For various tags associated with the book, like
genre.
- **Page count** (Number type): To store the number of pages in the book.
- **Link** (URL type): For a link to more information about the book.
- **Russian translation** (Select type): With options like "Unknown",
"Available", etc., to indicate the availability of a Russian translation.
- **Status** (Select type): With options like "Unread", "Read", etc., to track
reading status.

Ensure each property is correctly named and configured according to the data
structure expected by the scripts.

## How to Use the Scripts

To add book metadata to your Notion database using the provided scripts, follow
these steps:

1. **Scraping Book Data**:
   - Run the `scrapper.py` script against individual Goodreads.com URLs for each
   book you wish to add. This will generate `.json` files with the book's
   metadata in the same directory as the script.
   - Alternatively, paste all goodreads urls into a text file, one per line. 
   Then pass the file name into the script instead of url. It should go through each url 
   in the file and create .json files for them.

2. **Importing to Notion**:
   - Ensure the `import_to_notion.py` script is in the same directory as the
   created `.json` files.
   - Run the `import_to_notion.py` script. It will process all `.json` files in
   the directory and upload their contents to your Notion database.
