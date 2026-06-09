"""
Build LLM-calibrated BENI narrative index.

Loads the existing TF-IDF-based narrative index, applies calibration factors
from the LLM validation analysis, and produces an enhanced time series with
BENI index values and confidence intervals.

Usage:
    python3 beni/index/build_narrative_index.py
    python3 beni/index/build_narrative_index.py --export-csv
    python3 beni/index/build_narrative_index.py --export-all

Output:
    outputs/narrative_index_enhanced.csv   — Enhanced index with LLM calibration
    outputs/narrative_index_full.csv       — Full data with macro overlays (if available)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BENI_ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = BENI_ROOT / "experiment" / "outputs" / "index"
ANALYSIS_DIR = BENI_ROOT / "annotation" / "exports"
OUTPUT_DIR = BENI_ROOT / "index" / "outputs"
MACRO_DIR = BENI_ROOT / "data" / "raw" / "macro"


# ── Calibration from LLM Analysis ──────────────────────────────────────

def load_analysis_report(path: Path) -> dict | None:
    """Load analysis report with LLM-TF-IDF agreement metrics."""
    if not path.exists():
        print(f"  [WARN] Analysis report not found: {path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def compute_calibration_factors(report: dict) -> dict:
    """Compute LLM-based calibration factors from classification report.

    Uses the LLM-TF-IDF confusion matrix to compute:
    - calibration_factor: adjustment to apply to TF-IDF economic_share
    - precision_TF: how many TF-IDF Economic predictions were correct
    - recall_TF: what fraction of true Economic articles TF-IDF caught
    """
    cr = report.get("economic_relevance_agreement", {}).get("classification_report", {})
    econ_metrics = cr.get("Economic", {})
    prec = econ_metrics.get("precision", 0.5)
    rec = econ_metrics.get("recall", 0.5)

    # Calibration: TF-IDF tends to underpredict (19 vs 22)
    # calibrated_share = tfidf_share * (llm_recall / tfidf_recall)
    # But tfidf_recall is the same as rec above, and we need base-rate adjustment
    rel = report.get("economic_relevance_agreement", {})
    llm_econ = rel.get("llm_economic_count", 22)
    tfidf_econ = rel.get("tfidf_economic_count", 19)

    # Base-rate ratio: LLM sees more economic articles than TF-IDF
    base_rate_ratio = llm_econ / tfidf_econ if tfidf_econ > 0 else 1.0

    # TF-IDF precision: how reliable are TF-IDF Economic predictions
    # (proportion of TF-IDF Economic that are also LLM Economic)
    cm = rel.get("confusion_matrix", {})
    tp = cm.get("Economic", {}).get("Economic", 0)
    fp = cm.get("Not Economic", {}).get("Economic", 0)
    precision_tfidf = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    return {
        "llm_base_rate": rel.get("llm_base_rate", 0.073),
        "tfidf_base_rate": rel.get("tfidf_base_rate", 0.064),
        "base_rate_ratio": base_rate_ratio,
        "precision_tfidf": precision_tfidf,
        "recall_tfidf": rec,
        "cohens_kappa": rel.get("cohens_kappa", 0.0),
        "llm_economic_count": llm_econ,
        "tfidf_economic_count": tfidf_econ,
    }


# ── Narrative Index Construction ───────────────────────────────────────

def load_narrative_index(path: Path) -> pd.DataFrame:
    """Load existing TF-IDF narrative index."""
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df.sort_values("month").reset_index(drop=True)


def apply_calibration(idx: pd.DataFrame, cal: dict) -> pd.DataFrame:
    """Apply LLM calibration to TF-IDF narrative index."""
    df = idx.copy()
    base_col = "economic_share"
    cal_col = "economic_share_calibrated"

    # Rule of thumb calibration:
    # TF-IDF tends to miss some economic articles (recall=0.4091)
    # and has false positives (precision=0.4737)
    # Adjust the base rate: calibrated = share * (llm_ratio / precision ) * recall
    # Simpler: use base_rate_ratio to adjust the level
    df[cal_col] = df[base_col] * cal["base_rate_ratio"]

    # Clamp to [0, 1]
    df[cal_col] = df[cal_col].clip(0, 1)

    # Compute BENI index value: z-score normalized
    mean_share = df[cal_col].mean()
    std_share = df[cal_col].std()
    df["beni_index"] = (df[cal_col] - mean_share) / std_share if std_share > 0 else 0.0

    # Also keep raw BENI for comparison
    mean_raw = df[base_col].mean()
    std_raw = df[base_col].std()
    df["beni_index_raw"] = (df[base_col] - mean_raw) / std_raw if std_raw > 0 else 0.0

    # Confidence interval based on TF-IDF agreement
    # Use kappa-adjusted bounds
    kappa = cal.get("cohens_kappa", 0.4)
    ci_width = (1 - kappa) * 0.5  # wider CI for lower agreement
    df["ci_lower"] = (df[cal_col] - ci_width).clip(0, 1)
    df["ci_upper"] = (df[cal_col] + ci_width).clip(0, 1)

    # Monthly economic count
    df["n_economic_calibrated"] = (df["n_articles"] * df[cal_col]).round(0).astype(int)

    return df


def load_bis_fx(path: Path) -> pd.DataFrame | None:
    """Load BIS FX data (same parsing as correlate.py)."""
    try:
        df = pd.read_csv(path)
        df["month"] = pd.to_datetime(df["TIME_PERIOD"] + "-01")
        df = df[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "fx_bdt_usd"})
        return df.dropna()
    except Exception as e:
        print(f"  [WARN] Failed to load FX: {e}")
        return None


def _parse_imf_period(period: str) -> str:
    """Convert IMF TIME_PERIOD like '2020-M01' to '2020-01'."""
    parts = period.split("-M")
    return f"{parts[0]}-{parts[1].zfill(2)}"


def load_imf_cpi(path: Path) -> pd.DataFrame | None:
    """Load IMF CPI data (same parsing as correlate.py)."""
    try:
        df = pd.read_csv(path)
        df = df[df["OBS_VALUE"].notna()].copy()
        df["month"] = pd.to_datetime(df["TIME_PERIOD"].map(_parse_imf_period) + "-01")
        df = df[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "cpi_index"})
        return df
    except Exception as e:
        print(f"  [WARN] Failed to load CPI: {e}")
        return None


def load_macro_data(macro_dir: Path) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load macro indicators if available."""
    fx_path = macro_dir / "fx_bdt_usd_bis_eop_monthly.csv"
    cpi_path = macro_dir / "cpi_imf_bgd_index_monthly.csv"

    fx = load_bis_fx(fx_path) if fx_path.exists() else None
    cpi = load_imf_cpi(cpi_path) if cpi_path.exists() else None

    return fx, cpi


def load_correlations(path: Path) -> pd.DataFrame | None:
    """Load existing correlation results."""
    if path.exists():
        return pd.read_csv(path)
    return None


def build_index() -> dict:
    """Main pipeline: load, calibrate, export."""
    print("=" * 60)
    print("BENI Narrative Index Builder")
    print("=" * 60)

    # ── 1. Load existing index ──
    print("\n[1/4] Loading TF-IDF narrative index...")
    index_path = INDEX_DIR / "narrative_index.csv"
    if not index_path.exists():
        print(f"  [ERROR] Narrative index not found: {index_path}")
        sys.exit(1)

    idx = load_narrative_index(index_path)
    print(f"  Loaded: {len(idx)} months ({idx['month'].min().date()} to {idx['month'].max().date()})")

    # ── 2. Load LLM analysis report ──
    print("\n[2/4] Loading LLM validation analysis...")
    report_path = ANALYSIS_DIR / "analysis_report.json"
    report = load_analysis_report(report_path)

    cal = compute_calibration_factors(report) if report else {
        "base_rate_ratio": 1.0,
        "cohens_kappa": 0.0,
        "llm_base_rate": 0.073,
        "tfidf_base_rate": 0.064,
        "precision_tfidf": 0.0,
        "recall_tfidf": 0.0,
    }
    print(f"  LLM base rate:        {cal['llm_base_rate']:.2%}")
    print(f"  TF-IDF base rate:     {cal['tfidf_base_rate']:.2%}")
    print(f"  Base rate ratio:       {cal['base_rate_ratio']:.4f}")
    print(f"  TF-IDF precision:      {cal['precision_tfidf']:.2%}")
    print(f"  TF-IDF recall:         {cal['recall_tfidf']:.2%}")
    print(f"  Cohen's κ:             {cal['cohens_kappa']:.4f}")

    # ── 3. Apply calibration ──
    print("\n[3/4] Applying LLM calibration...")
    enhanced = apply_calibration(idx, cal)
    print(f"  Raw mean share:       {enhanced['economic_share'].mean():.2%}")
    print(f"  Calibrated mean share: {enhanced['economic_share_calibrated'].mean():.2%}")
    print(f"  BENI index range:     [{enhanced['beni_index'].min():.2f}, {enhanced['beni_index'].max():.2f}]")

    # ── 4. Load macro data if available ──
    print("\n[4/4] Loading macro indicators...")
    fx, cpi = load_macro_data(MACRO_DIR)
    if fx is not None:
        enhanced = enhanced.merge(fx, on="month", how="left")
        print(f"  FX data merged: {fx['month'].min().date()} – {fx['month'].max().date()}")
    else:
        print(f"  FX data not available at {MACRO_DIR}")

    if cpi is not None:
        enhanced = enhanced.merge(cpi, on="month", how="left")
        print(f"  CPI data merged: {cpi['month'].min().date()} – {cpi['month'].max().date()}")
    else:
        print(f"  CPI data not available at {MACRO_DIR}")

    # Load existing correlations
    corr = load_correlations(INDEX_DIR / "correlations.csv")
    if corr is not None:
        print(f"  Correlations loaded: {len(corr)} pairs")

    # ── Save ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Enhanced index with calibration
    enhanced_path = OUTPUT_DIR / "narrative_index_enhanced.csv"
    enhanced.to_csv(enhanced_path, index=False)
    print(f"\n  Enhanced index → {enhanced_path}")

    # Full data with macro
    full_path = OUTPUT_DIR / "narrative_index_full.csv"
    enhanced.to_csv(full_path, index=False)
    print(f"  Full data       → {full_path}")

    # Summary stats
    summary = {
        "period": {
            "start": enhanced["month"].min().isoformat(),
            "end": enhanced["month"].max().isoformat(),
            "n_months": len(enhanced),
        },
        "calibration": cal,
        "index_stats": {
            "mean_economic_share_raw": round(enhanced["economic_share"].mean(), 4),
            "mean_economic_share_calibrated": round(enhanced["economic_share_calibrated"].mean(), 4),
            "mean_beni_index_raw": round(enhanced["beni_index_raw"].mean(), 4),
            "mean_beni_index": round(enhanced["beni_index"].mean(), 4),
            "min_beni_index": round(enhanced["beni_index"].min(), 4),
            "max_beni_index": round(enhanced["beni_index"].max(), 4),
            "std_beni_index": round(enhanced["beni_index"].std(), 4),
        },
        "top_events": [
            {k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in row.items()}
            for row in enhanced.nlargest(5, "beni_index")[
                ["month", "beni_index", "economic_share_calibrated", "n_economic_calibrated"]
            ].to_dict(orient="records")
        ],
        "bottom_events": [
            {k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in row.items()}
            for row in enhanced.nsmallest(5, "beni_index")[
                ["month", "beni_index", "economic_share_calibrated", "n_economic_calibrated"]
            ].to_dict(orient="records")
        ],
    }

    summary_path = OUTPUT_DIR / "index_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  Summary         → {summary_path}")

    return summary


def print_summary(summary: dict) -> None:
    """Print a human-readable summary."""
    print("\n" + "=" * 60)
    print("BENI Index Summary")
    print("=" * 60)
    print(f"  Period: {summary['period']['start']} to {summary['period']['end']}")
    print(f"  Months: {summary['period']['n_months']}")
    print()
    print("  Calibration (LLM vs TF-IDF):")
    print(f"    Base rate ratio:       {summary['calibration']['base_rate_ratio']:.4f}")
    print(f"    TF-IDF precision:      {summary['calibration']['precision_tfidf']:.2%}")
    print(f"    TF-IDF recall:         {summary['calibration']['recall_tfidf']:.2%}")
    print(f"    Cohen's κ:             {summary['calibration']['cohens_kappa']:.4f}")
    print()
    print("  Index Statistics:")
    print(f"    Raw economic share:      {summary['index_stats']['mean_economic_share_raw']:.2%}")
    print(f"    Calibrated share:        {summary['index_stats']['mean_economic_share_calibrated']:.2%}")
    print(f"    BENI index (mean):       {summary['index_stats']['mean_beni_index']:.4f}")
    print(f"    BENI index (std):        {summary['index_stats']['std_beni_index']:.4f}")
    print(f"    BENI index range:        [{summary['index_stats']['min_beni_index']:.2f}, {summary['index_stats']['max_beni_index']:.2f}]")
    print()
    print("  Top 5 Narrative Intensity Months:")
    for ev in summary["top_events"]:
        print(f"    {ev['month']}: BENI={ev['beni_index']:.2f}  share={ev['economic_share_calibrated']:.1%}  n={ev['n_economic_calibrated']}")
    print()
    print("  Bottom 5 Narrative Intensity Months:")
    for ev in summary["bottom_events"]:
        print(f"    {ev['month']}: BENI={ev['beni_index']:.2f}  share={ev['economic_share_calibrated']:.1%}  n={ev['n_economic_calibrated']}")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build BENI narrative index")
    parser.add_argument("--export-csv", action="store_true", help="Export enhanced CSV")
    parser.add_argument("--export-all", action="store_true", help="Export all formats")
    args = parser.parse_args()

    summary = build_index()
    print_summary(summary)
