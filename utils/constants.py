import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
environment: str | None = os.getenv("ENVIRONMENT")
if environment == "TESTING":
    NOTION_DATABASE_ID: str = os.environ["TESTING_DATABASE_ID"]
elif environment == "STAGING":
    NOTION_DATABASE_ID: str = os.environ["STAGING_DATABASE_ID"]
else:
    raise ValueError("Invalid environment setting. Must be 'TESTING' or 'STAGING'.")
