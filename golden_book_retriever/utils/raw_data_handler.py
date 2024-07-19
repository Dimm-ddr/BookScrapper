# raw_data_handler.py
import json
from pathlib import Path
from typing import Any


def save_raw_data(
    folder_name: str, source_name: str, data: dict[str, Any] | None
) -> None:
    """
    Save raw data from a source to a JSON file.

    Args:
        folder_name (str): Name of the folder to store the data (common for all sources)
        source_name (str): Name of the data source
        data (dict[str, Any] | None): Raw data to save, or None if no data was found
    """
    base_path: Path = Path("data/books/raw_data") / folder_name
    base_path.mkdir(parents=True, exist_ok=True)

    file_path: Path = base_path / f"{source_name}.json"

    if data is None:
        data = {"status": "No data found"}

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
