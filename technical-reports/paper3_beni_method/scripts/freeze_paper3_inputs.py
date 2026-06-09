#!/usr/bin/env python3
"""Create Paper 3 input-freeze QA artifacts.

This script does not adjudicate labels. It creates a defensible candidate
reference-label file and an input-freeze report that makes unresolved review
work explicit.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_FILE = ROOT / "data" / "processed" / "beni_unified_articles_deduped.csv.zst"
SUMMARY_FILE = ROOT / "data" / "processed" / "beni_unified_articles_summary.json"
LOCKED_LABELS = ROOT / "data" / "annotations" / "beni_v0_1_annotations_locked.jsonl"
LLM_LABELS = ROOT / "data" / "annotations" / "llm_assisted_300_annotations.jsonl"
REVIEW_QUEUE = ROOT / "data" / "annotations" / "beni_v0_1_review_queue.csv"
MODEL_COMPARISON = ROOT / "data" / "annotations" / "model_comparison.json"
CORPUS_MAP = ROOT / "data" / "annotations" / "beni_v1_reference_label_corpus_map.csv"

OUT_LABELS = ROOT / "data" / "annotations" / "beni_v1_reference_labels_candidate.jsonl"
OUT_REPORT = ROOT / "docs" / "PAPER3_INPUT_FREEZE_REPORT.md"


REQUIRED_ARTICLE_COLUMNS = [
    "article_id",
    "dataset_source",
    "source_file",
    "newspaper",
    "publication_date",
    "year_month",
    "category_harmonised",
    "headline",
    "text_clean",
    "language",
    "text_hash",
    "is_duplicate",
    "duplicate_group_id",
    "economic_seed_label",
    "release_version",
]


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_corpus_map(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["original_article_id"]: row for row in rows}


def stream_article_qa(path: Path) -> dict:
    """Stream the zstd CSV and collect cheap freeze checks."""
    proc = subprocess.Popen(["zstdcat", str(path)], stdout=subprocess.PIPE)
    if proc.stdout is None:
        raise RuntimeError("zstdcat did not provide stdout")

    text_stream = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
    reader = csv.DictReader(text_stream)

    qa = {
        "columns": reader.fieldnames or [],
        "rows_streamed": 0,
        "replacement_character_rows": 0,
        "missing_article_id": 0,
        "missing_publication_date": 0,
        "missing_text_clean": 0,
        "duplicate_article_ids": 0,
        "dataset_source_counts": Counter(),
        "year_counts": Counter(),
        "category_counts": Counter(),
        "language_counts": Counter(),
        "release_version_counts": Counter(),
        "duplicate_flag_counts": Counter(),
    }
    seen_ids: set[str] = set()

    for row in reader:
        qa["rows_streamed"] += 1
        article_id = row.get("article_id", "")
        if not article_id:
            qa["missing_article_id"] += 1
        elif article_id in seen_ids:
            qa["duplicate_article_ids"] += 1
        else:
            seen_ids.add(article_id)

        publication_date = row.get("publication_date", "")
        if not publication_date:
            qa["missing_publication_date"] += 1
        if not row.get("text_clean", ""):
            qa["missing_text_clean"] += 1
        if "\ufffd" in "".join("" if value is None else value for value in row.values()):
            qa["replacement_character_rows"] += 1

        qa["dataset_source_counts"][row.get("dataset_source", "")] += 1
        qa["year_counts"][(row.get("year_month", "") or "")[:4]] += 1
        qa["category_counts"][row.get("category_harmonised", "")] += 1
        qa["language_counts"][row.get("language", "")] += 1
        qa["release_version_counts"][row.get("release_version", "")] += 1
        qa["duplicate_flag_counts"][row.get("is_duplicate", "")] += 1

    return_code = proc.wait()
    qa["zstdcat_return_code"] = return_code
    qa["stream_completed_cleanly"] = return_code == 0
    qa["required_columns_missing"] = [
        col for col in REQUIRED_ARTICLE_COLUMNS if col not in qa["columns"]
    ]
    qa["unique_article_ids"] = len(seen_ids)
    return qa


def counter_to_dict(counter: Counter, limit: int | None = None) -> dict:
    items = counter.most_common(limit)
    return {str(k): v for k, v in items}


def build_candidate_labels() -> tuple[list[dict], dict]:
    locked = read_jsonl(LOCKED_LABELS)
    llm = read_jsonl(LLM_LABELS)
    llm_by_id = {r["id"]: r for r in llm}
    corpus_map = read_corpus_map(CORPUS_MAP)

    candidate: list[dict] = []
    mismatches: list[dict] = []
    for record in locked:
        article_id = record["article_id"]
        mapped = corpus_map.get(article_id, {})
        llm_record = llm_by_id.get(article_id)
        llm_label = None if llm_record is None else llm_record.get("economic_relevance")
        final_label = record.get("final_label")
        if llm_label is not None and llm_label != final_label:
            mismatches.append(
                {
                    "article_id": article_id,
                    "locked_final_label": final_label,
                    "llm_economic_relevance": llm_label,
                }
            )

        annotation_status = record.get("annotation_status")
        confidence = record.get("confidence")
        needs_review = annotation_status == "needs_review" or confidence == 2
        candidate.append(
            {
                "dataset_version": "BENI_v1_reference_candidate",
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
                "confidence": confidence,
                "difficulty": record.get("difficulty"),
                "annotation_status": annotation_status,
                "annotation_method": record.get("annotation_method"),
                "canonical_publication_date": mapped.get("publication_date"),
                "corpus_title_match": mapped.get("title_match"),
                "corpus_raw_text_prefix_in_label_text": mapped.get("raw_text_prefix_in_label_text"),
                "requires_human_review": needs_review,
                "include_in_clean_validation": not needs_review,
                "freeze_note": (
                    "Candidate label only; review required before final validation."
                    if needs_review
                    else "Candidate clean validation label."
                ),
            }
        )

    stats = {
        "locked_n": len(locked),
        "llm_n": len(llm),
        "locked_label_counts": Counter(r.get("final_label") for r in locked),
        "candidate_label_counts": Counter(r.get("final_label") for r in candidate),
        "status_counts": Counter(r.get("annotation_status") for r in locked),
        "confidence_counts": Counter(r.get("confidence") for r in locked),
        "difficulty_counts": Counter(r.get("difficulty") for r in locked),
        "requires_review": sum(1 for r in candidate if r["requires_human_review"]),
        "clean_validation_n": sum(1 for r in candidate if r["include_in_clean_validation"]),
        "canonical_id_mapped": sum(1 for r in candidate if r.get("canonical_article_id")),
        "llm_locked_label_mismatches": mismatches,
    }
    return candidate, stats


def read_review_queue_stats() -> dict:
    if not REVIEW_QUEUE.exists():
        return {"exists": False}
    with REVIEW_QUEUE.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {
        "exists": True,
        "rows": len(rows),
        "label_counts": Counter(r.get("final_label") for r in rows),
        "confidence_counts": Counter(r.get("confidence") for r in rows),
        "difficulty_counts": Counter(r.get("difficulty") for r in rows),
    }


def read_model_comparison_stats() -> dict:
    if not MODEL_COMPARISON.exists():
        return {"exists": False}
    data = json.loads(MODEL_COMPARISON.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    return {
        "exists": True,
        "metadata": meta,
        "ranking": data.get("ranking"),
    }


def render_report(
    article_qa: dict,
    label_stats: dict,
    review_stats: dict,
    model_stats: dict,
    summary: dict,
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    article_sha = sha256(ARTICLE_FILE)
    label_sha = sha256(OUT_LABELS)

    rows = [
        "# Paper 3 Input Freeze Report",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "## Decision",
        "",
        "This is a candidate input freeze for Paper 3. The article database can be treated as the current BENI v1 empirical base, but the reference labels should not yet be treated as final human-adjudicated labels.",
        "",
        "## Article Database",
        "",
        f"- file: `{ARTICLE_FILE.relative_to(ROOT)}`",
        f"- sha256: `{article_sha}`",
        f"- streamed rows: {article_qa['rows_streamed']:,}",
        f"- unique article IDs: {article_qa['unique_article_ids']:,}",
        f"- missing article IDs: {article_qa['missing_article_id']:,}",
        f"- duplicate article IDs: {article_qa['duplicate_article_ids']:,}",
        f"- missing publication dates: {article_qa['missing_publication_date']:,}",
        f"- missing clean text: {article_qa['missing_text_clean']:,}",
        f"- rows with replacement characters during UTF-8 streaming: {article_qa['replacement_character_rows']:,}",
        f"- zstdcat return code: {article_qa['zstdcat_return_code']}",
        f"- stream completed cleanly: {article_qa['stream_completed_cleanly']}",
        f"- missing required columns: {article_qa['required_columns_missing'] or 'none'}",
        "",
        "Counts from streamed article file:",
        "",
        f"- dataset sources: `{counter_to_dict(article_qa['dataset_source_counts'])}`",
        f"- release versions: `{counter_to_dict(article_qa['release_version_counts'])}`",
        f"- duplicate flags: `{counter_to_dict(article_qa['duplicate_flag_counts'])}`",
        f"- languages: `{counter_to_dict(article_qa['language_counts'])}`",
        f"- years: `{dict(sorted(counter_to_dict(article_qa['year_counts']).items()))}`",
        f"- top categories: `{counter_to_dict(article_qa['category_counts'], 12)}`",
        "",
        "Counts from existing summary JSON:",
        "",
        f"- release version: `{summary.get('release_version')}`",
        f"- merge rule: {summary.get('merge_rule')}",
        f"- merged rows: {summary.get('merged_counts', {}).get('rows'):,}",
        f"- duplicate rows flagged: {summary.get('dedupe_counts', {}).get('duplicate_rows'):,}",
        "",
        "Important QA note: if `stream completed cleanly` is false, this compressed CSV should not be treated as a final frozen corpus file until it is regenerated or recompressed successfully.",
        "",
        "## Reference Labels",
        "",
        f"- candidate file: `{OUT_LABELS.relative_to(ROOT)}`",
        f"- sha256: `{label_sha}`",
        f"- locked labels: {label_stats['locked_n']:,}",
        f"- LLM annotation rows: {label_stats['llm_n']:,}",
        f"- candidate label counts: `{counter_to_dict(label_stats['candidate_label_counts'])}`",
        f"- annotation status counts: `{counter_to_dict(label_stats['status_counts'])}`",
        f"- confidence counts: `{counter_to_dict(label_stats['confidence_counts'])}`",
        f"- difficulty counts: `{counter_to_dict(label_stats['difficulty_counts'])}`",
        f"- rows requiring review: {label_stats['requires_review']:,}",
        f"- clean validation rows if unresolved review rows are excluded: {label_stats['clean_validation_n']:,}",
        f"- locked-vs-LLM label mismatches: {len(label_stats['llm_locked_label_mismatches']):,}",
        f"- canonical BENI v1 IDs mapped: {label_stats['canonical_id_mapped']:,}",
        "",
        "## Review Queue",
        "",
        f"- exists: {review_stats.get('exists')}",
        f"- rows: {review_stats.get('rows', 0):,}",
        f"- label counts: `{counter_to_dict(review_stats.get('label_counts', Counter()))}`",
        f"- confidence counts: `{counter_to_dict(review_stats.get('confidence_counts', Counter()))}`",
        f"- difficulty counts: `{counter_to_dict(review_stats.get('difficulty_counts', Counter()))}`",
        "",
        "## Model-Comparison Mismatch To Resolve",
        "",
        "The candidate reference-label file has 120 Economic and 180 Not Economic labels. The existing `model_comparison.json` uses a different evaluation universe:",
        "",
        f"- model comparison metadata: `{model_stats.get('metadata', {})}`",
        "",
        "This must be reconciled before manuscript tables are final. For now, treat existing model-comparison results as calibration/prototype evidence only.",
        "",
        "## Next Actions",
        "",
        "1. Human-adjudicate or explicitly exclude the review rows.",
        "2. Decide whether Paper 3 reports the 300-row candidate label set or a stricter clean-validation subset.",
        "3. Regenerate model-comparison results from the selected frozen label set.",
        "4. Generate final article-level predictions on the streamed-clean BENI v1 article file.",
        "5. Build article-weighted and source-balanced monthly BENI v1 indices.",
    ]
    return "\n".join(rows) + "\n"


def main() -> None:
    summary = json.loads(SUMMARY_FILE.read_text(encoding="utf-8"))
    article_qa = stream_article_qa(ARTICLE_FILE)
    candidate_labels, label_stats = build_candidate_labels()
    write_jsonl(OUT_LABELS, candidate_labels)
    review_stats = read_review_queue_stats()
    model_stats = read_model_comparison_stats()
    OUT_REPORT.write_text(
        render_report(article_qa, label_stats, review_stats, model_stats, summary),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_LABELS}")
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
