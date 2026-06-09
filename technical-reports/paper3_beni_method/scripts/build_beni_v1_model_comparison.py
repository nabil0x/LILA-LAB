#!/usr/bin/env python3
"""Build BENI v1 model-comparison outputs from the frozen validation set.

This script evaluates the frozen BENI v1 reference labels against the repaired
article-level TF-IDF predictions. It preserves the older prototype comparison
as a clearly marked legacy appendix input, but the frozen validation metrics are
computed only from the BENI v1 frozen label set.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_DIR = ROOT / "data" / "annotations"
INDEX_DIR = ROOT / "data" / "index"
FROZEN_LABELS_PATH = ANNOTATIONS_DIR / "beni_v1_reference_labels_frozen.jsonl"
PREDICTIONS_PATH = INDEX_DIR / "beni_v1_article_predictions.parquet"
LEGACY_COMPARISON_PATH = ANNOTATIONS_DIR / "model_comparison.json"

OUT_JSON = ANNOTATIONS_DIR / "model_comparison_beni_v1.json"
OUT_TXT = ANNOTATIONS_DIR / "model_comparison_beni_v1.txt"
OUT_CSV = ANNOTATIONS_DIR / "model_comparison_beni_v1.csv"

ECONOMIC = "Economic"
NOT_ECONOMIC = "Not Economic"


def cohens_kappa(y1: list[str], y2: list[str]) -> float:
    n = len(y1)
    if n == 0:
        return 0.0
    labels = sorted(set(y1) | set(y2))
    n_classes = len(labels)
    cm = np.zeros((n_classes, n_classes), dtype=int)
    idx = {label: i for i, label in enumerate(labels)}
    for a, b in zip(y1, y2):
        cm[idx[a], idx[b]] += 1
    p_o = np.trace(cm) / n
    row_sums = cm.sum(axis=1)
    col_sums = cm.sum(axis=0)
    p_e = sum(row_sums[i] * col_sums[i] for i in range(n_classes)) / (n * n)
    if p_e == 1:
        return 0.0
    return (p_o - p_e) / (1 - p_e)


def classification_metrics(y_pred: list[str], y_true: list[str]) -> dict[str, Any]:
    n = len(y_pred)
    correct = sum(1 for p, t in zip(y_pred, y_true) if p == t)
    accuracy = correct / n if n else 0.0
    kappa = cohens_kappa(y_pred, y_true)

    tp = sum(1 for p, t in zip(y_pred, y_true) if p == ECONOMIC and t == ECONOMIC)
    fp = sum(1 for p, t in zip(y_pred, y_true) if p == ECONOMIC and t == NOT_ECONOMIC)
    fn = sum(1 for p, t in zip(y_pred, y_true) if p == NOT_ECONOMIC and t == ECONOMIC)
    tn = sum(1 for p, t in zip(y_pred, y_true) if p == NOT_ECONOMIC and t == NOT_ECONOMIC)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "n": n,
        "n_economic_predicted": sum(1 for p in y_pred if p == ECONOMIC),
        "n_economic_true": sum(1 for t in y_true if t == ECONOMIC),
        "accuracy": round(accuracy, 4),
        "cohens_kappa": round(kappa, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "confusion_matrix": {
            ECONOMIC: {ECONOMIC: tp, NOT_ECONOMIC: fp},
            NOT_ECONOMIC: {ECONOMIC: fn, NOT_ECONOMIC: tn},
        },
    }


def load_frozen_labels(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("include_in_clean_validation"):
                rows.append(
                    {
                        "article_id": row["canonical_article_id"],
                        "gold_label": row["final_label"],
                        "original_article_id": row["original_article_id"],
                        "source": row.get("source", ""),
                        "category": row.get("category", ""),
                        "annotation_method": row.get("annotation_method", ""),
                        "confidence": row.get("confidence"),
                        "difficulty": row.get("difficulty"),
                    }
                )
    return pd.DataFrame(rows)


def load_tfidf_predictions(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=["article_id", "economic_prob", "economic_pred"])
    df = df.copy()
    df["article_id"] = df["article_id"].astype(str)
    df["tfidf_label"] = df["economic_pred"].map({1: ECONOMIC, 0: NOT_ECONOMIC})
    return df[["article_id", "economic_prob", "tfidf_label"]]


def load_legacy_comparison(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_legacy(legacy: dict[str, Any] | None) -> dict[str, Any] | None:
    if not legacy:
        return None
    return {
        "metadata": legacy.get("metadata", {}),
        "per_model_vs_gold": legacy.get("per_model_vs_gold", {}),
        "pairwise_mcnemar": legacy.get("pairwise_mcnemar", []),
        "pairwise_agreement": legacy.get("pairwise_agreement", []),
        "ranking": legacy.get("ranking", []),
        "note": "Legacy prototype comparison; not recomputed on the frozen BENI v1 validation set.",
    }


def main() -> None:
    frozen = load_frozen_labels(FROZEN_LABELS_PATH)
    tfidf = load_tfidf_predictions(PREDICTIONS_PATH)

    merged = frozen.merge(tfidf, on="article_id", how="left", validate="one_to_one")
    if merged["tfidf_label"].isna().any():
        missing = merged.loc[merged["tfidf_label"].isna(), "article_id"].tolist()[:10]
        raise RuntimeError(
            f"Missing TF-IDF predictions for {int(merged['tfidf_label'].isna().sum())} frozen labels. "
            f"Sample: {missing}"
        )

    y_gold = merged["gold_label"].tolist()
    y_tfidf = merged["tfidf_label"].tolist()

    tfidf_metrics = classification_metrics(y_tfidf, y_gold)
    majority_label = NOT_ECONOMIC
    y_majority = [majority_label] * len(y_gold)
    majority_metrics = classification_metrics(y_majority, y_gold)

    legacy = summarize_legacy(load_legacy_comparison(LEGACY_COMPARISON_PATH))

    report = {
        "metadata": {
            "dataset_version": "BENI_v1_reference_frozen",
            "n_total": int(len(merged)),
            "n_economic_gold": int(sum(1 for v in y_gold if v == ECONOMIC)),
            "n_economic_tfidf": int(sum(1 for v in y_tfidf if v == ECONOMIC)),
            "n_economic_majority_baseline": int(sum(1 for v in y_majority if v == ECONOMIC)),
            "n_excluded_from_clean_validation": 114,
            "n_included_in_clean_validation": int(len(merged)),
        },
        "per_model_vs_gold": {
            "TF-IDF + LogReg": tfidf_metrics,
            "Majority baseline (Not Economic)": majority_metrics,
        },
        "pairwise_mcnemar": [],
        "pairwise_agreement": [],
        "pattern_summary": dict(Counter(f"G={g[0]}/T={t[0]}" for g, t in zip(y_gold, y_tfidf)).most_common()),
        "error_log": [
            {"id": aid, "gold": g, "tfidf": t}
            for aid, g, t in zip(merged["article_id"], y_gold, y_tfidf)
            if g != t
        ],
        "ranking": [
            {"rank": 1, "model": "TF-IDF + LogReg", **tfidf_metrics},
            {"rank": 2, "model": "Majority baseline (Not Economic)", **majority_metrics},
        ],
        "legacy_prototype_comparison": legacy,
    }

    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for model_name, metrics in report["per_model_vs_gold"].items():
        rows.append(
            {
                "model": model_name,
                **{k: v for k, v in metrics.items() if k != "confusion_matrix"},
            }
        )
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)

    lines = [
        "=" * 72,
        "BENI v1 MODEL COMPARISON",
        "=" * 72,
        "",
        f"Frozen validation set: {report['metadata']['n_total']} articles",
        f"  Economic:     {report['metadata']['n_economic_gold']}",
        f"  Not Economic: {report['metadata']['n_total'] - report['metadata']['n_economic_gold']}",
        "",
        "Per-model performance vs frozen BENI v1 reference labels:",
        f"  {'Model':40s} {'Acc':>6s} {'Kappa':>7s} {'Prec':>6s} {'Recall':>7s} {'F1':>6s} {'Econ':>6s}",
        "  " + "-" * 72,
    ]
    for row in rows:
        lines.append(
            f"  {row['model'][:40]:40s} "
            f"{row['accuracy']:.2%} {row['cohens_kappa']:.4f} {row['precision']:.2%} "
            f"{row['recall']:.2%} {row['f1']:.2%} "
            f"{row['n_economic_predicted']:3d}/{row['n']:3d}"
        )

    lines += [
        "",
        f"Legacy prototype comparison available: {'yes' if legacy else 'no'}",
        "Legacy prototype results are not recomputed here and should remain labeled as prototype evidence.",
    ]
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report["metadata"], ensure_ascii=False, indent=2), flush=True)
    print(f"Wrote {OUT_JSON}", flush=True)


if __name__ == "__main__":
    main()
