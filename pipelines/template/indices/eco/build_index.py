#!/usr/bin/env python3
"""
[X]ENI — Economic Narrative Index Builder

Aggregate article-level LLM predictions into monthly economic narrative index.
Adapted from BENI's build_narrative_index.py.

Usage:
    python build_index.py --predictions ../../experiment/outputs/predictions.csv \\
        --output ./

Deliverable:
    - Monthly economic narrative index CSV
    - Ready for validation against macroeconomic indicators
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from pipelines.shared.io import ensure_dirs, read_csv_safe, write_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Data loading ──────────────────────────────────────────────────────

def load_predictions(path: str) -> pd.DataFrame:
    """Load article-level predictions from a CSV file.

    Automatically detects and parses the date column.  Expected columns
    include ``article_id``, a date column, and prediction or probability
    columns.

    Args:
        path: Path to predictions CSV.

    Returns:
        DataFrame with a standardised ``date`` column.

    Raises:
        ValueError: If no date-like column can be identified.
    """
    logger.info("Loading predictions from %s", path)
    df = read_csv_safe(Path(path))
    logger.info("Loaded %d rows with columns: %s", len(df), list(df.columns))

    # Identify date column
    date_candidates = [
        "date", "publication_date", "month", "year_month", "timestamp",
    ]
    date_col: str | None = next(
        (c for c in df.columns if c.lower() in date_candidates),
        None,
    )
    if date_col is None:
        date_col = next(
            (c for c in df.columns if "date" in c.lower() or "time" in c.lower()),
            None,
        )
    if date_col is None:
        raise ValueError(
            f"No date column found. Expected one of: {date_candidates}. "
            f"Available columns: {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    n_invalid = df["date"].isna().sum()
    if n_invalid:
        logger.warning(
            "%d rows have invalid dates and will be dropped", n_invalid,
        )
        df = df.dropna(subset=["date"])

    logger.info("Using date column: '%s'", date_col)
    return df


# ── Column normalisation ──────────────────────────────────────────────

def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map variant prediction column names to a standard set.

    Handles common naming variations so the downstream aggregation logic
    is simpler.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with renamed columns.
    """
    mapping = {
        "prob": "probability",
        "economic_prob": "probability",
        "prediction_probability": "probability",
        "economic_relevance_prob": "probability",
        "economic_pred": "prediction",
        "economic_relevance_pred": "prediction",
        "economic_relevance": "relevance",
        "source": "source",
        "newspaper": "source",
        "publication": "source",
    }
    df = df.copy()
    for old, new in mapping.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    return df


# ── Index construction ────────────────────────────────────────────────

def build_monthly_index(predictions_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate article-level predictions into a monthly narrative index.

    Steps:
        1. Normalise column names.
        2. Group articles by ``year_month``.
        3. Compute mean probability / economic share per month.
        4. Apply source-weighting normalisation if a ``source`` column exists.

    Args:
        predictions_df: DataFrame with at least ``date`` and prediction columns.

    Returns:
        DataFrame with one row per month and columns for mean probability,
        article count, economic share, and (optionally) source-weighted
        probability.
    """
    df = normalise_columns(predictions_df)

    # Create year-month grouping column
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    # Build aggregation specification dynamically
    agg_spec: dict[str, tuple[str, str]] = {
        "n_articles": ("date", "count"),
    }

    if "probability" in df.columns:
        agg_spec["mean_probability"] = ("probability", "mean")
        agg_spec["median_probability"] = ("probability", "median")
        agg_spec["std_probability"] = ("probability", "std")

    if "prediction" in df.columns:
        agg_spec["n_positive"] = ("prediction", "sum")

    # Group and aggregate
    monthly = (
        df.groupby("year_month", sort=True)
        .agg(**agg_spec)
        .reset_index()
    )

    # Economic share (fraction of articles predicted as positive)
    if "n_positive" in monthly.columns:
        monthly["economic_share"] = (
            monthly["n_positive"] / monthly["n_articles"]
        ).round(4)

    # Source-weighting normalisation
    source_col: str | None = (
        "source" if "source" in df.columns else None
    )
    if source_col is not None and "probability" in df.columns:
        logger.info(
            "Applying source-weighting normalisation using '%s'", source_col,
        )
        # Per-source, per-month mean probability
        source_monthly = (
            df.groupby(["year_month", source_col])["probability"]
            .mean()
            .reset_index(name="source_mean_prob")
        )
        # Average across sources (each source contributes equally)
        source_weighted = (
            source_monthly.groupby("year_month")["source_mean_prob"]
            .mean()
            .reset_index(name="source_weighted_probability")
        )
        monthly = monthly.merge(source_weighted, on="year_month", how="left")

    # Add a proper month-start date column
    monthly["month"] = pd.to_datetime(monthly["year_month"] + "-01")
    monthly = monthly.sort_values("month").reset_index(drop=True)

    logger.info("Built monthly index with %d months", len(monthly))
    logger.info(
        "Date range: %s to %s",
        monthly["month"].min().date(),
        monthly["month"].max().date(),
    )

    return monthly


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Economic Narrative Index",
    )
    parser.add_argument(
        "--predictions", required=True,
        help="Article-level predictions CSV",
    )
    parser.add_argument(
        "--output", default="./",
        help="Output directory for index files",
    )
    args = parser.parse_args()

    predictions = load_predictions(args.predictions)
    index = build_monthly_index(predictions)

    out_dir = Path(args.output)
    ensure_dirs(out_dir)

    # Save monthly index CSV
    index_path = out_dir / "eco_monthly_index.csv"
    index.to_csv(index_path, index=False)
    logger.info("Index saved: %s", index_path)

    # Save summary statistics
    summary: dict[str, Any] = {
        "n_months": len(index),
        "date_range": {
            "start": str(index["month"].min().date()),
            "end": str(index["month"].max().date()),
        },
        "total_articles": int(index["n_articles"].sum()),
    }

    if "economic_share" in index.columns:
        summary["mean_economic_share"] = round(
            float(index["economic_share"].mean()), 4,
        )
        summary["min_economic_share"] = round(
            float(index["economic_share"].min()), 4,
        )
        summary["max_economic_share"] = round(
            float(index["economic_share"].max()), 4,
        )

    summary_path = out_dir / "index_summary.json"
    write_json(summary_path, summary)
    logger.info("Summary saved: %s", summary_path)

    logger.info("Index built: %d months", len(index))
    logger.info("Deliverable: monthly index CSV ready for validation.")


if __name__ == "__main__":
    main()
