#!/usr/bin/env python3
"""Map original annotation IDs to canonical BENI v1 article IDs."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
BUILDER_PATH = REPO_ROOT / "BENI_v1_data_paper" / "scripts" / "build_beni_v1_articles.py"
BNAD_DIR = REPO_ROOT / "BENI_v1_data_paper" / "data" / "raw" / "bnad"
LOCKED_LABELS = ROOT / "data" / "annotations" / "beni_v0_1_annotations_locked.jsonl"
OUT_MAP = ROOT / "data" / "annotations" / "beni_v1_reference_label_corpus_map.csv"
OUT_SUMMARY = ROOT / "data" / "annotations" / "beni_v1_reference_label_corpus_map_summary.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("beni_v1_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import builder from {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_labels() -> list[dict]:
    rows = []
    with LOCKED_LABELS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> None:
    builder = load_builder()
    labels = read_labels()
    targets = {(row["source_file"], int(row["source_line"])) for row in labels}
    label_by_key = {(row["source_file"], int(row["source_line"])): row for row in labels}

    matches: dict[tuple[str, int], dict] = {}
    bnad_idx = 0
    for path in sorted(BNAD_DIR.glob("*.jsonl")):
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for source_line, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                obj = json.loads(line)
                date = builder.parse_bangla_date(obj.get("Time"))
                text = obj.get("Content") or ""
                if not date or int(date[:4]) <= 2020:
                    continue
                if len(builder.clean_text(text)) < 50:
                    continue
                bnad_idx += 1
                key = (path.name, source_line)
                if key not in targets:
                    continue
                label = label_by_key[key]
                raw_title = builder.clean_text(obj.get("Title") or "")
                raw_text = builder.clean_text(text)
                label_text = builder.clean_text(label.get("text") or "")
                matches[key] = {
                    "original_article_id": label["article_id"],
                    "canonical_article_id": f"bnad_{bnad_idx:09d}",
                    "source_file": path.name,
                    "source_line": source_line,
                    "publication_date": date,
                    "newspaper": path.stem,
                    "label_title": label.get("title") or "",
                    "raw_title": raw_title,
                    "title_match": str((label.get("title") or "") == raw_title).lower(),
                    "label_text_starts_with_title": str(label_text.startswith(raw_title)).lower(),
                    "raw_text_prefix_in_label_text": str(raw_text[:120] in label_text).lower(),
                    "final_label": label.get("final_label"),
                    "confidence": label.get("confidence"),
                    "annotation_status": label.get("annotation_status"),
                }

    fieldnames = [
        "original_article_id",
        "canonical_article_id",
        "source_file",
        "source_line",
        "publication_date",
        "newspaper",
        "label_title",
        "raw_title",
        "title_match",
        "label_text_starts_with_title",
        "raw_text_prefix_in_label_text",
        "final_label",
        "confidence",
        "annotation_status",
    ]
    with OUT_MAP.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in sorted(matches):
            writer.writerow(matches[key])

    unmatched = sorted(targets - set(matches))
    summary = {
        "labels": len(labels),
        "mapped": len(matches),
        "unmatched": len(unmatched),
        "unmatched_keys": [{"source_file": k[0], "source_line": k[1]} for k in unmatched],
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_MAP}")
    print(f"Wrote {OUT_SUMMARY}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
