from __future__ import annotations

"""
Export Potrika or BNLP articles for LabelStudio annotation.

Usage (BNLP sample — runnable now):
    python3 export_for_labelstudio.py --source bnlp --output exports/bnlp_sample.json

Usage (Potrika — needs raw CSVs from Kaggle/Dropbox):
    python3 export_for_labelstudio.py --source potrika --potrika-dir /path/to/potrika --output exports/potrika_sample.json
"""

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

import pandas as pd

random.seed(42)

# ── Label mapping ───────────────────────────────────────────────────
# These are used by the dataset loading code.
# Keyword-based economic relevance heuristic (mirrors config.py)
ECONOMIC_KEYWORDS = [
    "অর্থনীতি", "অর্থনৈতিক", "মুদ্রাস্ফীতি", "মূল্যস্ফীতি",
    "ভোক্তা মূল্য", "খাদ্য মূল্য", "ডলার", "বৈদেশিক মুদ্রা",
    "রিজার্ভ", "বাংলাদেশ ব্যাংক", "সোনালী ব্যাংক", "জনতা ব্যাংক",
    "অগ্রণী ব্যাংক", "রূপালী ব্যাংক", "বাণিজ্য", "রপ্তানি",
    "আমদানি", "শিল্পোৎপাদন", "জিডিপি", "মোট দেশজ উৎপাদন",
    "শেয়ারবাজার", "পুঁজিবাজার", "বিনিয়োগ", "প্রবাসী আয়",
    "রেমিট্যান্স", "বাজেট", "অর্থমন্ত্রী", "টাকার বিনিময় হার",
    "বিনিময় হার", "সুদের হার", "সঞ্চয়পত্র", "ব্যাংক", "ঋণ",
    "কৃষি", "ফসল", "উৎপাদন", "সরকারি বন্ড", "টানা বাজেট",
]


def _keyword_match(text: str) -> int:
    """Check if any economic keyword appears in the text."""
    text_lower = text.lower()
    for kw in ECONOMIC_KEYWORDS:
        if kw in text_lower:
            return 1
    return 0


def load_bnlp_news_categorization(data_dir: Path) -> pd.DataFrame:
    """Load BNLP news_categorization TSVs — 3 splits, ~14k articles."""
    records = []
    for split in ("train", "dev", "test"):
        path = data_dir / f"{split}.tsv"
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            if header != ["id", "text", "class_label"]:
                continue
            for row in reader:
                if len(row) < 3:
                    continue
                text = " ".join(row[1:-1]).strip()
                topic = row[-1].strip().lower()
                if not text or not topic:
                    continue
                records.append({
                    "id": f"bnlp_{split}_{row[0]}",
                    "text": text,
                    "topic": topic,
                    "source": "bnlp_news_categorization",
                    "split": split,
                })
    if not records:
        raise ValueError(f"No records loaded from {data_dir}")
    frame = pd.DataFrame.from_records(records)
    frame["economic_relevance_keyword"] = frame["text"].map(_keyword_match)
    return frame


def load_potrika_sample(potrika_dir: Path, n_per_category: int = 200) -> pd.DataFrame:
    """
    Load raw Potrika CSVs and return a balanced multi-category sample.
    Requires the full Potrika dataset (3.3 GB from Mendeley).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiment" / "beni_pilot"))
    from data import load_potrika_binary_timeseries
    from config import ExperimentConfig

    cfg = ExperimentConfig(potrika_dir=potrika_dir)
    frame = load_potrika_binary_timeseries(potrika_dir)
    categories = frame["category"].unique()

    chunks = []
    for cat in categories:
        subset = frame[frame["category"].str.lower() == cat.lower()]
        if len(subset) > n_per_category:
            subset = subset.sample(n=n_per_category, random_state=42)
        chunks.append(subset)

    result = pd.concat(chunks, ignore_index=True)
    result = result.rename(columns={"economic_relevance": "economic_relevance_keyword"})
    result["source"] = "potrika"
    result["id"] = [f"potrika_{i}" for i in range(len(result))]
    result["topic"] = result["category"].str.lower()
    return result


def to_labelstudio_json(
    frame: pd.DataFrame,
    n_total: int | None = None,
    economic_ratio: float = 0.4,
) -> list[dict[str, Any]]:
    """
    Convert dataframe to LabelStudio JSON import format.

    Produces a stratified sample: ~economic_ratio proportion economically relevant,
    rest not, so the annotator sees a realistic class balance.
    """
    # Stratified sample
    econ = frame[frame["economic_relevance_keyword"] == 1]
    non_econ = frame[frame["economic_relevance_keyword"] == 0]

    n_econ = min(len(econ), int(n_total * economic_ratio) if n_total else len(econ))
    n_non = min(len(non_econ), n_total - n_econ if n_total else len(non_econ))

    sampled = pd.concat([
        econ.sample(n=n_econ, random_state=42) if n_econ > 0 else pd.DataFrame(),
        non_econ.sample(n=n_non, random_state=42) if n_non > 0 else pd.DataFrame(),
    ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

    tasks = []
    for _, row in sampled.iterrows():
        tasks.append({
            "id": row["id"],
            "data": {
                "text": row["text"][:5000],  # clip to 5k chars for readability
                "topic": row["topic"],
                "keyword_label": int(row["economic_relevance_keyword"]),
                "source": row["source"],
            },
        })
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["bnlp", "potrika"], default="bnlp")
    parser.add_argument("--potrika-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("exports") / "annotation_sample.json")
    parser.add_argument("--n", type=int, default=200, help="Total articles to export")
    parser.add_argument("--econ-ratio", type=float, default=0.4, help="Target economic ratio")
    args = parser.parse_args()

    if args.source == "bnlp":
        data_dir = Path(__file__).resolve().parents[2] / "beni" / "experiment" / "bnlp-resources" / "news_categorization"
        frame = load_bnlp_news_categorization(data_dir)
    else:
        if args.potrika_dir is None:
            raise ValueError("--potrika-dir is required when --source=potrika")
        frame = load_potrika_sample(Path(args.potrika_dir))

    print(f"Loaded {len(frame)} articles ({frame['economic_relevance_keyword'].value_counts().to_dict()})")

    tasks = to_labelstudio_json(frame, n_total=args.n, economic_ratio=args.econ_ratio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(tasks)} tasks → {args.output}")


if __name__ == "__main__":
    main()
