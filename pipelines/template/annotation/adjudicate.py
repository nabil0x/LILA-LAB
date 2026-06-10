#!/usr/bin/env python3
"""
[X]ENI — Adjudication Script

Resolve disagreements between multiple LLM annotators or human annotators.
Produces a locked reference set of gold-standard labels.

Usage:
    python adjudicate.py --input annotations/ --method majority --output refset/

Deliverable:
    - Locked reference set with adjudicated labels
    - Adjudication report showing agreement metrics
"""

import argparse
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pipelines.shared.io import ensure_dirs, read_jsonl, save_jsonl, write_json
from pipelines.shared.stats.agreement import (
    cohens_kappa,
    fleiss_kappa,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Fields that carry metadata rather than annotation labels
_META_FIELDS = frozenset({
    "provider", "model", "error", "raw", "raw_response", "seed",
})


# ── Data loading ──────────────────────────────────────────────────────

def load_annotations(input_dir: str) -> list[dict]:
    """Load multi-annotator outputs from a directory.

    Scans the input directory for ``.jsonl`` files (one per annotator /
    model run) and extracts annotation records.

    Args:
        input_dir: Directory containing annotation JSONL files.

    Returns:
        List of records with ``article_id``, ``annotator_id``,
        ``annotations`` (dict of field → value), and metadata.

    Raises:
        FileNotFoundError: If no JSONL files are found.
    """
    dir_path = Path(input_dir)
    jsonl_files = sorted(dir_path.glob("*.jsonl"))

    if not jsonl_files:
        raise FileNotFoundError(
            f"No JSONL files found in {input_dir}"
        )

    logger.info("Found %d annotation files", len(jsonl_files))
    records: list[dict[str, Any]] = []

    for filepath in jsonl_files:
        annotator_id = filepath.stem  # filename without extension
        annotations = read_jsonl(filepath)

        for ann in annotations:
            article_id = str(ann.get("id", ""))
            # Support both flat and nested annotation formats
            llm_ann = ann.get("llm_annotation", ann)

            record: dict[str, Any] = {
                "article_id": article_id,
                "annotator_id": annotator_id,
                "annotations": {
                    k: v
                    for k, v in llm_ann.items()
                    if k not in _META_FIELDS
                },
            }
            # Preserve metadata for later use
            for meta in ("provider", "model"):
                if meta in llm_ann:
                    record[meta] = llm_ann[meta]

            records.append(record)

    logger.info(
        "Loaded %d annotations from %d annotators",
        len(records), len(jsonl_files),
    )
    return records


def group_by_article(annotations: list[dict]) -> dict[str, list[dict]]:
    """Group annotation records by article ID.

    Args:
        annotations: List of annotation records.

    Returns:
        Dictionary mapping ``article_id`` → list of records.
    """
    grouped: dict[str, list[dict]] = defaultdict(list)
    for ann in annotations:
        grouped[ann["article_id"]].append(ann)
    return dict(grouped)


# ── Agreement statistics ──────────────────────────────────────────────

def compute_interrater_agreement(
    grouped: dict[str, list[dict]],
) -> dict[str, Any]:
    """Compute inter-rater agreement metrics across all annotation fields.

    Uses Fleiss' kappa for multi-rater agreement and pairwise Cohen's
    kappa averaged across annotator pairs.

    Args:
        grouped: Dictionary mapping ``article_id`` → list of records.

    Returns:
        Agreement report with per-field statistics.
    """
    # Collect all field names present in any annotation
    all_fields: set[str] = set()
    for records in grouped.values():
        for rec in records:
            all_fields.update(rec.get("annotations", {}).keys())

    fields = sorted(all_fields - _META_FIELDS)

    report: dict[str, Any] = {
        "n_articles": len(grouped),
        "field_agreements": {},
    }

    for field in fields:
        # Build rating matrix: one row per article, one column per rater
        ratings: list[list[str]] = []
        for records in grouped.values():
            values = [
                str(rec["annotations"].get(field))
                for rec in records
                if field in rec.get("annotations", {})
            ]
            values = [v for v in values if v not in ("None", "")]
            if len(values) >= 2:
                ratings.append(values)

        n_subjects = len(ratings)
        if n_subjects < 2:
            report["field_agreements"][field] = {
                "n_subjects": n_subjects,
                "message": "Insufficient data for kappa calculation",
            }
            continue

        all_labels = sorted({l for row in ratings for l in row})
        fk = fleiss_kappa(ratings, labels=all_labels)

        # Pairwise Cohen's kappa across annotator pairs
        pairwise_kappas: list[float] = []
        n_raters = len(ratings[0]) if ratings else 0
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                y1 = [r[i] for r in ratings if len(r) > i and len(r) > j]
                y2 = [r[j] for r in ratings if len(r) > i and len(r) > j]
                if len(y1) >= 2:
                    ck = cohens_kappa(y1, y2)
                    pairwise_kappas.append(ck["kappa"])

        report["field_agreements"][field] = {
            "n_subjects": fk["n_subjects"],
            "n_raters": fk["n_raters"],
            "fleiss_kappa": fk["kappa"],
            "observed_agreement": fk["observed_agreement"],
            "expected_agreement": fk["expected_agreement"],
            "mean_pairwise_cohens_kappa": (
                round(sum(pairwise_kappas) / len(pairwise_kappas), 4)
                if pairwise_kappas
                else None
            ),
        }

    return report


# ── Adjudication methods ──────────────────────────────────────────────

def majority_vote(annotations: list[dict]) -> dict[str, Any]:
    """Resolve annotation disagreements by simple majority voting.

    For each field the most frequent value among annotators is chosen.
    Ties are broken by selecting the value with the higher mean confidence
    (if a confidence field exists) or by picking the first tied value.

    Args:
        annotations: Annotation records for a single article.

    Returns:
        Dictionary with ``adjudicated_labels``, per-field ``agreement``
        info, and the ``method`` name.
    """
    if not annotations:
        return {"adjudicated_labels": {}, "agreement": {}, "method": "majority_vote"}

    # Collect values per field
    field_values: dict[str, list[Any]] = defaultdict(list)
    for ann in annotations:
        ann_data = ann.get("annotations", {})
        for key, value in ann_data.items():
            if key not in _META_FIELDS:
                field_values[key].append(value)

    adjudicated: dict[str, Any] = {}
    agreement_info: dict[str, Any] = {}

    # Locate confidence field if any
    confidence_field: str | None = next(
        (f for f in field_values if "confidence" in f.lower()),
        None,
    )

    for field, values in field_values.items():
        valid = [v for v in values if v is not None and v != ""]
        if not valid:
            adjudicated[field] = None
            agreement_info[field] = {"n_votes": 0, "agreement_ratio": 0.0}
            continue

        counter = Counter(valid)
        most_common = counter.most_common()
        top_value, top_count = most_common[0]

        # Tie-breaking
        if len(most_common) > 1 and most_common[1][1] == top_count:
            tied_values = {v for v, c in most_common if c == top_count}
            if confidence_field and confidence_field in field_values:
                # Choose the tied value with the highest average confidence
                confidence_scores: dict[Any, list[float]] = defaultdict(list)
                for ann in annotations:
                    ad = ann.get("annotations", {})
                    val = ad.get(field)
                    conf = ad.get(confidence_field)
                    if val in tied_values and conf is not None:
                        confidence_scores[val].append(float(conf))
                if confidence_scores:
                    top_value = max(
                        confidence_scores,
                        key=lambda v: (
                            sum(confidence_scores[v]) / len(confidence_scores[v])
                        ),
                    )

        adjudicated[field] = top_value
        agreement_info[field] = {
            "n_votes": len(valid),
            "agreement_ratio": round(top_count / len(valid), 4),
            "vote_distribution": dict(counter),
        }

    ratios = [
        info["agreement_ratio"]
        for info in agreement_info.values()
        if info["n_votes"] > 0
    ]
    mean_agreement = round(sum(ratios) / len(ratios), 4) if ratios else 0.0

    return {
        "adjudicated_labels": adjudicated,
        "agreement": agreement_info,
        "mean_field_agreement": mean_agreement,
        "method": "majority_vote",
    }


def confidence_weighted(annotations: list[dict]) -> dict[str, Any]:
    """Resolve annotation disagreements by confidence-weighted voting.

    Each annotator's vote is weighted by their confidence in that
    annotation.  Falls back to majority vote if no confidence field
    is present.

    Args:
        annotations: Annotation records for a single article.

    Returns:
        Dictionary with ``adjudicated_labels``, per-field ``agreement``
        info, and the ``method`` name.
    """
    if not annotations:
        return {
            "adjudicated_labels": {},
            "agreement": {},
            "method": "confidence_weighted",
        }

    # Find the confidence field
    sample = annotations[0].get("annotations", {})
    confidence_field: str | None = next(
        (key for key in sample if "confidence" in key.lower()),
        None,
    )

    if confidence_field is None:
        return majority_vote(annotations)

    # Accumulate weighted counts per field
    weighted_counts: dict[str, dict[Any, float]] = defaultdict(
        lambda: defaultdict(float),
    )

    for ann in annotations:
        ann_data = ann.get("annotations", {})
        weight = float(ann_data.get(confidence_field, 1))

        for key, value in ann_data.items():
            if key in _META_FIELDS or key == confidence_field:
                continue
            if value is not None and value != "":
                weighted_counts[key][value] += weight

    adjudicated: dict[str, Any] = {}
    agreement_info: dict[str, Any] = {}

    for field, counts in weighted_counts.items():
        if not counts:
            adjudicated[field] = None
            agreement_info[field] = {"n_votes": 0}
            continue

        top_value = max(counts, key=counts.get)
        total_weight = sum(counts.values())

        adjudicated[field] = top_value
        agreement_info[field] = {
            "n_votes": len(counts),
            "weighted_agreement": (
                round(counts[top_value] / total_weight, 4)
                if total_weight > 0
                else 0.0
            ),
            "weight_distribution": dict(counts),
        }

    return {
        "adjudicated_labels": adjudicated,
        "agreement": agreement_info,
        "method": "confidence_weighted",
    }


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudication Pipeline")
    parser.add_argument(
        "--input", required=True,
        help="Input annotations directory containing JSONL files",
    )
    parser.add_argument(
        "--method", default="majority",
        choices=["majority", "confidence", "human_review"],
        help="Adjudication method",
    )
    parser.add_argument(
        "--output", default="refset/",
        help="Output directory for reference set and report",
    )
    args = parser.parse_args()

    logger.info("Adjudicating with method: %s", args.method)

    # Load and group
    annotations = load_annotations(args.input)
    grouped = group_by_article(annotations)
    logger.info("Grouped into %d articles", len(grouped))

    # Inter-rater agreement
    logger.info("Computing inter-rater agreement …")
    agreement_report = compute_interrater_agreement(grouped)

    # Resolve disagreements
    logger.info("Resolving disagreements …")
    refset: list[dict[str, Any]] = []

    for article_id, records in grouped.items():
        if args.method == "majority":
            resolved = majority_vote(records)
        elif args.method == "confidence":
            resolved = confidence_weighted(records)
        elif args.method == "human_review":
            resolved = majority_vote(records)
            resolved["needs_human_review"] = True
        else:
            resolved = majority_vote(records)

        refset.append({
            "article_id": article_id,
            "annotators": [
                {
                    "annotator_id": r["annotator_id"],
                    "annotations": r.get("annotations", {}),
                }
                for r in records
            ],
            **resolved,
        })

    # Save
    out_dir = Path(args.output)
    ensure_dirs(out_dir)

    refset_file = out_dir / "refset.jsonl"
    save_jsonl(refset, refset_file)
    logger.info("Reference set saved: %s (%d articles)", refset_file, len(refset))

    report_file = out_dir / "adjudication_report.json"
    write_json(report_file, agreement_report)
    logger.info("Agreement report saved: %s", report_file)

    # Print summary
    n_flagged = sum(1 for r in refset if r.get("needs_human_review"))
    if n_flagged:
        logger.info(
            "%d articles flagged for human review", n_flagged,
        )

    logger.info(
        "Adjudication complete. %d articles in locked reference set.",
        len(refset),
    )


if __name__ == "__main__":
    main()
