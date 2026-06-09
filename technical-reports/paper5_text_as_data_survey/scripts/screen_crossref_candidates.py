from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PAPER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PAPER_ROOT / "data" / "crossref_candidate_papers.csv"
DEFAULT_OUTPUT = PAPER_ROOT / "data" / "crossref_screening_queue.csv"

HIGH_VALUE_TERMS = [
    "text as data",
    "automated text analysis",
    "computational text analysis",
    "content analysis",
    "structural topic model",
    "topic model",
    "large language model",
    "chatgpt",
    "liwc",
    "economic policy uncertainty",
    "news sentiment",
    "political text",
    "social science",
    "computational social science",
]

LOW_VALUE_TERMS = [
    "social text",  # journal title false positive
    "job advertisements",
    "book review",
    "review of ",
    "current approaches in social sciences",
]


def score_row(row: pd.Series) -> int:
    blob = " ".join(str(row.get(col, "")) for col in ["title", "container", "source_query"]).lower()
    score = 0
    for term in HIGH_VALUE_TERMS:
        if term in blob:
            score += 3
    for term in LOW_VALUE_TERMS:
        if term in blob:
            score -= 5
    try:
        cites = int(float(row.get("citation_count_crossref", 0)))
    except (TypeError, ValueError):
        cites = 0
    if cites >= 500:
        score += 4
    elif cites >= 100:
        score += 3
    elif cites >= 25:
        score += 2
    if row.get("type") in {"journal-article", "book", "book-chapter", "proceedings-article", "posted-content"}:
        score += 1
    if pd.isna(row.get("year")):
        score -= 1
    return score


def recommendation(score: int) -> str:
    if score >= 8:
        return "screen_first"
    if score >= 4:
        return "screen_second"
    return "screen_later_or_exclude"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank Crossref candidates for Paper 5 screening")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df["relevance_score"] = df.apply(score_row, axis=1)
    df["screening_priority"] = df["relevance_score"].map(recommendation)
    df = df.sort_values(["relevance_score", "citation_count_crossref"], ascending=[False, False])
    df.to_csv(args.output, index=False)
    print(f"Wrote ranked screening queue: {args.output}")
    print(df["screening_priority"].value_counts().to_string())


if __name__ == "__main__":
    main()
