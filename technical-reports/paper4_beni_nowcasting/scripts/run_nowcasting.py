from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-beni-nowcasting")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENI_INDEX = PROJECT_ROOT / "beni" / "experiment" / "outputs" / "index" / "narrative_index.csv"
DEFAULT_CPI = PROJECT_ROOT / "beni" / "data" / "raw" / "macro" / "cpi_imf_bgd_index_monthly.csv"
DEFAULT_FX = PROJECT_ROOT / "beni" / "data" / "raw" / "macro" / "fx_bdt_usd_bis_eop_monthly.csv"
DEFAULT_RESULTS = PAPER_ROOT / "results"


@dataclass(frozen=True)
class ModelSpec:
    name: str
    features: list[str]
    estimator: str = "ridge"


def parse_imf_month(value: str) -> pd.Timestamp:
    year, month = value.split("-M")
    return pd.Timestamp(year=int(year), month=int(month), day=1)


def load_beni(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df.sort_values("month").reset_index(drop=True)


def load_cpi(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[df["OBS_VALUE"].notna()].copy()
    df["month"] = df["TIME_PERIOD"].map(parse_imf_month)
    df["cpi"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df = df[["month", "cpi"]].dropna().sort_values("month").reset_index(drop=True)
    df["inflation_yoy"] = 100 * (np.log(df["cpi"]) - np.log(df["cpi"].shift(12)))
    df["inflation_mom"] = 100 * (np.log(df["cpi"]) - np.log(df["cpi"].shift(1)))
    return df.dropna().reset_index(drop=True)


def load_fx(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["TIME_PERIOD"] + "-01")
    df["fx_bdt_usd"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df = df[["month", "fx_bdt_usd"]].dropna().sort_values("month").reset_index(drop=True)
    df["fx_change_yoy"] = 100 * (np.log(df["fx_bdt_usd"]) - np.log(df["fx_bdt_usd"].shift(12)))
    return df


def build_panel(beni_path: Path, cpi_path: Path, fx_path: Path) -> pd.DataFrame:
    beni = load_beni(beni_path)
    cpi = load_cpi(cpi_path)
    fx = load_fx(fx_path)
    panel = beni.merge(cpi, on="month", how="inner").merge(fx, on="month", how="left")
    panel = panel.sort_values("month").reset_index(drop=True)

    for lag in range(1, 4):
        panel[f"inflation_lag{lag}"] = panel["inflation_yoy"].shift(lag)
        panel[f"mom_lag{lag}"] = panel["inflation_mom"].shift(lag)
    panel["beni_change"] = panel["mean_prob"].diff()
    panel["share_change"] = panel["economic_share"].diff()
    panel["fx_change_yoy"] = panel["fx_change_yoy"].fillna(0)
    return panel.dropna(subset=["inflation_lag1", "inflation_lag2", "inflation_lag3", "beni_change"]).reset_index(drop=True)


def make_estimator(kind: str, seed: int):
    if kind == "rf":
        return RandomForestRegressor(
            n_estimators=300,
            max_depth=4,
            min_samples_leaf=3,
            random_state=seed,
        )
    return Ridge(alpha=1.0)


def recursive_forecast(
    panel: pd.DataFrame,
    spec: ModelSpec,
    horizon: int,
    train_end: str,
    test_start: str,
    test_end: str,
    seed: int,
) -> pd.DataFrame:
    rows = []
    train_end_ts = pd.Timestamp(train_end)
    test_start_ts = pd.Timestamp(test_start)
    test_end_ts = pd.Timestamp(test_end)

    for origin in panel["month"]:
        if origin < test_start_ts or origin > test_end_ts:
            continue
        target_month = origin + pd.DateOffset(months=horizon)
        if target_month not in set(panel["month"]):
            continue

        train = panel.copy()
        train["target_month"] = train["month"] + pd.DateOffset(months=horizon)
        train["target"] = train["inflation_yoy"].shift(-horizon)
        train = train[train["target_month"] <= origin - pd.DateOffset(months=1)]
        train = train[train["target_month"] >= panel["month"].min()]
        train = train.dropna(subset=spec.features + ["target"])

        if len(train) < 24:
            continue

        test = panel[panel["month"] == origin].copy()
        target = panel.loc[panel["month"] == target_month, "inflation_yoy"]
        if test.empty or target.empty:
            continue

        scaler = StandardScaler()
        x_train = scaler.fit_transform(train[spec.features])
        x_test = scaler.transform(test[spec.features])
        estimator = make_estimator(spec.estimator, seed)
        estimator.fit(x_train, train["target"])
        prediction = float(estimator.predict(x_test)[0])

        rows.append(
            {
                "model": spec.name,
                "horizon": horizon,
                "origin_month": origin,
                "target_month": target_month,
                "actual": float(target.iloc[0]),
                "prediction": prediction,
                "error": prediction - float(target.iloc[0]),
                "train_n": int(len(train)),
            }
        )
    return pd.DataFrame(rows)


def forecast_metrics(preds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, horizon), g in preds.groupby(["model", "horizon"]):
        actual_delta = g["actual"].diff()
        pred_delta = g["prediction"].diff()
        direction = (np.sign(actual_delta.dropna()) == np.sign(pred_delta.dropna())).mean()
        rows.append(
            {
                "model": model,
                "horizon": int(horizon),
                "n": int(len(g)),
                "rmse": float(np.sqrt(mean_squared_error(g["actual"], g["prediction"]))),
                "mae": float(mean_absolute_error(g["actual"], g["prediction"])),
                "direction_accuracy": float(direction) if not np.isnan(direction) else np.nan,
            }
        )
    out = pd.DataFrame(rows).sort_values(["horizon", "model"]).reset_index(drop=True)
    baseline = out[out["model"] == "M1_AR"][["horizon", "rmse"]].rename(columns={"rmse": "baseline_rmse"})
    out = out.merge(baseline, on="horizon", how="left")
    out["rmse_improvement_vs_ar"] = 100 * (out["baseline_rmse"] - out["rmse"]) / out["baseline_rmse"]
    return out.drop(columns=["baseline_rmse"])


def asymmetry_metrics(preds: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    accel = panel[["month", "inflation_mom"]].rename(columns={"month": "target_month"})
    merged = preds.merge(accel, on="target_month", how="left")
    merged["regime"] = np.where(
        merged["inflation_mom"] > 0.5,
        "acceleration",
        np.where(merged["inflation_mom"] < -0.2, "deceleration", "stable"),
    )
    rows = []
    for (model, horizon, regime), g in merged.groupby(["model", "horizon", "regime"]):
        if len(g) < 3:
            continue
        rows.append(
            {
                "model": model,
                "horizon": int(horizon),
                "regime": regime,
                "n": int(len(g)),
                "rmse": float(np.sqrt(mean_squared_error(g["actual"], g["prediction"]))),
                "mae": float(mean_absolute_error(g["actual"], g["prediction"])),
            }
        )
    return pd.DataFrame(rows).sort_values(["horizon", "regime", "model"]).reset_index(drop=True)


def feature_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    features = ["mean_prob", "economic_share", "beni_change", "share_change", "fx_change_yoy"]
    for feature in features:
        pair = panel[[feature, "inflation_yoy"]].dropna()
        if len(pair) < 5:
            continue
        r, p = pearsonr(pair[feature], pair["inflation_yoy"])
        rows.append({"feature": feature, "n": len(pair), "pearson_r": r, "pearson_p": p})
    return pd.DataFrame(rows)


def write_latex_table(df: pd.DataFrame, path: Path, float_format: str = "%.3f") -> None:
    safe = df.copy()
    safe.columns = [str(col).replace("_", "\\_") for col in safe.columns]
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("_", "\\_", regex=False)
    path.write_text(safe.to_latex(index=False, float_format=float_format, escape=False), encoding="utf-8")


def plot_nowcast(preds: pd.DataFrame, path: Path) -> None:
    h0 = preds[(preds["horizon"] == 0) & (preds["model"].isin(["M1_AR", "M2_AR_BENI"]))].copy()
    if h0.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 4.8))
    actual = h0[h0["model"] == "M1_AR"][["target_month", "actual"]].drop_duplicates()
    ax.plot(actual["target_month"], actual["actual"], color="black", linewidth=2, label="Actual CPI inflation")
    for model, color in [("M1_AR", "#777777"), ("M2_AR_BENI", "#1f77b4")]:
        g = h0[h0["model"] == model]
        ax.plot(g["target_month"], g["prediction"], linewidth=1.8, label=model, color=color)
    ax.set_title("Pseudo-real-time nowcast: CPI inflation")
    ax.set_ylabel("YoY inflation (%)")
    ax.set_xlabel("Target month")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_beni(panel: pd.DataFrame, path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    ax1.plot(panel["month"], panel["inflation_yoy"], color="black", label="CPI inflation")
    ax1.set_ylabel("YoY CPI inflation (%)")
    ax2 = ax1.twinx()
    ax2.plot(panel["month"], panel["mean_prob"], color="#1f77b4", alpha=0.8, label="BENI mean probability")
    ax2.set_ylabel("BENI mean economic probability")
    ax1.set_title("BENI and CPI inflation")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, frameon=False, loc="upper left")
    ax1.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper 4 BENI inflation nowcasting analysis")
    parser.add_argument("--beni-index", type=Path, default=DEFAULT_BENI_INDEX)
    parser.add_argument("--cpi", type=Path, default=DEFAULT_CPI)
    parser.add_argument("--fx", type=Path, default=DEFAULT_FX)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--train-end", default="2017-12-01")
    parser.add_argument("--test-start", default="2018-01-01")
    parser.add_argument("--test-end", default="2020-12-01")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    tables_dir = args.results_dir / "tables"
    figures_dir = args.results_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    panel = build_panel(args.beni_index, args.cpi, args.fx)
    model_specs = [
        ModelSpec("M1_AR", ["inflation_lag1", "inflation_lag2", "inflation_lag3"]),
        ModelSpec("M2_AR_BENI", ["inflation_lag1", "inflation_lag2", "inflation_lag3", "mean_prob", "economic_share"]),
        ModelSpec("M3_AR_BENI_FX", ["inflation_lag1", "inflation_lag2", "inflation_lag3", "mean_prob", "economic_share", "fx_change_yoy"]),
        ModelSpec("M4_RF_BENI", ["inflation_lag1", "inflation_lag2", "inflation_lag3", "mean_prob", "economic_share", "beni_change", "share_change", "fx_change_yoy"], "rf"),
    ]
    horizons = [0, 1, 3]

    all_preds = []
    for horizon in horizons:
        for spec in model_specs:
            all_preds.append(
                recursive_forecast(
                    panel,
                    spec,
                    horizon,
                    args.train_end,
                    args.test_start,
                    args.test_end,
                    args.seed,
                )
            )
    preds = pd.concat(all_preds, ignore_index=True)
    metrics = forecast_metrics(preds)
    asymmetry = asymmetry_metrics(preds, panel)
    corr = feature_correlations(panel)

    preds.to_csv(tables_dir / "forecast_predictions.csv", index=False)
    metrics.to_csv(tables_dir / "forecast_metrics.csv", index=False)
    asymmetry.to_csv(tables_dir / "asymmetry_metrics.csv", index=False)
    corr.to_csv(tables_dir / "feature_correlations.csv", index=False)
    write_latex_table(metrics, tables_dir / "forecast_metrics.tex")
    write_latex_table(asymmetry, tables_dir / "asymmetry_metrics.tex")
    write_latex_table(corr, tables_dir / "feature_correlations.tex")

    plot_nowcast(preds, figures_dir / "nowcast_actual_vs_predicted.png")
    plot_beni(panel, figures_dir / "beni_vs_inflation.png")

    summary = {
        "sample": {
            "panel_months": int(len(panel)),
            "panel_start": str(panel["month"].min().date()),
            "panel_end": str(panel["month"].max().date()),
            "test_start": args.test_start,
            "test_end": args.test_end,
        },
        "inputs": {
            "beni_index": str(args.beni_index),
            "cpi": str(args.cpi),
            "fx": str(args.fx),
        },
        "best_by_horizon": metrics.sort_values("rmse").groupby("horizon").head(1).to_dict(orient="records"),
    }
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
