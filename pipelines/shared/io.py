"""File I/O utilities.

JSON/JSONL reading and writing, directory management, CSV loading,
and archive creation.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def ensure_dirs(*paths: Path) -> None:
    """Create directories if they don't exist."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    """Write data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def read_json(path: Path) -> Any:
    """Read data from a JSON file."""
    return json.loads(path.read_text())


def save_jsonl(data: list[dict], path: Path) -> None:
    """Write a list of dicts as JSONL (one JSON object per line)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file into a list of dicts."""
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def read_csv_safe(path: Path) -> pd.DataFrame:
    """Read a CSV file, trying multiple encodings.

    Attempts utf-8, utf-8-sig, and latin-1 in order.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    raise ValueError(f"Could not read {path} with any supported encoding")


def load_split(
    path: Path, delimiter: str = "\t", required_columns: list[str] | None = None
) -> pd.DataFrame:
    """Load a delimited data file with column validation.

    Args:
        path: Path to the data file.
        delimiter: Column delimiter (default: tab).
        required_columns: Optional list of column names that must exist.

    Returns:
        Loaded DataFrame.
    """
    df = pd.read_csv(path, delimiter=delimiter, encoding="utf-8")
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")
    return df


def zip_outputs(output_dir: Path, prefix: str = "") -> Path:
    """Create a zip archive of the output directory.

    Args:
        output_dir: Directory to zip.
        prefix: Optional prefix for the zip filename.

    Returns:
        Path to the created zip file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{prefix}_{timestamp}" if prefix else timestamp
    archive_path = output_dir.parent / name
    shutil.make_archive(str(archive_path), "zip", output_dir)
    return Path(f"{archive_path}.zip")
