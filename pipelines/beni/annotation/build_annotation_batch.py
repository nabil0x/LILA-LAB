"""
Build 300-article BENI annotation batch for LabelStudio.

This script:
1. Loads BNLP news_categorization data (13,940 articles, 6 topics)
2. Creates a stratified 300-article sample with ~35% economic ratio
3. Merges existing BanglaBERT pre-labels from bnlp_sample_with_predictions.json
4. Exports to LabelStudio JSON format with the expanded annotation schema

Usage:
    python3 build_annotation_batch.py

Output:
    exports/beni_300_batch.json          → LabelStudio import (no predictions)
    exports/beni_300_batch_with_ml.json  → LabelStudio import with pre-labels
    exports/beni_300_batch_stats.json    → Stratification summary
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────
BENI_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = BENI_ROOT / "experiment"
BNLP_DIR = EXPERIMENT_DIR / "bnlp-resources" / "news_categorization"
EXPORTS_DIR = Path(__file__).parent / "exports"
EXISTING_PREDICTIONS = EXPORTS_DIR / "bnlp_sample_with_predictions.json"

random.seed(42)
np.random.seed(42)

# ── Keyword list (mirrors config.py / export_for_labelstudio.py) ───────
ECONOMIC_KEYWORDS = [
    "অর্থনীতি", "অর্থনৈতিক", "মুদ্রাস্ফীতি", "মূল্যস্ফীতি",
    "ভোক্তা মূল্য", "খাদ্য মূল্য", "ডলার", "বৈদেশিক মুද્રা",
    "রিজার্ভ", "বাংলাদেশ ব্যাংক", "সোনালী ব্যাংক", "জনতা ব্যাংক",
    "অগ্রণী ব্যাংক", "রূপালী ব্যাংক", "বাণিজ্য", "রপ্তানি",
    "আমদানি", "শিল্পোৎপাদন", "জিডিপি", "মোট দেশজ উৎপাদন",
    "শেয়ারবাজার", "পুঁজিবাজার", "বিনিয়োগ", "প্রবাসী আয়",
    "রেমিট্যান্স", "বাজেট", "অর্থমন্ত্রী", "টাকার বিনিময় হার",
    "বিনিময় হার", "সুদের হার", "সঞ্চয়পত্র", "ব্যাংক", "ঋণ",
    "কৃষি", "ফসল", "উৎপাদন", "সরকারি বন্ড", "টানা বাজেট",
    "মূল্য বৃদ্ধি", "দাম বাড়া", "সাড়া মূল্য", "ভর্তুকি",
    "সরকারি ব্যয়", "রাজস্ব", "কর", "শুল্ক", "বৈদেশিক বাণিজ্য",
    "পণ্য রপ্তানি", "পোশাক শিল্প", "গার্মেন্টস",
]


def _keyword_match(text: str) -> int:
    """Check if any economic keyword appears in the text."""
    text_lower = text.lower()
    for kw in ECONOMIC_KEYWORDS:
        if kw in text_lower:
            return 1
    return 0


def load_bnlp_data() -> list[dict[str, Any]]:
    """Load all BNLP news_categorization articles."""
    records = []
    for split in ("train", "dev", "test"):
        path = BNLP_DIR / f"{split}.tsv"
        if not path.exists():
            print(f"  [WARN] Missing: {path}")
            continue
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            if header != ["id", "text", "class_label"]:
                print(f"  [WARN] Unexpected header in {path}: {header}")
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
    print(f"  Loaded {len(records)} articles from BNLP")
    return records


def load_existing_predictions() -> dict[str, dict[str, Any]]:
    """
    Load existing BanglaBERT pre-labels from previous run.

    Returns dict mapping article ID -> prediction dict with:
        - pred_label: "Economic" or "Not Economic"
        - confidence: float
    """
    if not EXISTING_PREDICTIONS.exists():
        print("  [WARN] No existing predictions file found. Using keyword labels as fallback.")
        return {}

    data = json.loads(EXISTING_PREDICTIONS.read_text(encoding="utf-8"))
    predictions: dict[str, dict[str, Any]] = {}
    for item in data:
        aid = item["id"]
        preds_list = item.get("predictions", [])
        if preds_list:
            pred = preds_list[0]
            for result in pred.get("result", []):
                if result.get("from_name") == "economic_relevance":
                    predictions[aid] = {
                        "pred_label": result["value"]["choices"][0],
                        "confidence": result.get("confidence", 0.0),
                        "model_version": pred.get("model_version", "unknown"),
                    }
    print(f"  Loaded {len(predictions)} existing BanglaBERT pre-labels")
    return predictions


def build_stratified_sample(
    records: list[dict[str, Any]],
    n_total: int = 300,
    econ_ratio: float = 0.35,
) -> list[dict[str, Any]]:
    for rec in records:
        rec["keyword_label"] = _keyword_match(rec["text"])

    topic_targets = {
        "national": 0.18, "state": 0.18, "kolkata": 0.20,
        "sports": 0.15, "entertainment": 0.14, "international": 0.15,
    }
    weight_sum = sum(topic_targets.values())
    topic_targets = {t: w / weight_sum for t, w in topic_targets.items()}

    n_econ = int(n_total * econ_ratio)
    n_non = n_total - n_econ

    econ_candidates = [r for r in records if r["keyword_label"] == 1]
    non_econ_candidates = [r for r in records if r["keyword_label"] == 0]
    random.shuffle(econ_candidates)
    random.shuffle(non_econ_candidates)

    def _topic_sample(pool: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
        result = []
        counts = {t: int(n * p) for t, p in topic_targets.items()}
        distributed = sum(counts.values())
        for t in sorted(topic_targets, key=lambda t: -topic_targets[t]):
            if distributed >= n:
                break
            counts[t] += 1
            distributed += 1
        for topic, quota in counts.items():
            topic_pool = [r for r in pool if r["topic"] == topic]
            result.extend(topic_pool[:min(len(topic_pool), quota)])
        shortfall = n - len(result)
        if shortfall > 0:
            remaining = [r for r in pool if r not in result]
            result.extend(remaining[:shortfall])
        random.shuffle(result)
        return result

    sampled = _topic_sample(econ_candidates, n_econ) + _topic_sample(non_econ_candidates, n_non)
    random.shuffle(sampled)

    actual_econ = sum(1 for r in sampled if r["keyword_label"] == 1)
    print(f"  Sampled: {len(sampled)} articles ({actual_econ} economic, "
          f"{actual_econ/len(sampled)*100:.1f}%)")
    return sampled


def export_to_labelstudio(
    articles: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    output_path: Path,
    include_ml_predictions: bool = False,
) -> None:
    """Export to LabelStudio JSON format with the expanded schema."""
    tasks = []
    for art in articles:
        task: dict[str, Any] = {
            "id": art["id"],
            "data": {
                "text": art["text"][:5000],
                "topic": art["topic"],
                "keyword_label": art["keyword_label"],
                "source": art["source"],
                "id": art["id"],
            },
        }

        if include_ml_predictions:
            pred = predictions.get(art["id"])
            if pred:
                task["predictions"] = [
                    {
                        "model_version": pred.get("model_version", "banglabert_bnwp_prelabel"),
                        "score": pred["confidence"],
                        "result": [
                            {
                                "from_name": "economic_relevance",
                                "to_name": "article_text",
                                "type": "choices",
                                "value": {"choices": [pred["pred_label"]]},
                                "confidence": pred["confidence"],
                            },
                        ],
                    },
                ]
            else:
                kw_label = "Economic" if art["keyword_label"] == 1 else "Not Economic"
                kw_conf = 0.85 if art["keyword_label"] == 1 else 0.95  # heuristic confidence
                task["predictions"] = [
                    {
                        "model_version": "keyword_fallback",
                        "score": kw_conf,
                        "result": [
                            {
                                "from_name": "economic_relevance",
                                "to_name": "article_text",
                                "type": "choices",
                                "value": {"choices": [kw_label]},
                                "confidence": kw_conf,
                            },
                        ],
                    },
                ]

        tasks.append(task)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  Wrote {len(tasks)} tasks → {output_path}")


def print_stats(articles: list[dict[str, Any]], label: str = "") -> None:
    """Print stratification summary."""
    econ_count = sum(1 for a in articles if a["keyword_label"] == 1)
    topics = Counter(a["topic"] for a in articles)
    econ_by_topic = Counter(a["topic"] for a in articles if a["keyword_label"] == 1)

    print(f"\n  {'=' * 50}")
    print(f"  Stratification Summary {label}")
    print(f"  {'=' * 50}")
    print(f"  Total: {len(articles)}")
    print(f"  Economic (keyword): {econ_count} ({econ_count/len(articles)*100:.1f}%)")
    print(f"  Not Economic: {len(articles) - econ_count} ({(len(articles)-econ_count)/len(articles)*100:.1f}%)")
    print(f"\n  By Topic:")
    print(f"  {'Topic':<20s} {'Total':>6s} {'Econ':>6s} {'Ratio':>8s}")
    print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*8}")
    for topic in sorted(topics.keys()):
        total = topics[topic]
        econ_t = econ_by_topic.get(topic, 0)
        ratio = econ_t / total if total > 0 else 0
        print(f"  {topic:<20s} {total:>6d} {econ_t:>6d} {ratio:>7.0%}")
    print(f"  {'=' * 50}\n")


def main() -> None:
    print("=" * 60)
    print("BENI 300-Article Annotation Batch Builder")
    print("=" * 60)

    print("\n[1/4] Loading BNLP news_categorization data...")
    records = load_bnlp_data()

    print("\n[2/4] Loading existing BanglaBERT pre-labels...")
    predictions = load_existing_predictions()

    print("\n[3/4] Building stratified 300-article sample...")
    sampled = build_stratified_sample(records, n_total=300, econ_ratio=0.35)
    print_stats(sampled, "(300-article batch)")

    print("\n[4/4] Exporting to LabelStudio format...")

    clean_path = EXPORTS_DIR / "beni_300_batch.json"
    export_to_labelstudio(sampled, predictions, clean_path, include_ml_predictions=False)

    ml_path = EXPORTS_DIR / "beni_300_batch_with_ml.json"
    export_to_labelstudio(sampled, predictions, ml_path, include_ml_predictions=True)

    stats_path = EXPORTS_DIR / "beni_300_batch_stats.json"
    topics = Counter(a["topic"] for a in sampled)
    econ_by_topic = Counter(a["topic"] for a in sampled if a["keyword_label"] == 1)
    stats = {
        "total": len(sampled),
        "economic_keyword": sum(1 for a in sampled if a["keyword_label"] == 1),
        "not_economic_keyword": sum(1 for a in sampled if a["keyword_label"] == 0),
        "econ_ratio": sum(1 for a in sampled if a["keyword_label"] == 1) / len(sampled),
        "by_topic": {
            t: {
                "total": topics[t],
                "economic": econ_by_topic.get(t, 0),
                "ratio": econ_by_topic.get(t, 0) / topics[t] if topics[t] > 0 else 0,
            }
            for t in sorted(topics.keys())
        },
        "sampling_seed": 42,
        "batch_size": 300,
        "target_econ_ratio": 0.35,
    }
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote stats → {stats_path}")

    print("\n" + "=" * 60)
    print("Done! Import into LabelStudio:")
    print(f"  With ML pre-labels: {ml_path}")
    print(f"  Clean (no pre-labels): {clean_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
