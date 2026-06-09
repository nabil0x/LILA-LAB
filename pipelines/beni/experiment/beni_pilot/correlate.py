from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import pearsonr, spearmanr

from config import ExperimentConfig
from utils import zip_outputs


def _parse_imf_period(period: str) -> str:
    """Convert IMF TIME_PERIOD like '2020-M01' → '2020-01'."""
    parts = period.split("-M")
    return f"{parts[0]}-{parts[1].zfill(2)}"


def load_bis_fx(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["TIME_PERIOD"] + "-01")
    df = df[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "fx_bis"})
    return df.dropna()


def load_imf_cpi(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["OBS_VALUE"].notna()].copy()
    df["month"] = pd.to_datetime(df["TIME_PERIOD"].map(_parse_imf_period) + "-01")
    df = df[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "cpi"})
    return df


def load_imf_fx(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["TIME_PERIOD"].map(_parse_imf_period) + "-01")
    df = df[["month", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "fx_imf"})
    return df.dropna()


def load_reserves(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[["year", "reserves_usd"]]


def make_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    monthly = monthly.copy()
    monthly["year"] = monthly["month"].dt.year
    return monthly.groupby("year").mean(numeric_only=True).reset_index()


def compute_correlations(
    merged: pd.DataFrame, x_col: str, y_cols: list[str], label: str
) -> list[dict]:
    rows = []
    for y in y_cols:
        pair = merged[[x_col, y]].dropna()
        n = len(pair)
        if n < 5:
            continue
        r_p, p_p = pearsonr(pair[x_col], pair[y])
        r_s, p_s = spearmanr(pair[x_col], pair[y])
        rows.append(
            {
                "frequency": label,
                "x": x_col,
                "y": y,
                "n": n,
                "pearson_r": round(r_p, 4),
                "pearson_p": round(p_p, 4),
                "spearman_r": round(r_s, 4),
                "spearman_p": round(p_s, 4),
            }
        )
    return rows


def _parse_correlate_args() -> tuple[ExperimentConfig, bool]:
    parser = argparse.ArgumentParser(description="Correlate narrative index with macro indicators.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Kaggle data directory (e.g. /kaggle/input/beni-data). Overrides macro and output paths.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Zip outputs/ directory on completion (for easy download from Kaggle).",
    )
    args, _ = parser.parse_known_args()
    if args.data_dir is not None:
        dd = args.data_dir
        cfg = ExperimentConfig(
            macro_dir=dd / "macro",
            output_dir=Path("/kaggle/working/outputs"),
        )
    else:
        cfg = ExperimentConfig()
    return cfg, args.zip


def main() -> None:
    config, do_zip = _parse_correlate_args()

    # --- 1. Load narrative index ---
    index_path = config.output_dir / "index" / "narrative_index.csv"
    idx = pd.read_csv(index_path)
    idx["month"] = pd.to_datetime(idx["month"])
    print(f"Narrative index: {len(idx)} months ({idx['month'].min().date()} to {idx['month'].max().date()})", flush=True)

    # --- 2. Load macro series ---
    macro_dir = config.macro_dir.resolve()
    bis_fx = load_bis_fx(macro_dir / "fx_bdt_usd_bis_eop_monthly.csv")
    imf_cpi = load_imf_cpi(macro_dir / "cpi_imf_bgd_index_monthly.csv")
    imf_fx = load_imf_fx(macro_dir / "fx_bdt_usd_imf_eop_monthly.csv")
    reserves = load_reserves(macro_dir / "reserves_wb_annual.csv")

    print(f"BIS FX:       {len(bis_fx)} months ({bis_fx['month'].min().date()} – {bis_fx['month'].max().date()})", flush=True)
    print(f"IMF CPI:      {len(imf_cpi)} months ({imf_cpi['month'].min().date()} – {imf_cpi['month'].max().date()})", flush=True)

    # NOTE: IMF FX data is loaded for reference only — it is IDENTICAL to BIS FX
    # in the 2014-2020 period (max diff < 1e-7). Including both would produce
    # redundant duplicate correlations. BIS FX is used as the primary source.
    print(f"IMF FX:       {len(imf_fx)} months ({imf_fx['month'].min().date()} – {imf_fx['month'].max().date()})  [SKIPPED — identical to BIS in index period]", flush=True)
    print(f"Reserves:     {len(reserves)} years", flush=True)

    # --- 3. Merge monthly ---
    monthly = idx.merge(bis_fx, on="month", how="inner")
    monthly = monthly.merge(imf_cpi, on="month", how="inner")
    monthly = monthly.sort_values("month").reset_index(drop=True)
    print(f"\nMerged monthly: {len(monthly)} months ({monthly['month'].min().date()} – {monthly['month'].max().date()})", flush=True)

    # --- 4. Correlations: contemporaneous ---
    results = []
    macro_cols = [c for c in ["fx_bis", "cpi"] if c in monthly.columns]
    results += compute_correlations(monthly, "economic_share", macro_cols, "monthly_contemp")
    results += compute_correlations(monthly, "mean_prob", macro_cols, "monthly_contemp")

    # --- 5. First-differenced correlations (detrended) ---
    diffed = monthly.copy()
    diff_cols = ["economic_share", "mean_prob"] + macro_cols
    for c in diff_cols:
        diffed[f"{c}_d1"] = diffed[c].diff()
    diffed = diffed.dropna().reset_index(drop=True)
    d1_cols = [f"{c}_d1" for c in diff_cols]
    print(f"\nDifferenced monthly: {len(diffed)} obs ({diffed['month'].min().date()} – {diffed['month'].max().date()})", flush=True)

    results += compute_correlations(diffed, "economic_share_d1", [c for c in d1_cols if c.startswith("fx_") or c.startswith("cpi")], "monthly_diff_contemp")
    results += compute_correlations(diffed, "mean_prob_d1", [c for c in d1_cols if c.startswith("fx_") or c.startswith("cpi")], "monthly_diff_contemp")

    for lag in [1, 3, 6]:
        shifted = diffed.copy()
        for mc in d1_cols:
            if mc in ["economic_share_d1", "mean_prob_d1"]:
                continue
            shifted[f"{mc}_lag{lag}"] = shifted[mc].shift(-lag)
        lag_cols = [f"{c}_d1_lag{lag}" for c in macro_cols]
        results += compute_correlations(shifted, "economic_share_d1", lag_cols, f"monthly_diff_lead{lag}m")
        results += compute_correlations(shifted, "mean_prob_d1", lag_cols, f"monthly_diff_lead{lag}m")

    # --- 6. Correlations: narrative leads macro by 1, 3, 6 months ---
    for lag in [1, 3, 6]:
        shifted = monthly.copy()
        for mc in macro_cols:
            shifted[f"{mc}_lag{lag}"] = shifted[mc].shift(-lag)
        lag_cols = [f"{c}_lag{lag}" for c in macro_cols]
        results += compute_correlations(shifted, "economic_share", lag_cols, f"monthly_lead{lag}m")
        results += compute_correlations(shifted, "mean_prob", lag_cols, f"monthly_lead{lag}m")

    # --- 6. Annual correlation with reserves ---
    annual_idx = make_annual(monthly)
    annual = annual_idx.merge(reserves, on="year", how="inner")
    print(f"Annual merge: {len(annual)} years ({annual['year'].min()} – {annual['year'].max()})", flush=True)
    results += compute_correlations(annual, "economic_share", ["reserves_usd"], "annual")
    results += compute_correlations(annual, "mean_prob", ["reserves_usd"], "annual")

    # --- 7. Save results ---
    out_path = config.output_dir / "index" / "correlations.csv"
    out_df = pd.DataFrame(results)
    out_df.to_csv(out_path, index=False)
    print(f"\nCorrelations saved: {out_path}", flush=True)
    print(f"Total correlation pairs: {len(out_df)}", flush=True)

    # --- 8. Print summary ---
    print("\n=== Correlation Results ===", flush=True)
    for _, row in out_df.iterrows():
        p_star = ""
        if row["pearson_p"] < 0.01:
            p_star = "**"
        elif row["pearson_p"] < 0.05:
            p_star = "*"
        print(
            f'  [{row["frequency"]:20s}] {row["x"]:15s} vs {row["y"]:12s}  '
            f'r={row["pearson_r"]:7.4f}{p_star}  (p={row["pearson_p"]:.4f})  n={row["n"]}',
            flush=True,
        )

    if do_zip:
        zip_outputs(config.output_dir, "beni_correlate")


if __name__ == "__main__":
    main()
