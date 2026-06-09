#!/usr/bin/env python3
"""Generate article-level BENI v1 predictions from the repaired corpus."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "processed" / "beni_unified_articles_deduped.csv.zst"
MODEL_PATH = ROOT / "data" / "models" / "economic_potrika-timeseries_tfidf_logreg.joblib"
OUT_PATH = ROOT / "data" / "index" / "beni_v1_article_predictions.parquet"
OUT_SUMMARY = ROOT / "data" / "index" / "beni_v1_article_predictions_summary.json"

CHUNK_SIZE = 10_000
POSITIVE_CLASS = 1


def predict_chunk(model, df: pd.DataFrame) -> pd.DataFrame:
    texts = df["text_clean"].fillna("").astype(str).tolist()
    proba = model.predict_proba(texts)
    if proba.ndim == 1:
        econ_prob = proba
    else:
        econ_prob = proba[:, POSITIVE_CLASS]

    econ_pred = model.predict(texts)
    out = pd.DataFrame(
        {
            "article_id": df["article_id"].astype(str),
            "publication_date": df["publication_date"].astype(str),
            "year_month": df["year_month"].astype(str),
            "dataset_source": df["dataset_source"].astype(str),
            "source_file": df["source_file"].astype(str),
            "newspaper": df["newspaper"].astype(str),
            "category_harmonised": df["category_harmonised"].astype(str),
            "is_duplicate": df["is_duplicate"].astype(bool),
            "duplicate_group_id": df["duplicate_group_id"].fillna("").astype(str),
            "economic_prob": econ_prob.astype(float),
            "economic_pred": econ_pred.astype(int),
            "model_version": "economic_potrika-timeseries_tfidf_logreg",
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    return out


def main() -> None:
    model = joblib.load(MODEL_PATH)

    usecols = [
        "article_id",
        "dataset_source",
        "source_file",
        "newspaper",
        "publication_date",
        "year_month",
        "category_harmonised",
        "text_clean",
        "is_duplicate",
        "duplicate_group_id",
    ]

    reader = pd.read_csv(
        CORPUS_PATH,
        compression="zstd",
        usecols=usecols,
        chunksize=CHUNK_SIZE,
    )

    writer = None
    total_rows = 0
    econ_rows = 0
    source_counts: dict[str, int] = {}
    year_counts: dict[str, int] = {}

    try:
        for i, chunk in enumerate(reader, start=1):
            pred = predict_chunk(model, chunk)
            total_rows += len(pred)
            econ_rows += int(pred["economic_pred"].sum())
            for k, v in pred["dataset_source"].value_counts().items():
                source_counts[k] = source_counts.get(k, 0) + int(v)
            for k, v in pred["year_month"].str[:4].value_counts().items():
                year_counts[k] = year_counts.get(k, 0) + int(v)

            table = pa.Table.from_pandas(pred, preserve_index=False)
            if writer is None:
                OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
                writer = pq.ParquetWriter(OUT_PATH, table.schema, compression="zstd")
            writer.write_table(table)
            print(f"[chunk {i}] wrote {len(pred):,} rows; cumulative {total_rows:,}", flush=True)
    finally:
        if writer is not None:
            writer.close()

    summary = {
        "corpus_path": str(CORPUS_PATH),
        "model_path": str(MODEL_PATH),
        "output_path": str(OUT_PATH),
        "chunk_size": CHUNK_SIZE,
        "rows": total_rows,
        "economic_predictions": econ_rows,
        "economic_share": econ_rows / total_rows if total_rows else 0.0,
        "dataset_source_counts": source_counts,
        "year_counts": year_counts,
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
