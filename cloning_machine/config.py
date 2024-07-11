import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class NotionConfig(TypedDict):
    NOTION_TOKEN: str
    LIVE_PAGE_ID: str
    STAGING_PARENT_PAGE_ID: str
    DATABASE_ID: str


config: NotionConfig = {
    "NOTION_TOKEN": os.getenv("NOTION_SECRET", ""),
    "LIVE_PAGE_ID": os.getenv("LIVE_PAGE_ID", ""),
    "STAGING_PARENT_PAGE_ID": os.getenv("STAGING_PARENT_PAGE_ID", ""),
    "DATABASE_ID": os.getenv("DATABASE_ID", ""),
}

if not all(config.values()):
    raise ValueError(
        f"Missing required environment variables. Please check your .env file. Config values present: {config}"
    )
