#!/usr/bin/env python3
"""Build BENI v1 monthly indices from repaired article-level predictions."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = ROOT / "data" / "index" / "beni_v1_article_predictions.parquet"
OUT_DIR = ROOT / "data" / "index"
OUT_INDEX = OUT_DIR / "beni_v1_monthly_index.csv"
OUT_ARTICLE_WEIGHTED = OUT_DIR / "beni_v1_monthly_index_article_weighted.csv"
OUT_SOURCE_BALANCED = OUT_DIR / "beni_v1_monthly_index_source_balanced.csv"
OUT_SOURCE_COVERAGE = OUT_DIR / "beni_v1_monthly_source_coverage.csv"
OUT_CATEGORY_COVERAGE = OUT_DIR / "beni_v1_monthly_category_coverage.csv"
OUT_SUMMARY = OUT_DIR / "beni_v1_monthly_index_summary.json"


def _prepare_frame(path: Path) -> tuple[pd.DataFrame, dict]:
    if not path.exists():
        raise FileNotFoundError(f"Prediction parquet not found: {path}")

    df = pd.read_parquet(path)
    qa = {
        "raw_rows": int(len(df)),
        "duplicate_rows_flagged": int(df["is_duplicate"].fillna(False).astype(bool).sum()) if "is_duplicate" in df.columns else 0,
    }
    required = {
        "article_id",
        "publication_date",
        "year_month",
        "dataset_source",
        "newspaper",
        "category_harmonised",
        "economic_prob",
        "economic_pred",
        "is_duplicate",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Prediction parquet missing columns: {missing}")

    df = df.copy()
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
    df["month"] = df["publication_date"].dt.to_period("M").dt.to_timestamp()
    df["economic_prob"] = pd.to_numeric(df["economic_prob"], errors="coerce")
    df["economic_pred"] = pd.to_numeric(df["economic_pred"], errors="coerce").fillna(0).astype(int)
    df["is_duplicate"] = df["is_duplicate"].fillna(False).astype(bool)

    df = df[df["publication_date"].notna() & df["month"].notna()].copy()
    qa["rows_after_required_fields"] = int(len(df))
    df = df[df["is_duplicate"] == False].copy()  # noqa: E712
    df["newspaper"] = df["newspaper"].fillna("unknown").astype(str)
    df["dataset_source"] = df["dataset_source"].fillna("unknown").astype(str)
    df["category_harmonised"] = df["category_harmonised"].fillna("unknown").astype(str)
    qa["rows_scored"] = int(len(df))
    qa["rows_excluded_missing_required"] = qa["raw_rows"] - qa["rows_after_required_fields"]
    qa["duplicate_rows_excluded"] = qa["rows_after_required_fields"] - qa["rows_scored"]
    return df, qa


def _weighted_monthly(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("month", as_index=False).agg(
        n_articles=("article_id", "size"),
        mean_prob=("economic_prob", "mean"),
        economic_share=("economic_pred", "mean"),
        n_economic=("economic_pred", "sum"),
        n_sources=("newspaper", "nunique"),
        n_dataset_sources=("dataset_source", "nunique"),
        n_categories=("category_harmonised", "nunique"),
    )
    grouped["economic_share"] = grouped["economic_share"].astype(float)
    grouped["n_economic"] = grouped["n_economic"].astype(int)
    return grouped.sort_values("month").reset_index(drop=True)


def _source_balanced_monthly(df: pd.DataFrame) -> pd.DataFrame:
    source_month = (
        df.groupby(["month", "newspaper"], as_index=False)
        .agg(
            source_n_articles=("article_id", "size"),
            source_mean_prob=("economic_prob", "mean"),
            source_economic_share=("economic_pred", "mean"),
            source_n_economic=("economic_pred", "sum"),
            source_dataset_sources=("dataset_source", "nunique"),
            source_categories=("category_harmonised", "nunique"),
        )
        .sort_values(["month", "newspaper"])
    )

    balanced = source_month.groupby("month", as_index=False).agg(
        n_sources=("newspaper", "nunique"),
        n_articles=("source_n_articles", "sum"),
        mean_prob=("source_mean_prob", "mean"),
        economic_share=("source_economic_share", "mean"),
        mean_source_articles=("source_n_articles", "mean"),
        median_source_articles=("source_n_articles", "median"),
        mean_source_economic_count=("source_n_economic", "mean"),
    )
    balanced["economic_share"] = balanced["economic_share"].astype(float)
    balanced["n_economic_equiv"] = (balanced["n_articles"] * balanced["economic_share"]).round(0).astype(int)
    balanced = balanced.sort_values("month").reset_index(drop=True)
    return balanced


def _category_coverage(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["month", "category_harmonised"], as_index=False)
        .agg(
            n_articles=("article_id", "size"),
            n_economic=("economic_pred", "sum"),
            mean_prob=("economic_prob", "mean"),
        )
        .sort_values(["month", "category_harmonised"])
    )
    monthly_totals = out.groupby("month", as_index=False)["n_articles"].sum().rename(columns={"n_articles": "month_n_articles"})
    out = out.merge(monthly_totals, on="month", how="left")
    out["article_share"] = out["n_articles"] / out["month_n_articles"]
    return out


def _zscore(series: pd.Series) -> pd.Series:
    std = series.std()
    if pd.isna(std) or std == 0:
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return (series - series.mean()) / std


def main() -> None:
    df, qa = _prepare_frame(PREDICTIONS_PATH)

    article_weighted = _weighted_monthly(df)
    source_balanced = _source_balanced_monthly(df)
    category_coverage = _category_coverage(df)

    monthly = article_weighted.merge(
        source_balanced,
        on="month",
        how="outer",
        suffixes=("_article_weighted", "_source_balanced"),
    ).sort_values("month").reset_index(drop=True)

    monthly["beni_index_article_weighted"] = _zscore(monthly["economic_share_article_weighted"])
    monthly["beni_index_source_balanced"] = _zscore(monthly["economic_share_source_balanced"])
    monthly["beni_index"] = monthly["beni_index_source_balanced"]

    monthly["month"] = pd.to_datetime(monthly["month"]).dt.strftime("%Y-%m-01")
    article_weighted["month"] = pd.to_datetime(article_weighted["month"]).dt.strftime("%Y-%m-01")
    source_balanced["month"] = pd.to_datetime(source_balanced["month"]).dt.strftime("%Y-%m-01")
    category_coverage["month"] = pd.to_datetime(category_coverage["month"]).dt.strftime("%Y-%m-01")

    source_coverage = (
        df.groupby(["month", "dataset_source"], as_index=False)
        .agg(
            n_articles=("article_id", "size"),
            n_economic=("economic_pred", "sum"),
            mean_prob=("economic_prob", "mean"),
            n_newspapers=("newspaper", "nunique"),
        )
        .sort_values(["month", "dataset_source"])
    )
    source_coverage["month"] = pd.to_datetime(source_coverage["month"]).dt.strftime("%Y-%m-01")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(OUT_INDEX, index=False)
    article_weighted.to_csv(OUT_ARTICLE_WEIGHTED, index=False)
    source_balanced.to_csv(OUT_SOURCE_BALANCED, index=False)
    source_coverage.to_csv(OUT_SOURCE_COVERAGE, index=False)
    category_coverage.to_csv(OUT_CATEGORY_COVERAGE, index=False)

    summary = {
        "predictions_path": str(PREDICTIONS_PATH),
        "output_index": str(OUT_INDEX),
        "raw_prediction_rows": int(qa["raw_rows"]),
        "duplicate_rows_flagged": int(qa["duplicate_rows_flagged"]),
        "rows_excluded_missing_required": int(qa["rows_excluded_missing_required"]),
        "duplicate_rows_excluded": int(qa["duplicate_rows_excluded"]),
        "rows_scored": int(len(df)),
        "months": int(monthly["month"].nunique()),
        "sources": int(df["newspaper"].nunique()),
        "dataset_sources": int(df["dataset_source"].nunique()),
        "categories": int(df["category_harmonised"].nunique()),
        "article_weighted_mean_share": round(float(article_weighted["economic_share"].mean()), 6),
        "source_balanced_mean_share": round(float(source_balanced["economic_share"].mean()), 6),
        "article_weighted_index_range": [
            round(float(monthly["beni_index_article_weighted"].min()), 6),
            round(float(monthly["beni_index_article_weighted"].max()), 6),
        ],
        "source_balanced_index_range": [
            round(float(monthly["beni_index_source_balanced"].min()), 6),
            round(float(monthly["beni_index_source_balanced"].max()), 6),
        ],
        "total_economic_predictions": int(df["economic_pred"].sum()),
        "source_coverage_rows": int(len(source_coverage)),
        "category_coverage_rows": int(len(category_coverage)),
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
