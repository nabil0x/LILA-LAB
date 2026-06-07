#!/usr/bin/env python3
"""Build the preliminary BENI v1 unified article corpus.

The merge follows docs/MERGE_PLAN.md:

- Potrika dated raw files for 2014-2020.
- BNAD JSONL files after 2020.
- Potrika balanced *_40k.csv files and BNAD pre-2021 rows are excluded from
  the main merged panel.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
POTRIKA_DIR = ROOT / "data" / "raw" / "potrika"
DEFAULT_BNAD_DIRS = [
    ROOT / "data" / "raw" / "bnad",
    REPO_ROOT / "beni" / "Bangla_News_Database",
]
OUT_DIR = ROOT / "data" / "processed"

BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
BN_MONTHS = {
    "জানুয়ারি": 1,
    "জানুয়ারি": 1,
    "ফেব্রুয়ারি": 2,
    "ফেব্রুয়ারি": 2,
    "মার্চ": 3,
    "এপ্রিল": 4,
    "মে": 5,
    "জুন": 6,
    "জুলাই": 7,
    "আগস্ট": 8,
    "সেপ্টেম্বর": 9,
    "অক্টোবর": 10,
    "নভেম্বর": 11,
    "ডিসেম্বর": 12,
}

FIELDNAMES = [
    "article_id",
    "dataset_source",
    "source_file",
    "newspaper",
    "publication_date",
    "year_month",
    "category_original",
    "category_harmonised",
    "headline",
    "text",
    "text_clean",
    "tags",
    "meta",
    "language",
    "text_hash",
    "headline_date_hash",
    "is_duplicate",
    "duplicate_group_id",
    "economic_seed_label",
    "economic_probability",
    "economic_prediction",
    "model_version",
    "release_version",
]


def parse_bangla_date(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.translate(BN_DIGITS)
    text = re.sub(r"^(প্রকাশ|প্রকাশিত|আপডেট)\s*:\s*", "", text).strip()
    text = text.split("|")[0].strip()
    text = text.replace(",", " ")
    text = re.sub(r"\s+", " ", text)

    iso_match = re.search(r"(20\d{2}|19\d{2})[-/](\d{1,2})[-/](\d{1,2})", text)
    if iso_match:
        y, m, d = map(int, iso_match.groups())
        return safe_iso_date(y, m, d)

    for month_name, month in BN_MONTHS.items():
        pattern = rf"(\d{{1,2}})\s+{re.escape(month_name)}\s+(20\d{{2}}|19\d{{2}})"
        match = re.search(pattern, text)
        if match:
            return safe_iso_date(int(match.group(2)), month, int(match.group(1)))
    return None


def safe_iso_date(year: int, month: int, day: int) -> str | None:
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return None


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\ufeff", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def digest(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def classify_harmonised_category(category: object) -> str:
    raw = ("" if category is None else str(category)).strip().lower()
    if any(k in raw for k in ["economy", "business", "finance", "stock"]):
        return "economy"
    if any(k in raw for k in ["অর্থ", "অর্থনীতি", "বাণিজ্য", "ব্যবসা", "ফাইন্যান্স", "শেয়ার", "শেয়ার", "বাজার"]):
        return "economy"
    if "politic" in raw or "রাজনীতি" in raw:
        return "politics"
    if any(k in raw for k in ["national", "bangladesh", "country", "state", "local"]):
        return "national"
    if any(k in raw for k in ["বাংলাদেশ", "জাতীয়", "জাতীয়", "দেশ", "সারাদেশ", "রাজধানী", "নগর", "বাংলারজমিন"]):
        return "national"
    if any(k in raw for k in ["world", "international", "আন্তর্জাতিক", "বিশ্ব"]):
        return "international"
    if any(k in raw for k in ["sport", "খেলা", "ক্রীড়া", "ক্রীড়া", "খেলাধুলা"]):
        return "sports"
    if "education" in raw or "শিক্ষা" in raw:
        return "education"
    if "entertainment" in raw or "বিনোদন" in raw:
        return "entertainment"
    if any(k in raw for k in ["technology", "science", "tech", "প্রযুক্তি", "বিজ্ঞান"]):
        return "technology_science"
    if "স্বাস্থ্য" in raw:
        return "health"
    return "other_or_unknown"


def infer_source_from_filename(name: str) -> str:
    low = name.lower()
    if "__" in name:
        return name.split("__", 1)[0]
    for source in ["ittefaq", "jugantor", "jaijaidin", "kaler_kontho", "somoyer_alo"]:
        if low.startswith(source):
            return source
    return "balanced_category_file"


def infer_category_from_filename(name: str) -> str:
    stem = Path(name).stem.lower()
    if "economy" in stem:
        return "economy"
    if "national" in stem:
        return "national"
    if "politics" in stem:
        return "politics"
    if "worldnews" in stem or "international" in stem:
        return "international"
    if "sports" in stem:
        return "sports"
    if "education" in stem:
        return "education"
    if "entertainment" in stem:
        return "entertainment"
    if "science" in stem:
        return "technology_science"
    return stem


def economic_seed_label(category_harmonised: str) -> str:
    if category_harmonised == "economy":
        return "positive"
    if category_harmonised in {"sports", "entertainment"}:
        return "negative"
    return "ambiguous"


def make_article(
    article_id: str,
    dataset_source: str,
    source_file: str,
    newspaper: str,
    publication_date: str,
    category_original: object,
    headline: object,
    text: object,
    tags: object = "",
    meta: object = "",
) -> dict:
    text_clean = clean_text(text)
    headline_clean = clean_text(headline)
    category_h = classify_harmonised_category(category_original)
    return {
        "article_id": article_id,
        "dataset_source": dataset_source,
        "source_file": source_file,
        "newspaper": newspaper,
        "publication_date": publication_date,
        "year_month": publication_date[:7],
        "category_original": clean_text(category_original),
        "category_harmonised": category_h,
        "headline": headline_clean,
        "text": clean_text(text),
        "text_clean": text_clean,
        "tags": clean_text(tags),
        "meta": clean_text(meta),
        "language": "bn",
        "text_hash": digest(text_clean),
        "headline_date_hash": digest(f"{publication_date}|{headline_clean}"),
        "is_duplicate": "false",
        "duplicate_group_id": "",
        "economic_seed_label": economic_seed_label(category_h),
        "economic_probability": "",
        "economic_prediction": "",
        "model_version": "",
        "release_version": "BENI_unified_v1.0_preliminary",
    }


def iter_potrika_articles(min_chars: int) -> Iterable[dict]:
    idx = 0
    for path in sorted(POTRIKA_DIR.glob("*.csv")):
        if path.name.endswith("_40k.csv"):
            continue
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = parse_bangla_date(row.get("Date") or row.get("publication_date") or row.get("date"))
                if not date or not (2014 <= int(date[:4]) <= 2020):
                    continue
                text = row.get("News") or row.get("article") or row.get("Content") or ""
                if len(clean_text(text)) < min_chars:
                    continue
                idx += 1
                category = row.get("Category") or row.get("category") or infer_category_from_filename(path.name)
                yield make_article(
                    article_id=f"potrika_{idx:09d}",
                    dataset_source="potrika",
                    source_file=path.name,
                    newspaper=row.get("Source") or row.get("source") or infer_source_from_filename(path.name),
                    publication_date=date,
                    category_original=category,
                    headline=row.get("Heading") or row.get("Title") or "",
                    text=text,
                )


def iter_bnad_articles(bnad_dir: Path, min_chars: int) -> Iterable[dict]:
    idx = 0
    for path in sorted(bnad_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                date = parse_bangla_date(obj.get("Time"))
                if not date or int(date[:4]) <= 2020:
                    continue
                text = obj.get("Content") or ""
                if len(clean_text(text)) < min_chars:
                    continue
                idx += 1
                yield make_article(
                    article_id=f"bnad_{idx:09d}",
                    dataset_source="bnad",
                    source_file=path.name,
                    newspaper=path.stem,
                    publication_date=date,
                    category_original=obj.get("Category") or "",
                    headline=obj.get("Title") or "",
                    text=text,
                    tags=obj.get("Tags") or "",
                    meta=obj.get("Meta") or "",
                )


def write_articles(path: Path, rows: Iterable[dict]) -> Counter:
    counts = Counter()
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            counts["rows"] += 1
            counts[f"source:{row['dataset_source']}"] += 1
            counts[f"year:{row['publication_date'][:4]}"] += 1
            counts[f"category:{row['category_harmonised']}"] += 1
    return counts


def dedupe_csv(input_path: Path, output_path: Path) -> Counter:
    seen: dict[str, str] = {}
    duplicate_groups: dict[str, str] = {}
    group_idx = 0
    counts = Counter()
    with input_path.open("r", encoding="utf-8", newline="") as src, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in reader:
            text_hash = row["text_hash"]
            if text_hash in seen:
                if text_hash not in duplicate_groups:
                    group_idx += 1
                    duplicate_groups[text_hash] = f"dup_{group_idx:09d}"
                row["is_duplicate"] = "true"
                row["duplicate_group_id"] = duplicate_groups[text_hash]
                counts["duplicate_rows"] += 1
            else:
                seen[text_hash] = row["article_id"]
            writer.writerow(row)
            counts["rows"] += 1
    counts["unique_text_hashes"] = len(seen)
    counts["duplicate_groups"] = len(duplicate_groups)
    return counts


def resolve_bnad_dir(value: str | None) -> Path:
    candidates = [Path(value)] if value else DEFAULT_BNAD_DIRS
    for candidate in candidates:
        if candidate.exists() and any(candidate.glob("*.jsonl")):
            return candidate
    checked = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"No BNAD JSONL files found. Checked: {checked}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bnad-dir", default=None, help="Directory containing BNAD *.jsonl files.")
    parser.add_argument("--min-chars", type=int, default=50, help="Drop articles with shorter cleaned text.")
    args = parser.parse_args()

    bnad_dir = resolve_bnad_dir(args.bnad_dir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    potrika_path = OUT_DIR / "potrika_articles_canonical.csv"
    bnad_path = OUT_DIR / "bnad_articles_canonical.csv"
    merged_path = OUT_DIR / "beni_unified_articles.csv"
    deduped_path = OUT_DIR / "beni_unified_articles_deduped.csv"
    summary_path = OUT_DIR / "beni_unified_articles_summary.json"

    potrika_counts = write_articles(potrika_path, iter_potrika_articles(args.min_chars))
    bnad_counts = write_articles(bnad_path, iter_bnad_articles(bnad_dir, args.min_chars))

    def merged_rows() -> Iterable[dict]:
        for path in [potrika_path, bnad_path]:
            with path.open("r", encoding="utf-8", newline="") as f:
                yield from csv.DictReader(f)

    merged_counts = write_articles(merged_path, merged_rows())
    dedupe_counts = dedupe_csv(merged_path, deduped_path)

    summary = {
        "release_version": "BENI_unified_v1.0_preliminary",
        "merge_rule": "Potrika dated 2014-2020 plus BNAD post-2020.",
        "potrika_dir": str(POTRIKA_DIR),
        "bnad_dir": str(bnad_dir),
        "min_chars": args.min_chars,
        "outputs": {
            "potrika_canonical": str(potrika_path),
            "bnad_canonical": str(bnad_path),
            "merged": str(merged_path),
            "deduped": str(deduped_path),
        },
        "potrika_counts": dict(potrika_counts),
        "bnad_counts": dict(bnad_counts),
        "merged_counts": dict(merged_counts),
        "dedupe_counts": dict(dedupe_counts),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
