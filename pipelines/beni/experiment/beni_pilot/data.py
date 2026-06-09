from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from config import ECONOMIC_KEYWORDS, ExperimentConfig
from utils import normalize_text


def load_split(config: ExperimentConfig, split: str) -> pd.DataFrame:
    path = config.raw_data_dir / f"{split}.tsv"
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset split: {path}")

    records = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if header != ["id", "text", "class_label"]:
            raise ValueError(f"Unexpected header in {path}: {header}")
        for row in reader:
            if len(row) < 3:
                continue
            records.append(
                {
                    "id": row[0],
                    "text": " ".join(row[1:-1]),
                    "class_label": row[-1],
                }
            )

    frame = pd.DataFrame.from_records(records)
    frame = frame.dropna(subset=["text", "class_label"])
    frame["class_label"] = frame["class_label"].astype(str).str.strip()
    frame = frame[frame["class_label"] != ""].copy()
    frame["text_norm"] = frame["text"].map(normalize_text)
    return frame


def load_all_splits(config: ExperimentConfig) -> dict[str, pd.DataFrame]:
    return {split: load_split(config, split) for split in ("train", "dev", "test")}


def add_economic_relevance_label(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    pattern = "|".join(map(lambda word: word.replace("+", "\\+"), ECONOMIC_KEYWORDS))
    frame["economic_relevance"] = frame["text_norm"].str.contains(pattern, regex=True).astype(int)
    return frame


def describe_splits(splits: dict[str, pd.DataFrame]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for split, frame in splits.items():
        econ = add_economic_relevance_label(frame)
        summary[split] = {
            "rows": int(len(frame)),
            "topic_labels": {k: int(v) for k, v in frame["class_label"].value_counts().to_dict().items()},
            "economic_relevance": {
                str(k): int(v) for k, v in econ["economic_relevance"].value_counts().to_dict().items()
            },
        }
    return summary


def save_sample(frame: pd.DataFrame, path: Path, n: int = 20) -> None:
    cols = ["id", "class_label", "economic_relevance", "text"]
    frame.head(n)[cols].to_csv(path, index=False)


# ── Potrika data loaders ──────────────────────────────────────────────────

def load_potrika_export(path: Path) -> pd.DataFrame:
    """Load pre-exported potrika_economy.csv (balanced 40k Economy articles)."""
    if not path.exists():
        raise FileNotFoundError(
            f"Potrika export not found: {path}. "
            "Run: python3 potrika.py --category Economy"
        )
    frame = pd.read_csv(path, encoding="utf-8")
    frame["economic_relevance"] = 1  # all are Economy articles
    return frame


def _read_csv_safe(path: Path) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    return pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")


def load_potrika_raw_economy(potrika_dir: Path) -> pd.DataFrame:
    """Load raw Potrika Economy files preserving dates and sources for time-series use."""
    if not potrika_dir.exists():
        raise FileNotFoundError(f"Potrika raw directory not found: {potrika_dir}")

    records = []
    for csv_path in sorted(potrika_dir.glob("*economy*")):
        frame = _read_csv_safe(csv_path)
        cols_lower = {c: c for c in frame.columns}
        news_col = cols_lower.get("News") or cols_lower.get("article") or cols_lower.get("text")
        date_col = cols_lower.get("Date")
        source_col = cols_lower.get("Source")
        cat_col = cols_lower.get("Category") or cols_lower.get("class")

        if news_col is None:
            continue

        row = pd.DataFrame({
            "text": frame[news_col].astype(str),
            "category": "Economy",
            "publication_date": pd.to_datetime(frame[date_col], errors="coerce") if date_col else pd.NaT,
            "source": frame[source_col].astype(str) if source_col else csv_path.stem,
            "economic_relevance": 1,
        })
        records.append(row)

    if not records:
        raise ValueError(f"No Economy CSV files found in {potrika_dir}")

    combined = pd.concat(records, ignore_index=True, sort=False)
    combined = combined.dropna(subset=["text"])
    combined["text_norm"] = combined["text"].map(normalize_text)
    combined = combined[combined["text_norm"] != ""].copy()
    return combined


def _load_raw_category(
    potrika_dir: Path,
    category_keyword: str,
    max_rows: int | None = None,
) -> pd.DataFrame:
    records = []
    for csv_path in sorted(potrika_dir.glob(f"*{category_keyword}*")):
        if "_40k" in csv_path.stem:
            continue
        frame = _read_csv_safe(csv_path)
        if max_rows is not None and len(frame) > max_rows:
            frame = frame.sample(n=max_rows, random_state=42)
        cols_lower = {c: c for c in frame.columns}
        news_col = cols_lower.get("News") or cols_lower.get("article") or cols_lower.get("text")
        date_col = cols_lower.get("Date")
        source_col = cols_lower.get("Source")

        if news_col is None:
            continue

        row = pd.DataFrame({
            "text": frame[news_col].astype(str),
            "category": category_keyword.capitalize(),
            "publication_date": pd.to_datetime(frame[date_col], errors="coerce") if date_col else pd.NaT,
            "source": frame[source_col].astype(str) if source_col else csv_path.stem,
        })
        records.append(row)

    if not records:
        return pd.DataFrame()

    combined = pd.concat(records, ignore_index=True, sort=False)
    combined = combined.dropna(subset=["text"])
    combined["text_norm"] = combined["text"].map(normalize_text)
    combined = combined[combined["text_norm"] != ""].copy()
    return combined


def load_potrika_binary_timeseries(potrika_dir: Path) -> pd.DataFrame:
    categories = {
        "economy": 1,
        "national": 0,
        "politics": 0,
        "worldnews": 0,
    }
    max_per_file = {"economy": None, "national": 5000, "politics": 5000, "worldnews": 5000}

    chunks = []
    for keyword, label in categories.items():
        chunk = _load_raw_category(potrika_dir, keyword, max_rows=max_per_file[keyword])
        if chunk.empty:
            continue
        chunk["economic_relevance"] = label
        chunks.append(chunk)

    if not chunks:
        listed = "\n  ".join(sorted(str(p.name) for p in potrika_dir.iterdir())) if potrika_dir.exists() else "(directory does not exist)"
        raise ValueError(
            f"No raw Potrika files found in {potrika_dir}\n"
            f"  Contents of {potrika_dir}:\n  {listed}"
        )

    frame = pd.concat(chunks, ignore_index=True, sort=False)
    frame = frame.dropna(subset=["publication_date"]).copy()
    frame = frame.sort_values("publication_date").reset_index(drop=True)

    econ = frame[frame["economic_relevance"] == 1]
    non_econ = frame[frame["economic_relevance"] == 0]
    target_non = min(len(non_econ), len(econ) * 3)
    if target_non < len(non_econ):
        non_econ = non_econ.sample(n=target_non, random_state=42)
        frame = pd.concat([econ, non_econ], ignore_index=True).sort_values("publication_date")
        frame = frame.reset_index(drop=True)

    return frame


def load_potrika_timeseries(config: ExperimentConfig) -> dict[str, pd.DataFrame]:
    """Load raw Potrika articles (all categories) and split by date for time-series modeling."""
    frame = load_potrika_binary_timeseries(config.potrika_dir)
    frame = frame.sort_values("publication_date").reset_index(drop=True)

    train = frame[frame["publication_date"] <= config.potrika_train_end].copy()
    val = frame[
        (frame["publication_date"] > config.potrika_train_end)
        & (frame["publication_date"] <= config.potrika_val_end)
    ].copy()
    test = frame[frame["publication_date"] > config.potrika_val_end].copy()

    return {"train": train, "val": val, "test": test, "full": frame}


def load_potrika_all_categories(potrika_dir: Path) -> pd.DataFrame:
    """Load all balanced 40k CSVs for multiclass topic classification."""
    if not potrika_dir.exists():
        raise FileNotFoundError(f"Potrika directory not found: {potrika_dir}")

    records = []
    for csv_path in sorted(potrika_dir.glob("*_40k.csv")):
        frame = _read_csv_safe(csv_path)
        article_col = None
        cat_col = None
        for c in frame.columns:
            cl = c.strip().lower()
            if cl in ("article", "text", "news"):
                article_col = c
            if cl in ("class", "category", "label"):
                cat_col = c
        if article_col is None or cat_col is None:
            continue
        row = pd.DataFrame({
            "text": frame[article_col].astype(str),
            "class_label": frame[cat_col].astype(str).str.strip(),
        })
        records.append(row)

    if not records:
        raise ValueError(f"No balanced 40k CSVs found in {potrika_dir}")

    combined = pd.concat(records, ignore_index=True, sort=False)
    combined = combined.dropna(subset=["text", "class_label"])
    combined = combined[combined["class_label"] != ""].copy()
    combined["text_norm"] = combined["text"].map(normalize_text)
    combined = combined[combined["text_norm"] != ""].copy()
    return combined
