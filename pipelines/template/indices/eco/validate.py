#!/usr/bin/env python3
"""
[X]ENI — Economic Index Validator

Validate narrative index against macroeconomic indicators
(CPI, FX, reserves, etc.).

Usage:
    python validate.py --index eco_monthly_index.csv \\
        --macro data/macro_indicators.csv

Deliverable:
    - Validation report with correlation statistics
    - Significance tests and lead/lag analysis
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from pipelines.shared.io import ensure_dirs, read_csv_safe, write_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Columns to skip when identifying numeric indicator columns
_SKIP_COLS = frozenset({
    "month", "date", "year_month", "n_articles", "n_positive",
    "n_sources", "id", "article_id",
})


# ── Data loading ──────────────────────────────────────────────────────

def load_index(path: str) -> pd.DataFrame:
    """Load a monthly narrative index CSV.

    Args:
        path: Path to the index CSV.

    Returns:
        DataFrame with a ``month`` column.

    Raises:
        ValueError: If no date column can be identified.
    """
    logger.info("Loading index from %s", path)
    df = read_csv_safe(Path(path))
    logger.info("Loaded %d rows with columns: %s", len(df), list(df.columns))

    date_col = _resolve_date_column(df)
    df["month"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["month"]).sort_values("month").reset_index(drop=True)

    logger.info(
        "Index date range: %s to %s",
        df["month"].min().date(), df["month"].max().date(),
    )
    return df


def load_macro_data(path: str) -> pd.DataFrame:
    """Load macroeconomic indicators CSV.

    Args:
        path: Path to the macro indicators CSV.

    Returns:
        DataFrame with a ``month`` column.

    Raises:
        ValueError: If no date column can be identified.
    """
    logger.info("Loading macro data from %s", path)
    df = read_csv_safe(Path(path))
    logger.info("Loaded %d rows with columns: %s", len(df), list(df.columns))

    date_col = _resolve_date_column(df)
    df["month"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["month"]).sort_values("month").reset_index(drop=True)

    logger.info(
        "Macro date range: %s to %s",
        df["month"].min().date(), df["month"].max().date(),
    )
    return df


def _resolve_date_column(df: pd.DataFrame) -> str:
    """Find the most likely date column in a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Column name to use as date.

    Raises:
        ValueError: If no suitable column exists.
    """
    candidates = ["month", "date", "year_month", "timestamp", "period", "time"]
    for col in df.columns:
        if col.lower() in candidates:
            return col
    for col in df.columns:
        low = col.lower()
        if "date" in low or "month" in low or "time" in low:
            return col
    raise ValueError(
        f"No date column found. Expected one of: {candidates}. "
        f"Available columns: {list(df.columns)}"
    )


# ── Numeric column detection ──────────────────────────────────────────

def _numeric_indicator_columns(df: pd.DataFrame) -> list[str]:
    """Return names of numeric columns suitable for correlation analysis.

    Args:
        df: Input DataFrame.

    Returns:
        List of numeric column names, excluding date-like and count columns.
    """
    return [
        c for c in df.columns
        if c not in _SKIP_COLS
        and pd.api.types.is_numeric_dtype(df[c])
    ]


# ── Correlation logic ─────────────────────────────────────────────────

def compute_correlations(
    index_series: pd.Series,
    macro_series: pd.Series,
    name: str,
) -> dict[str, Any]:
    """Compute Pearson and Spearman correlations between two time series.

    Also computes first-differenced correlations (to remove shared trends)
    and cross-correlations at lags −3 … +3 months.

    Args:
        index_series: Index values.
        macro_series: Macro indicator values.
        name: Human-readable label for the correlation pair.

    Returns:
        Dictionary of correlation statistics.
    """
    # Remove NaN pairs
    valid = ~(index_series.isna() | macro_series.isna())
    x = index_series[valid].values.astype(float)
    y = macro_series[valid].values.astype(float)
    n = len(x)

    if n < 3:
        return {"indicator": name, "n": n, "error": "Insufficient observations (n < 3)"}

    # Level correlations
    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_r, spearman_p = stats.spearmanr(x, y)

    # First-differenced correlations
    x_diff = np.diff(x)
    y_diff = np.diff(y)
    n_diff = len(x_diff)

    if n_diff >= 3:
        pearson_r_diff, pearson_p_diff = stats.pearsonr(x_diff, y_diff)
        spearman_r_diff, spearman_p_diff = stats.spearmanr(x_diff, y_diff)
    else:
        pearson_r_diff = pearson_p_diff = None
        spearman_r_diff = spearman_p_diff = None

    # Cross-correlation at lags −3 … +3 months
    cross_corr: dict[str, float] = {}
    for lag in range(-3, 4):
        if lag < 0:
            xx = x[-lag:]
            yy = y[:lag]
        elif lag > 0:
            xx = x[:-lag]
            yy = y[lag:]
        else:
            xx, yy = x, y

        if len(xx) >= 5:
            lag_r, _ = stats.pearsonr(xx, yy)
            cross_corr[f"lag_{lag}"] = round(lag_r, 4)

    return {
        "indicator": name,
        "n": n,
        "n_diff": n_diff,
        "pearson_r": round(pearson_r, 4),
        "pearson_p": round(pearson_p, 6),
        "spearman_r": round(spearman_r, 4),
        "spearman_p": round(spearman_p, 6),
        "pearson_r_diff": (
            round(pearson_r_diff, 4) if pearson_r_diff is not None else None
        ),
        "pearson_p_diff": (
            round(pearson_p_diff, 6) if pearson_p_diff is not None else None
        ),
        "spearman_r_diff": (
            round(spearman_r_diff, 4) if spearman_r_diff is not None else None
        ),
        "spearman_p_diff": (
            round(spearman_p_diff, 6) if spearman_p_diff is not None else None
        ),
        "cross_correlation": cross_corr,
    }


def validate_index(
    index: pd.DataFrame,
    macro_data: pd.DataFrame,
) -> dict[str, Any]:
    """Validate a narrative index against macroeconomic indicators.

    Merges the two DataFrames on ``month`` and computes level and
    first-differenced correlations for every pair of numeric columns.

    Args:
        index: DataFrame with ``month`` and index value columns.
        macro_data: DataFrame with ``month`` and indicator columns.

    Returns:
        Validation report with correlation results and summary.

    Raises:
        ValueError: If no overlapping data or numeric columns exist.
    """
    index_cols = _numeric_indicator_columns(index)
    macro_cols = _numeric_indicator_columns(macro_data)

    logger.info("Index value columns: %s", index_cols)
    logger.info("Macro indicator columns: %s", macro_cols)

    if not index_cols:
        raise ValueError("No numeric index value columns found")
    if not macro_cols:
        raise ValueError("No numeric macro indicator columns found")

    # Merge on month
    merged = pd.merge(
        index, macro_data, on="month", how="inner",
        suffixes=("_index", "_macro"),
    )
    logger.info("Merged dataset: %d months", len(merged))

    if len(merged) < 3:
        raise ValueError(
            f"Insufficient overlapping observations: {len(merged)} (need ≥3)"
        )

    # Compute correlations for every pair
    correlations: list[dict[str, Any]] = []
    for index_col in index_cols:
        for macro_col in macro_cols:
            result = compute_correlations(
                merged[index_col],
                merged[macro_col],
                name=f"{index_col} vs {macro_col}",
            )
            correlations.append(result)

    # Summary
    significant = sum(
        1 for c in correlations
        if "error" not in c and c.get("pearson_p", 1) < 0.05
    )
    valid_pairs = sum(1 for c in correlations if "error" not in c)

    report: dict[str, Any] = {
        "n_overlapping_months": len(merged),
        "index_date_range": {
            "start": str(index["month"].min().date()),
            "end": str(index["month"].max().date()),
        },
        "macro_date_range": {
            "start": str(macro_data["month"].min().date()),
            "end": str(macro_data["month"].max().date()),
        },
        "index_columns": index_cols,
        "macro_columns": macro_cols,
        "correlations": correlations,
        "summary": {
            "total_pairs": len(correlations),
            "valid_pairs": valid_pairs,
            "significant_at_0_05": significant,
        },
    }

    return report


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Economic Narrative Index",
    )
    parser.add_argument(
        "--index", required=True,
        help="Monthly index CSV",
    )
    parser.add_argument(
        "--macro", required=True,
        help="Macroeconomic indicators CSV",
    )
    parser.add_argument(
        "--output", default="./",
        help="Output directory for validation report",
    )
    args = parser.parse_args()

    index = load_index(args.index)
    macro = load_macro_data(args.macro)
    report = validate_index(index, macro)

    out_dir = Path(args.output)
    ensure_dirs(out_dir)

    report_path = out_dir / "validation_report.json"
    write_json(report_path, report)
    logger.info("Validation report saved: %s", report_path)

    # Print summary to console
    logger.info(
        "Validation complete. %d correlation pairs computed.",
        report["summary"]["valid_pairs"],
    )
    logger.info(
        "Significant at p<0.05: %d / %d",
        report["summary"]["significant_at_0_05"],
        report["summary"]["total_pairs"],
    )

    for corr in report["correlations"]:
        if "error" not in corr:
            logger.info(
                "  %s: Pearson r=%.4f (p=%.4f), Spearman ρ=%.4f (p=%.4f)",
                corr["indicator"],
                corr["pearson_r"], corr["pearson_p"],
                corr["spearman_r"], corr["spearman_p"],
            )


if __name__ == "__main__":
    main()
