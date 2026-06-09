from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from config import ROOT
from utils import normalize_text


DEFAULT_INPUT_DIR = ROOT / "data" / "raw" / "potrika"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "processed" / "potrika_economy.csv"


COLUMN_ALIASES = {
    "text": {
        "newsarticle",
        "news_article",
        "article",
        "content",
        "text",
        "body",
    },
    "category": {"category", "class", "label", "topic"},
    "headline": {"headline", "heading", "title"},
    "publication_date": {
        "publicationdate",
        "publication_date",
        "date",
        "published_date",
    },
    "source": {
        "newspapersource",
        "newspaper_source",
        "source",
        "newspaper",
    },
}


def _canonical_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")
    compact = normalized.replace("_", "")
    for target, aliases in COLUMN_ALIASES.items():
        if normalized in aliases or compact in aliases:
            return target
    return normalized


def _read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding="latin-1")


def iter_potrika_csvs(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.rglob("*.csv") if path.is_file())


def load_potrika(input_dir: Path = DEFAULT_INPUT_DIR) -> pd.DataFrame:
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Potrika directory not found: {input_dir}. "
            "Download Potrika from Mendeley and place BalancedDataset/RawDataset here."
        )

    records: list[pd.DataFrame] = []
    for csv_path in iter_potrika_csvs(input_dir):
        frame = _read_csv(csv_path)
        frame = frame.rename(columns={col: _canonical_name(col) for col in frame.columns})
        if "text" not in frame.columns:
            continue
        if "category" not in frame.columns:
            folder_names = {part.lower() for part in csv_path.parts}
            if "economy" in folder_names:
                frame["category"] = "Economy"
            else:
                frame["category"] = csv_path.parent.name
        frame["source_file"] = str(csv_path)
        records.append(frame)

    if not records:
        raise ValueError(f"No readable Potrika CSV files with an article/text column found in {input_dir}")

    combined = pd.concat(records, ignore_index=True, sort=False)
    keep = ["text", "category", "headline", "publication_date", "source", "source_file"]
    for column in keep:
        if column not in combined.columns:
            combined[column] = ""
    combined = combined[keep].dropna(subset=["text", "category"]).copy()
    combined["category"] = combined["category"].astype(str).str.strip()
    combined["text"] = combined["text"].astype(str)
    combined["text_norm"] = combined["text"].map(normalize_text)
    return combined[combined["text_norm"] != ""].copy()


def export_category_subset(
    input_dir: Path,
    output_path: Path,
    category: str = "Economy",
    max_rows: int | None = None,
) -> pd.DataFrame:
    frame = load_potrika(input_dir)
    subset = frame[frame["category"].str.casefold() == category.casefold()].copy()
    if max_rows is not None:
        subset = subset.head(max_rows).copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(output_path, index=False)
    return subset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Potrika category subset for BENI.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--category", default="Economy")
    parser.add_argument("--max-rows", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    subset = export_category_subset(args.input_dir, args.output, args.category, args.max_rows)
    print(f"rows={len(subset)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
