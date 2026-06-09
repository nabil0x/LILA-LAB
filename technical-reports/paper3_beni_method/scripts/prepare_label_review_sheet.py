#!/usr/bin/env python3
"""Prepare a human-review sheet for unresolved Paper 3 labels."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_QUEUE = ROOT / "data" / "annotations" / "beni_v0_1_review_queue.csv"
OUT_SHEET = ROOT / "data" / "annotations" / "beni_v1_label_review_decisions.csv"


FIELDNAMES = [
    "article_id",
    "current_label",
    "confidence",
    "difficulty",
    "category",
    "title",
    "text_preview",
    "review_decision",
    "reviewed_label",
    "exclude_from_validation",
    "review_notes",
]


def main() -> None:
    with IN_QUEUE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    output_rows = []
    for row in rows:
        output_rows.append(
            {
                "article_id": row.get("article_id", ""),
                "current_label": row.get("final_label", ""),
                "confidence": row.get("confidence", ""),
                "difficulty": row.get("difficulty", ""),
                "category": row.get("category", ""),
                "title": row.get("title", ""),
                "text_preview": row.get("text_preview", ""),
                "review_decision": "",
                "reviewed_label": "",
                "exclude_from_validation": "",
                "review_notes": "",
            }
        )

    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    with OUT_SHEET.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {OUT_SHEET}")
    print(f"Rows: {len(output_rows)}")
    print("Fill review_decision with: keep, revise, or exclude")
    print("Fill reviewed_label only when review_decision is revise")
    print("Fill exclude_from_validation with true for ambiguous rows")


if __name__ == "__main__":
    main()
