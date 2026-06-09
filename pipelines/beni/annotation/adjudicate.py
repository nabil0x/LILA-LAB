"""
Adjudication tools for BENI 300-article annotation batch.

Computes Cohen's kappa between two annotators, generates agreement
reports, and produces the gold-standard label set.

Usage:
    python3 adjudicate.py --annotator-a exports/annotator_a_results.json \
                          --annotator-b exports/annotator_b_results.json \
                          --output exports/gold_standard.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPORTS_DIR = Path(__file__).parent / "exports"


def cohens_kappa(y1: list, y2: list) -> float:
    n = len(y1)
    if n == 0:
        return 0.0
    labels = sorted(set(y1) | set(y2))
    po = sum(1 for a, b in zip(y1, y2) if a == b) / n
    c1 = Counter(y1)
    c2 = Counter(y2)
    pe = sum((c1.get(l, 0) / n) * (c2.get(l, 0) / n) for l in labels)
    if abs(pe - 1.0) < 1e-9:
        return 1.0
    return round((po - pe) / (1 - pe), 4)


def load_labelstudio_export(path: Path) -> dict[str, dict[str, Any]]:
    """Load LabelStudio JSON export. Returns dict mapping article_id -> annotations."""
    data = json.loads(path.read_text(encoding="utf-8"))
    results: dict[str, dict[str, Any]] = {}
    for item in data:
        aid = item.get("id", "")
        annotations = item.get("annotations", [{}])
        if not annotations:
            continue
        ann = annotations[0]
        result_list = ann.get("result", [])
        parsed: dict[str, Any] = {"confidence": None, "difficulty": None}
        for r in result_list:
            from_name = r.get("from_name", "")
            value = r.get("value", {})
            if from_name == "economic_relevance":
                parsed["economic_relevance"] = value.get("choices", [None])[0]
            elif from_name == "confidence":
                parsed["confidence"] = value.get("rating")
            elif from_name == "difficulty":
                parsed["difficulty"] = value.get("choices", [None])[0]
            elif from_name == "economic_topic":
                parsed["economic_topic"] = value.get("choices", [None])[0]
            elif from_name == "sentiment":
                parsed["sentiment"] = value.get("choices", [None])[0]
            elif from_name == "narrative_force":
                parsed["narrative_force"] = value.get("choices", [None])[0]
            elif from_name == "valuation_target":
                parsed["valuation_target"] = value.get("choices", [None])[0]
            elif from_name == "notes":
                parsed["notes"] = value.get("text", [None])[0] if isinstance(value.get("text"), list) else value.get("text")
        results[aid] = parsed
    return results


def compute_agreement_report(
    ann_a: dict[str, dict[str, Any]],
    ann_b: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    fields = [
        "economic_relevance",
        "economic_topic",
        "sentiment",
        "narrative_force",
        "valuation_target",
    ]
    report: dict[str, Any] = {
        "total_articles": len(set(ann_a.keys()) & set(ann_b.keys())),
        "field_agreement": {},
        "disagreement_matrix": {},
    }

    common_ids = sorted(set(ann_a.keys()) & set(ann_b.keys()))

    for field in fields:
        y1, y2 = [], []
        for aid in common_ids:
            v1 = ann_a[aid].get(field)
            v2 = ann_b[aid].get(field)
            if v1 is not None and v2 is not None:
                y1.append(v1)
                y2.append(v2)

        if len(y1) < 2:
            report["field_agreement"][field] = {
                "n": len(y1),
                "kappa": None,
                "observed_agreement": None,
                "message": "Insufficient data",
            }
            continue

        kappa = cohens_kappa(y1, y2)
        obs_agree = sum(1 for a, b in zip(y1, y2) if a == b) / len(y1)
        disagreements = sum(1 for a, b in zip(y1, y2) if a != b)

        labels = sorted(set(y1) | set(y2))
        matrix = {l1: {l2: 0 for l2 in labels} for l1 in labels}
        for a, b in zip(y1, y2):
            matrix[a][b] += 1

        report["field_agreement"][field] = {
            "n": len(y1),
            "kappa": kappa,
            "observed_agreement": round(obs_agree, 4),
            "disagreements": disagreements,
            "disagreement_rate": round(disagreements / len(y1), 4),
        }
        report["disagreement_matrix"][field] = matrix

    kappas = [
        v["kappa"]
        for v in report["field_agreement"].values()
        if v["kappa"] is not None
    ]
    report["mean_kappa"] = round(sum(kappas) / len(kappas), 4) if kappas else None

    return report


def build_gold_standard(
    ann_a: dict[str, dict[str, Any]],
    ann_b: dict[str, dict[str, Any]],
    report: dict[str, Any],
    base_tasks_path: Path,
    output_path: Path,
) -> None:
    """Build gold-standard dataset with adjudication decisions."""
    base_tasks = json.loads(base_tasks_path.read_text(encoding="utf-8"))
    base_by_id = {t["id"]: t for t in base_tasks}

    common_ids = sorted(set(ann_a.keys()) & set(ann_b.keys()))
    gold: list[dict[str, Any]] = []

    for aid in common_ids:
        a_data = ann_a[aid]
        b_data = ann_b[aid]
        base = base_by_id.get(aid, {})
        entry = {
            "id": aid,
            "data": base.get("data", {}),
            "annotations": [
                {"annotator": "A", **a_data},
                {"annotator": "B", **b_data},
            ],
            "gold": {},
            "agreement": {},
        }

        fields = [
            "economic_relevance",
            "economic_topic",
            "sentiment",
            "narrative_force",
            "valuation_target",
        ]
        for field in fields:
            v1 = a_data.get(field)
            v2 = b_data.get(field)
            if v1 == v2:
                entry["gold"][field] = v1
                entry["agreement"][field] = "agree"
            else:
                entry["gold"][field] = None  # Needs adjudicator review
                entry["agreement"][field] = "disagree"

        gold.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(gold, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Gold standard: {len(gold)} articles -> {output_path}")


def print_report(report: dict[str, Any]) -> None:
    print("\n" + "=" * 60)
    print("BENI Adjudication Report")
    print("=" * 60)
    print(f"Total articles: {report['total_articles']}")
    print(f"Mean kappa:     {report['mean_kappa']}")
    print()
    print(f"{'Field':<25s} {'N':>5s} {'κ':>8s} {'Agree':>8s} {'Disagree':>10s}")
    print("-" * 56)
    for field, stats in report["field_agreement"].items():
        k = f"{stats['kappa']:.4f}" if stats["kappa"] is not None else "N/A"
        oa = f"{stats['observed_agreement']:.2%}" if stats["observed_agreement"] is not None else "N/A"
        d = str(stats["disagreements"]) if "disagreements" in stats else "N/A"
        print(f"{field:<25s} {stats['n']:>5d} {k:>8s} {oa:>8s} {d:>10s}")
    print("=" * 60)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="BENI adjudication")
    parser.add_argument("--annotator-a", type=Path, required=True)
    parser.add_argument("--annotator-b", type=Path, required=True)
    parser.add_argument("--base-tasks", type=Path,
                        default=EXPORTS_DIR / "beni_300_batch.json")
    parser.add_argument("--output", type=Path,
                        default=EXPORTS_DIR / "gold_standard.json")
    args = parser.parse_args()

    print("Loading annotations...")
    ann_a = load_labelstudio_export(args.annotator_a)
    ann_b = load_labelstudio_export(args.annotator_b)
    print(f"  Annotator A: {len(ann_a)} articles")
    print(f"  Annotator B: {len(ann_b)} articles")

    print("\nComputing agreement...")
    report = compute_agreement_report(ann_a, ann_b)
    print_report(report)

    report_path = EXPORTS_DIR / "adjudication_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nReport saved -> {report_path}")

    if args.base_tasks.exists():
        build_gold_standard(ann_a, ann_b, report, args.base_tasks, args.output)
    else:
        print(f"\n[WARN] Base tasks not found at {args.base_tasks}; gold standard not built")


if __name__ == "__main__":
    main()
