#!/usr/bin/env python3
"""Apply Paper 3 label-review decisions to create a frozen reference file."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCKED_LABELS = ROOT / "data" / "annotations" / "beni_v0_1_annotations_locked.jsonl"
REVIEW_SHEET = ROOT / "data" / "annotations" / "beni_v1_label_review_decisions.csv"
CORPUS_MAP = ROOT / "data" / "annotations" / "beni_v1_reference_label_corpus_map.csv"
OUT_LABELS = ROOT / "data" / "annotations" / "beni_v1_reference_labels_frozen.jsonl"
OUT_SUMMARY = ROOT / "data" / "annotations" / "beni_v1_reference_labels_frozen_summary.json"

VALID_DECISIONS = {"", "keep", "revise", "exclude"}
VALID_LABELS = {"Economic", "Not Economic"}


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def read_review_sheet(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    decisions = {}
    errors = []
    for i, row in enumerate(rows, start=2):
        article_id = row.get("article_id", "")
        decision = (row.get("review_decision") or "").strip().lower()
        reviewed_label = (row.get("reviewed_label") or "").strip()
        exclude_text = (row.get("exclude_from_validation") or "").strip().lower()
        if decision not in VALID_DECISIONS:
            errors.append(f"line {i}: invalid review_decision {decision!r}")
        if reviewed_label and reviewed_label not in VALID_LABELS:
            errors.append(f"line {i}: invalid reviewed_label {reviewed_label!r}")
        if exclude_text not in {"", "true", "false"}:
            errors.append(f"line {i}: invalid exclude_from_validation {exclude_text!r}")
        if decision == "revise" and not reviewed_label:
            errors.append(f"line {i}: revise requires reviewed_label")
        if article_id in decisions:
            errors.append(f"line {i}: duplicate article_id {article_id}")
        decisions[article_id] = {
            "review_decision": decision,
            "reviewed_label": reviewed_label,
            "exclude_from_validation": exclude_text == "true" or decision == "exclude",
            "review_notes": row.get("review_notes", ""),
        }
    if errors:
        raise SystemExit("\n".join(errors))
    return decisions


def read_corpus_map(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["original_article_id"]: row for row in rows}


def main() -> None:
    labels = read_jsonl(LOCKED_LABELS)
    decisions = read_review_sheet(REVIEW_SHEET)
    corpus_map = read_corpus_map(CORPUS_MAP)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    output = []
    unresolved = []
    for record in labels:
        article_id = record["article_id"]
        mapped = corpus_map.get(article_id, {})
        decision = decisions.get(article_id, {})
        review_decision = decision.get("review_decision", "")
        reviewed_label = decision.get("reviewed_label", "")
        exclude_from_validation = bool(decision.get("exclude_from_validation", False))

        needs_review = record.get("annotation_status") == "needs_review" or record.get("confidence") == 2
        if needs_review and not review_decision:
            unresolved.append(article_id)

        final_label = record.get("final_label")
        if review_decision == "revise":
            final_label = reviewed_label

        include_in_clean_validation = not exclude_from_validation and not (needs_review and not review_decision)
        output.append(
            {
                "dataset_version": "BENI_v1_reference_frozen",
                "original_article_id": article_id,
                "canonical_article_id": mapped.get("canonical_article_id"),
                "title": record.get("title"),
                "text": record.get("text"),
                "source": record.get("source"),
                "source_file": record.get("source_file"),
                "source_line": record.get("source_line"),
                "category": record.get("category"),
                "publication_raw": record.get("publication_raw"),
                "final_label": final_label,
                "original_label": record.get("final_label"),
                "confidence": record.get("confidence"),
                "difficulty": record.get("difficulty"),
                "annotation_status": record.get("annotation_status"),
                "annotation_method": record.get("annotation_method"),
                "canonical_publication_date": mapped.get("publication_date"),
                "corpus_title_match": mapped.get("title_match"),
                "corpus_raw_text_prefix_in_label_text": mapped.get("raw_text_prefix_in_label_text"),
                "review_decision": review_decision,
                "reviewed_label": reviewed_label,
                "review_notes": decision.get("review_notes", ""),
                "requires_human_review": needs_review,
                "exclude_from_validation": exclude_from_validation,
                "include_in_clean_validation": include_in_clean_validation,
                "frozen_at": generated_at,
            }
        )

    with OUT_LABELS.open("w", encoding="utf-8") as f:
        for record in output:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "dataset_version": "BENI_v1_reference_frozen",
        "generated_at": generated_at,
        "n": len(output),
        "label_counts": dict(Counter(r["final_label"] for r in output)),
        "review_decision_counts": dict(Counter(r["review_decision"] or "unreviewed" for r in output)),
        "include_in_clean_validation_counts": dict(
            Counter(str(r["include_in_clean_validation"]).lower() for r in output)
        ),
        "unresolved_review_rows": len(unresolved),
        "canonical_id_mapped": sum(1 for r in output if r.get("canonical_article_id")),
        "unresolved_article_ids": unresolved,
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {OUT_LABELS}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Unresolved review rows: {len(unresolved)}")


if __name__ == "__main__":
    main()
