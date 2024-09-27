import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
from collections import Counter

# Load environment variables from .env file
load_dotenv()

# Get the Notion secret and database ID from environment variables
notion_secret = os.getenv("NOTION_SECRET")
database_id = os.getenv("STAGING_DATABASE_ID")

# Normalization map (simplified for example)
normalization_map: dict[str, str | list[str] | None] = {
    "adult": "adult fiction",
    "adult fiction": "adult fiction",
    "adventure": "adventure",
    "alien cultures": "alien cultures",
    "american fiction": "American fiction",
    "americans": "Americans",
    "anthologies": "anthologies",
    "art": "art",
    "art and technology": ["art", "technology"],
    "asian americans": "Asian Americans",
    "audiobook": "audiobook",
    "autobiography": "autobiography",
    "biography": "biography",
    "biography memoir": ["biography", "memoir"],
    "boarding school": "boarding school",
    "boarding school & prep school": "boarding school",
    "boarding schools": "boarding school",
    "book club": "book club",
    "boys": "boys",
    "boys love": "boys love (BL)",
    "british literature": "British literature",
    "campus": "campus",
    "charlie spring": None,
    "childrens fiction": "children's fiction",
    "china": "China",
    "christmas": "christmas",
    "classics": "classics",
    "college students": "college students",
    "comic book": "graphic novels & comics",
    "comic books": "graphic novels & comics",
    "comics": "graphic novels & comics",
    "comics & graphic novels": "graphic novels & comics",
    "coming of age": "coming of age",
    "contemporary": "contemporary",
    "contemporary romance": ["contemporary", "romance"],
    "crime": "crime",
    "darius kellner": None,
    "dark fantasy": "dark fantasy",
    "depression": "mental illness",
    "desire (philosophy)": "desire",
    "detective and mystery stories": ["detective", "mystery"],
    "detroit": "Detroit",
    "detroit (mich.)": "Detroit",
    "domestic fiction": "domestic fiction",
    "dragons": "dragons",
    "english fantasy fiction": "fantasy",
    "epic fantasy": "epic fantasy",
    "essays": "essays",
    "extortion": "extortion",
    "f f romance": "female-female romance",
    "fae": "fae",
    "fairies": "fairies",
    "families": "family",
    "family": "family",
    "fantasy": "fantasy",
    "fantasy fiction": "fantasy",
    "feminism": "feminism",
    "fiction": "fiction",
    "fiction fantasy epic": "epic fantasy",
    "fiction gay": "gay",
    "fiction romance general": "romance",
    "fiction science fiction space opera": ["science fiction", "space opera"],
    "fiction short stories (single author)": "short stories",
    "friendship": "friendship",
    "friendship in youth": "friendship",
    "gay": "gay",
    "gay men": "gay",
    "gay men's writings russian": "gay's writings",
    "gay teenagers": "gay teenagers",
    "gay's writings": "gay's writings",
    "gay-parent families": "gay-parent families",
    "gays": "gay",
    "gender studies": "gender studies",
    "genderqueer": "genderqueer",
    "general": None,
    "german literature": "German literature",
    "germany": "Germany",
    "ghosts": "ghosts",
    "good and evil": "good and evil",
    "grandparents": "family",
    "graphic novels": "graphic novels & comics",
    "graphic novels comics": "graphic novels & comics",
    "high fantasy": "high fantasy",
    "high schools": "high school",
    "historical": "historical",
    "historical fiction": "historical fiction",
    "historical romance": ["historical", "romance"],
    "history": "history",
    "horror": "horror",
    "identity": "identity",
    "iran": "Iran",
    "iranian americans": "Iranian Americans",
    "isolation": "isolation",
    "juvenile fiction": "juvenile fiction",
    "lesbian": "lesbian",
    "lesbians": "lesbian",
    "lgbt": "LGBTQ+",
    "lgbt memoir": ["LGBTQ+", "memoir"],
    "lgbtq": "LGBTQ+",
    "lgbtq historical fiction": ["LGBTQ+", "historical fiction"],
    "lgbtq novels": ["LGBTQ+", "novels"],
    "lgbtq novels before stonewall": ["LGBTQ+ novels before Stonewall"],
    "lgbtq romance": ["LGBTQ+", "romance"],
    "lgbtq young adult": ["LGBTQ+", "young adult (YA)"],
    "lgbtq+": "LGBTQ+",
    "lgbtq+ activists": "LGBTQ+ activists",
    "literary collections": "literary collections",
    "literary fiction": "literary fiction",
    "literature": None,
    "love": "love",
    "love in adolescence": "love in adolescence",
    "lynn": None,
    "m f romance": "male-female romance",
    "m m romance": "male-male romance",
    "magic": "magic",
    "magical realism": "magical realism",
    "man-woman relationships": "male-female romance",
    "marriage": "marriage",
    "memoir": "memoir",
    "mental": "mental health",
    "mental depression": "mental illness",
    "mental health": "mental health",
    "mental illness": "mental illness",
    "monsters": "monsters",
    "murder": "murder",
    "mystery": "mystery",
    "new adult": "new adult (NA)",
    "new york times bestseller": "new york times bestseller",
    "nick nelson": None,
    "nonfiction": "nonfiction",
    "novella": "novels",
    "novels": "novels",
    "paranormal": "paranormal",
    "paranormal romance": ["paranormal", "romance"],
    "performing arts": "performing arts",
    "plague": "plague",
    "political intrigue": "political intrigue",
    "prep school": "prep school",
    "present day": None,
    "psychology": "mental health",
    "queer": "queer",
    "queer lit": "queer",
    "realistic fiction": "realistic fiction",
    "recreation": "recreation",
    "renaissance art": "renaissance art",
    "retellings": "retellings",
    "romance": "romance",
    "rus": "Russia",
    "russia": "Russia",
    "russian fiction": "Russian literature",
    "russian literature": "Russian literature",
    "sagas": "sagas",
    "san francisco": "San Francisco",
    "san francisco calif.": "San Francisco",
    "school": "school",
    "school & education": "school",
    "schools": "school",
    "science fiction": "science fiction",
    "science fiction fantasy": ["science fiction", "fantasy"],
    "scotland": "Scotland",
    "short stories": "short stories",
    "social commentary": "social commentary",
    "speculative fiction": "speculative fiction",
    "sports": "sports",
    "sports romance": ["sports", "romance"],
    "spy stories": "spy stories",
    "stephen kellner": None,
    "stonewall book awards": "Stonewall book awards",
    "strips": None,
    "supernatural": "supernatural",
    "suspense": "suspense",
    "technology": "technology",
    "teenage boys": ["teenage", "boys"],
    "the united states of america": "United States",
    "thrillers": "thrillers",
    "transgender": "transgender",
    "travel": "travel",
    "united states": "United States",
    "urban fantasy": "urban fantasy",
    "vampires": "vampires",
    "war": "war",
    "witches": "witches",
    "wizards & witches": ["wizards", "witches"],
    "world war ii": "world war ii",
    "ya": "young adult (YA)",
    "young adult": "young adult (YA)",
    "young adult contemporary": ["young adult (YA)", "contemporary"],
    "young adult fantasy": ["young adult (YA)", "fantasy"],
    "young adult fiction": "young adult (YA)",
    "young adult fiction / comics & graphic novels / general": [
        "young adult (YA)",
        "graphic novels & comics",
    ],
    "young adult fiction / comics & graphic novels / lgbt": [
        "young adult (YA)",
        "graphic novels & comics",
        "LGBTQ+",
    ],
    "young adult fiction / comics & graphic novels / romance": [
        "young adult (YA)",
        "graphic novels & comics",
        "romance",
    ],
}


def normalize_tag(tag, normalization_map, filename="unmatched_tags.txt"):
    """
    Normalize a tag based on the provided normalization map.
    Writes the tag to a file if it is not found in the normalization map.
    """
    lower_tag = tag.lower()
    if lower_tag in normalization_map:
        normalized = normalization_map[lower_tag]
        if normalized is None:
            return []  # Return an empty list for ignored tags
        elif isinstance(normalized, list):
            return normalized  # Return the list if multiple tags are returned
        else:
            return [normalized]  # Return as a single-item list
    else:
        # Write the unmatched tag to a file
        with open(filename, "a") as f:
            f.write(f"{tag}\n")
        return [lower_tag]  # Return the original tag if no match


def normalize_and_count_tags(books, normalization_map):
    """
    Normalize and count tag occurrences across all books.
    """
    all_tags = []
    for book in books:
        book_tags = book.get("tags", [])
        normalized_tags = set()  # Use a set to avoid duplicate tags per book
        for tag in book_tags:
            normalized_tags.update(normalize_tag(tag, normalization_map))
        all_tags.extend(normalized_tags)

    tag_counter = Counter(all_tags)
    return tag_counter


def filter_common_tags(tag_counter, total_books, threshold=0.25):
    """
    Filter out tags that appear in more than `threshold` percentage of books.
    """
    threshold_count = total_books * threshold
    return {tag: count for tag, count in tag_counter.items() if count < threshold_count}


def get_books_from_notion(notion_secret, database_id):
    """
    Fetch book data from the Notion API and return a list of books.
    """
    notion = Client(auth=notion_secret)
    books = []
    try:
        # Query the database for books
        response = notion.databases.query(database_id=database_id)

        # Ensure the response has results
        if isinstance(response, dict) and "results" in response:
            for result in response["results"]:
                properties = result.get("properties", {})
                tags = properties.get("Тэги", {}).get("multi_select", [])
                book_tags = [tag.get("name") for tag in tags]
                books.append({"tags": book_tags})
    except APIResponseError as e:
        print(f"Error querying Notion database: {e}")

    return books


# Lambda function for sorting dictionary by values (descending)
sorted_dict = lambda d: sorted(d.items(), key=lambda item: item[1], reverse=True)


def print_sorted_dict(d):
    sorted_items = sorted_dict(d)
    for tag, count in sorted_items:
        print(f"{tag}: {count}")


# Fetch books from Notion
books = get_books_from_notion(notion_secret, database_id)

# Normalize and count tags
tag_counter = normalize_and_count_tags(books, normalization_map)
total_books = len(books)

# Filter out common tags (those that appear in more than 25% of books)
filtered_tags = filter_common_tags(tag_counter, total_books, threshold=0.25)


# Output the results
print("Tag counts before filtering:")
print_sorted_dict(tag_counter)

print("\nFiltered tag counts (less than 25% occurrence):")
print_sorted_dict(filtered_tags)
