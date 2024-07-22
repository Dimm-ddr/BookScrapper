import requests
from typing import Any
from ..interface.data_source import DataSourceInterface


class OpenLibraryAPI(DataSourceInterface):
    BASE_URL = "https://openlibrary.org/search.json"

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        params: dict[str, str] = {"q": f"isbn:{isbn}"}
        response: requests.Response = requests.get(self.BASE_URL, params=params)
        if response.status_code == 200:
            raw_data = response.json()
            compiled_data: dict[str, Any] | None = (
                self._parse_data(raw_data["docs"][0])
                if raw_data.get("numFound", 0) > 0
                else None
            )
            return {
                "source_name": "OpenLibrary",
                "raw_data": raw_data,
                "compiled_data": compiled_data,
            }
        return None

    def fetch_by_title_author(
        self, title: str, authors: set[str]
    ) -> dict[str, Any] | None:
        # Construct a query that includes the title and any of the authors
        author_query: str = " OR ".join(f"author:{author}" for author in authors)
        query: str = f"title:{title} AND ({author_query})"

        params: dict[str, str] = {"q": query}
        response: requests.Response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            raw_data = response.json()
            compiled_data = None
            if raw_data.get("numFound", 0) > 0:
                # Find the first result that matches our criteria
                for doc in raw_data["docs"]:
                    parsed_data: dict[str, Any] = self._parse_data(doc)
                    if (
                        parsed_data.get("title")
                        and set(parsed_data.get("authors", [])) & authors
                    ):
                        compiled_data = parsed_data
                        break

            return {
                "source_name": "OpenLibrary",
                "raw_data": raw_data,
                "compiled_data": compiled_data,
            }

        return None

    def _parse_data(self, data: dict[str, Any]) -> dict[str, Any]:
        # Enrich description with first_sentence if available
        description = data.get("description")
        first_sentence = data.get("first_sentence")
        if description and first_sentence and first_sentence not in description:
            description = f"{first_sentence} {description}"

        # Combine subject, person, place, and time for a richer tags field
        tags = (
            data.get("subject", [])
            + data.get("person", [])
            + data.get("place", [])
            + data.get("time", [])
        )

        # Use alternative_title if title is not available
        title = data.get("title") or data.get("alternative_title")

        # Combine author_name and author_alternative_name for a more comprehensive authors list
        authors = list(
            set(
                data.get("author_name", [])
                + data.get("author_alternative_name", [])
                + [data.get("by_statement")]
                if data.get("by_statement")
                else []
            )
        )

        # Use the median number of pages if available
        page_count = data.get("number_of_pages_median")

        publishers = data.get("publisher", [])
        if isinstance(publishers, str):
            publishers: list[str] = [publishers]

        return {
            "title": title,
            "first_publish_year": data.get("first_publish_year"),
            "link": (
                f"https://openlibrary.org{data.get('key')}" if data.get("key") else None
            ),
            "description": description,
            "cover": (
                f"https://covers.openlibrary.org/b/id/{data.get('cover_i')}-L.jpg"
                if data.get("cover_i")
                else None
            ),
            "page_count": page_count,
            "editions_count": data.get("edition_count"),
            "isbn": (
                data.get("isbn", [None])[0]
                if isinstance(data.get("isbn"), list)
                else data.get("isbn")
            ),
            "authors": authors,
            "languages": data.get("language", []),
            "tags": tags,
            "publishers": publishers,
            # OpenLibrary doesn't provide series information
            "series": None,
        }
