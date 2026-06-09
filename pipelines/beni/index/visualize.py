"""
Visualize the BENI narrative index with macro indicator overlays.

Produces publication-quality figures for the BENI time series,
calibration comparison, and macro correlation scatter plots.

Usage:
    python3 beni/index/visualize.py                          # Generate all plots
    python3 beni/index/visualize.py --skip-macro              # Skip macro overlays
    python3 beni/index/visualize.py --format png              # PNG output (default)
    python3 beni/index/visualize.py --format pdf              # Vector output
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

BENI_ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = BENI_ROOT / "index" / "outputs"
OUTPUT_DIR = INDEX_DIR / "figures"
MACRO_DIR = BENI_ROOT / "data" / "raw" / "macro"


# ── Style ───────────────────────────────────────────────────────────────

plt.rcParams.update({
    "figure.dpi": 150,
    "figure.figsize": (12, 5),
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "lines.linewidth": 1.5,
})

COLORS = {
    "beni": "#1f77b4",
    "beni_raw": "#7f7f7f",
    "beni_calibrated": "#2ca02c",
    "fx": "#d62728",
    "cpi": "#9467bd",
    "ci": "#1f77b4",
    "zero": "#cccccc",
    "negative": "#ff7f0e",
    "positive": "#2ca02c",
}

BANGLADESH_EVENTS = [
    ("2016-02-01", "Bangladesh Bank\nreserve heist"),
    ("2016-11-01", "India\ndemonetization"),
    ("2018-02-01", "BNP-led\nelection boycott"),
    ("2020-03-01", "COVID-19\npandemic begins"),
    ("2020-07-01", "COVID-19\nsecond wave"),
]


# ── Data Loaders ────────────────────────────────────────────────────────

def load_index(path: Path = INDEX_DIR / "narrative_index_enhanced.csv") -> pd.DataFrame:
    """Load enhanced narrative index."""
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df.sort_values("month").reset_index(drop=True)


def load_macro() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load macro data if available."""
    fx_path = MACRO_DIR / "fx_bdt_usd_bis_eop_monthly.csv"
    cpi_path = MACRO_DIR / "cpi_imf_bgd_index_monthly.csv"

    fx = cpi = None
    if fx_path.exists():
        raw = pd.read_csv(fx_path)
        raw["month"] = pd.to_datetime(raw["TIME_PERIOD"] + "-01")
        fx = raw[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "fx_bdt_usd"}).dropna()
    if cpi_path.exists():
        raw = pd.read_csv(cpi_path)
        raw = raw[raw["OBS_VALUE"].notna()].copy()
        raw["month"] = pd.to_datetime(raw["TIME_PERIOD"].str.replace("-M", "-", regex=False) + "-01")
        cpi = raw[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "cpi_index"})
    return fx, cpi


def load_summary(path: Path = INDEX_DIR / "index_summary.json") -> dict:
    """Load index summary."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


# ── Plotting Functions ──────────────────────────────────────────────────

def plot_beni_timeseries(
    idx: pd.DataFrame,
    output_dir: Path,
    fmt: str = "png",
) -> None:
    """Main BENI index time series with calibrated and raw comparison."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    # Panel 1: BENI Index
    ax1.plot(idx["month"], idx["beni_index"], color=COLORS["beni"], label="BENI (calibrated)", linewidth=1.8)
    ax1.plot(idx["month"], idx["beni_index_raw"], color=COLORS["beni_raw"], alpha=0.5, linewidth=1.0, label="BENI (raw TF-IDF)")
    ax1.axhline(y=0, color=COLORS["zero"], linestyle="--", linewidth=0.5)
    ax1.fill_between(idx["month"], idx["ci_lower"], idx["ci_upper"],
                     alpha=0.12, color=COLORS["ci"], label="95% CI (κ-adjusted)")
    ax1.set_ylabel("BENI (z-score)")
    ax1.set_title("Bangla Economic Narrative Index (2014–2020)")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Annotate key events
    ylim = ax1.get_ylim()
    y_range = ylim[1] - ylim[0]
    for date_str, label in BANGLADESH_EVENTS:
        date = pd.Timestamp(date_str)
        if date >= idx["month"].min() and date <= idx["month"].max():
            y_pos = ylim[1] - y_range * 0.05
            ax1.axvline(x=date, color=COLORS["negative"], alpha=0.3, linestyle=":", linewidth=0.8)
            ax1.annotate(label, xy=(date, y_pos), xytext=(date, y_pos + y_range * 0.1),
                        fontsize=7, ha="center", va="bottom",
                        arrowprops=dict(arrowstyle="->", color="gray", alpha=0.5))

    # Panel 2: Economic Share Comparison
    ax2.plot(idx["month"], idx["economic_share"], color=COLORS["beni_raw"], alpha=0.6, label="TF-IDF share")
    ax2.plot(idx["month"], idx["economic_share_calibrated"], color=COLORS["beni_calibrated"], linewidth=1.8, label="LLM-calibrated share")
    ax2.fill_between(idx["month"], idx["ci_lower"], idx["ci_upper"],
                     alpha=0.12, color=COLORS["ci"])
    ax2.set_ylabel("Economic article share")
    ax2.set_xlabel("Month")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()
    path = output_dir / f"beni_timeseries.{fmt}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_beni_with_macro(
    idx: pd.DataFrame,
    fx: pd.DataFrame | None,
    cpi: pd.DataFrame | None,
    output_dir: Path,
    fmt: str = "png",
) -> None:
    """Plot BENI overlaid with macro indicators (FX, CPI)."""
    merged = idx.copy()
    n_panels = 1
    if fx is not None and "fx_bdt_usd" not in merged.columns:
        merged = merged.merge(fx, on="month", how="left")
        n_panels += 1
    elif fx is not None and "fx_bdt_usd" in merged.columns:
        n_panels += 1  # column already present from build step
    if cpi is not None and "cpi_index" not in merged.columns:
        merged = merged.merge(cpi, on="month", how="left")
        n_panels += 1
    elif cpi is not None and "cpi_index" in merged.columns:
        n_panels += 1

    fig, axes = plt.subplots(n_panels, 1, figsize=(12, 3 * n_panels), sharex=True)
    if n_panels == 1:
        axes = [axes]

    panel_idx = 0

    # Panel 1: BENI index
    ax = axes[panel_idx]
    ax.plot(merged["month"], merged["beni_index"], color=COLORS["beni"], linewidth=1.5, label="BENI")
    ax.fill_between(merged["month"], merged["ci_lower"], merged["ci_upper"],
                    alpha=0.12, color=COLORS["ci"])
    ax.axhline(y=0, color=COLORS["zero"], linestyle="--", linewidth=0.5)
    ax.set_ylabel("BENI (z-score)")
    ax.set_title("BENI vs Macro Indicators")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    panel_idx += 1

    # Panel 2: FX
    if fx is not None:
        ax = axes[panel_idx]
        ax2 = ax.twinx()
        ax.plot(merged["month"], merged["beni_index"], color=COLORS["beni"], alpha=0.4, linewidth=0.8)
        ax2.plot(merged["month"], merged["fx_bdt_usd"], color=COLORS["fx"], linewidth=1.5, label="BDT/USD")
        ax2.set_ylabel("BDT per USD", color=COLORS["fx"])
        ax2.tick_params(axis="y", colors=COLORS["fx"])
        ax.set_ylabel("BENI (z-score)")
        ax.set_title("BENI vs BDT/USD Exchange Rate")
        ax.grid(True, alpha=0.3)
        panel_idx += 1

    # Panel 3: CPI
    if cpi is not None:
        ax = axes[panel_idx]
        ax2 = ax.twinx()
        ax.plot(merged["month"], merged["beni_index"], color=COLORS["beni"], alpha=0.4, linewidth=0.8)
        ax2.plot(merged["month"], merged["cpi_index"], color=COLORS["cpi"], linewidth=1.5, label="CPI")
        ax2.set_ylabel("CPI Index", color=COLORS["cpi"])
        ax2.tick_params(axis="y", colors=COLORS["cpi"])
        ax.set_ylabel("BENI (z-score)")
        ax.set_xlabel("Month")
        ax.set_title("BENI vs Consumer Price Index")
        ax.grid(True, alpha=0.3)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()
    path = output_dir / f"beni_with_macro.{fmt}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_correlation_scatter(
    idx: pd.DataFrame,
    fx: pd.DataFrame | None,
    cpi: pd.DataFrame | None,
    output_dir: Path,
    fmt: str = "png",
) -> None:
    """Scatter plots of BENI vs macro indicators with regression lines."""
    merged = idx.copy()
    if fx is not None and "fx_bdt_usd" not in merged.columns:
        merged = merged.merge(fx, on="month", how="inner")
    if cpi is not None and "cpi_index" not in merged.columns:
        merged = merged.merge(cpi, on="month", how="inner")

    n_plots = 0
    pairs = []
    if fx is not None and "fx_bdt_usd" in merged.columns:
        pairs.append(("fx_bdt_usd", "BDT/USD Exchange Rate"))
        n_plots += 1
    if cpi is not None and "cpi_index" in merged.columns:
        pairs.append(("cpi_index", "CPI Index"))
        n_plots += 1

    if n_plots == 0:
        print("  [SKIP] No macro data for scatter plots")
        return

    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))
    if n_plots == 1:
        axes = [axes]

    for ax, (col, label) in zip(axes, pairs):
        pair = merged[["beni_index", col]].dropna()
        x, y = pair["beni_index"], pair[col]

        # Scatter
        ax.scatter(x, y, alpha=0.5, s=20, color=COLORS["beni"])

        # Regression line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_sorted = np.sort(x)
        ax.plot(x_sorted, p(x_sorted), color=COLORS["negative"], linewidth=1.5, linestyle="--")

        # Pearson r
        from scipy.stats import pearsonr
        r, p_val = pearsonr(x, y)
        ax.text(0.05, 0.95, f"r = {r:.3f}\np = {p_val:.4f}",
                transform=ax.transAxes, fontsize=10, verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        ax.set_xlabel("BENI (z-score)")
        ax.set_ylabel(label)
        ax.set_title(f"BENI vs {label}")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"beni_correlation_scatter.{fmt}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_calibration_diagnostic(
    idx: pd.DataFrame,
    output_dir: Path,
    summary: dict,
    fmt: str = "png",
) -> None:
    """Diagnostic plot: raw vs calibrated share, z-score comparison."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # Panel 1: Raw vs calibrated share
    ax = axes[0]
    ax.scatter(idx["economic_share"], idx["economic_share_calibrated"],
               alpha=0.5, s=15, color=COLORS["beni"])
    lims = [0, 1]
    ax.plot(lims, lims, color=COLORS["zero"], linestyle="--", linewidth=1, label="1:1 line")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Raw TF-IDF share")
    ax.set_ylabel("LLM-calibrated share")
    ax.set_title("Calibration Effect")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Panel 2: Calibration ratio over time
    ax = axes[1]
    ax.plot(idx["month"], idx["economic_share_calibrated"] / idx["economic_share"],
            color=COLORS["beni_calibrated"], linewidth=1.5)
    ax.axhline(y=1.0, color=COLORS["zero"], linestyle="--", linewidth=0.5)
    ax.set_ylabel("Calibration ratio")
    ax.set_xlabel("Month")
    ax.set_title("Calibration Factor over Time")
    ax.grid(True, alpha=0.3)

    # Panel 3: Z-score alignment
    ax = axes[2]
    ax.scatter(idx["beni_index_raw"], idx["beni_index"],
               alpha=0.5, s=15, color=COLORS["beni"])
    lims = [min(idx["beni_index_raw"].min(), idx["beni_index"].min()) - 0.5,
            max(idx["beni_index_raw"].max(), idx["beni_index"].max()) + 0.5]
    ax.plot(lims, lims, color=COLORS["zero"], linestyle="--", linewidth=1, label="1:1 line")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Raw BENI (z-score)")
    ax.set_ylabel("Calibrated BENI (z-score)")
    ax.set_title("Index Alignment")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"beni_calibration_diagnostic.{fmt}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="BENI visualization")
    parser.add_argument("--format", choices=["png", "pdf", "svg"], default="png",
                        help="Output format (default: png)")
    parser.add_argument("--skip-macro", action="store_true",
                        help="Skip macro overlay plots")
    args = parser.parse_args()

    fmt = args.format
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("BENI Visualization")
    print("=" * 60)

    # Load data
    print("\n[1/3] Loading data...")
    idx = load_index()
    fx, cpi = (None, None) if args.skip_macro else load_macro()
    summary = load_summary()
    print(f"  Index:        {len(idx)} months")
    print(f"  FX data:      {'loaded' if fx is not None else 'skipped/missing'}")
    print(f"  CPI data:     {'loaded' if cpi is not None else 'skipped/missing'}")

    # Generate plots
    print("\n[2/3] Generating plots...")
    plot_beni_timeseries(idx, OUTPUT_DIR, fmt)
    plot_calibration_diagnostic(idx, OUTPUT_DIR, summary, fmt)

    if not args.skip_macro:
        plot_beni_with_macro(idx, fx, cpi, OUTPUT_DIR, fmt)
        plot_correlation_scatter(idx, fx, cpi, OUTPUT_DIR, fmt)

    # Report
    print("\n[3/3] Summary...")
    print(f"\n  Figures saved to: {OUTPUT_DIR}/")
    print(f"  Format: {fmt}")
    print(f"  Plots generated:")
    print(f"    - beni_timeseries.{fmt}           (main index + share)")
    print(f"    - beni_calibration_diagnostic.{fmt} (diagnostic panels)")
    if not args.skip_macro:
        print(f"    - beni_with_macro.{fmt}          (BENI vs FX/CPI)")
        print(f"    - beni_correlation_scatter.{fmt} (scatter + regression)")
    print("=" * 60)


if __name__ == "__main__":
    main()
