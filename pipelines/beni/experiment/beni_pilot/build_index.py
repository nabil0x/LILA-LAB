from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast

from config import ExperimentConfig
from utils import zip_outputs


def parse_index_args() -> tuple[ExperimentConfig, bool, str]:
    parser = argparse.ArgumentParser(description="Build BENI narrative index.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Kaggle data directory (e.g. /kaggle/input/beni-data). Overrides potrika, model, and output paths.",
    )
    parser.add_argument(
        "--model-type",
        choices=["tfidf", "banglabert"],
        default="tfidf",
        help="Model to use: tfidf (baseline) or banglabert (fine-tuned transformer, must be trained first).",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Zip outputs/ directory on completion (for easy download from Kaggle).",
    )
    args, _ = parser.parse_known_args()
    if args.data_dir is not None:
        dd = args.data_dir
        if args.model_type == "banglabert":
            cfg = ExperimentConfig(
                potrika_dir=dd / "potrika",
                model_dir=Path("/kaggle/working/outputs/models"),
                output_dir=Path("/kaggle/working/outputs"),
                macro_dir=dd / "macro",
                banglabert_dir=Path("/kaggle/working/banglabert"),
            )
        else:
            cfg = ExperimentConfig(
                potrika_dir=dd / "potrika",
                model_dir=dd / "models",
                output_dir=Path("/kaggle/working/outputs"),
                macro_dir=dd / "macro",
            )
    else:
        cfg = ExperimentConfig()
    return cfg, args.zip, args.model_type


def _predict_tfidf(df: pd.DataFrame, config: ExperimentConfig) -> pd.DataFrame:
    model_path = config.model_dir / "economic_potrika-timeseries_tfidf_logreg.joblib"
    print(f"Loading TF-IDF model: {model_path}", flush=True)
    pipeline = joblib.load(str(model_path))
    probs = pipeline.predict_proba(df["text_norm"].tolist())
    df["economic_prob"] = probs[:, 1]
    return df


def _predict_banglabert(df: pd.DataFrame, config: ExperimentConfig) -> pd.DataFrame:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)

    model_name = "banglabert_economic_potrika-timeseries"
    model_path = config.model_dir / model_name
    print(f"Loading fine-tuned BanglaBERT from: {model_path}", flush=True)
    tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
    model = ElectraForSequenceClassification.from_pretrained(str(model_path))
    model.to(device)
    model.eval()

    from banglabert import BanglaBERTDataset

    dataset = BanglaBERTDataset(
        texts=df["text_norm"].tolist(),
        labels=[0] * len(df),
        tokenizer=tokenizer,
        config=config,
    )
    loader = DataLoader(
        dataset,
        batch_size=config.banglabert_batch_size,
        shuffle=False,
        num_workers=0,
    )

    all_probs: list[np.ndarray] = []
    n_batches = len(loader)
    print(f"Running BanglaBERT predictions on {len(df)} articles ({n_batches} batches)...", flush=True)
    with torch.no_grad():
        for i, batch in enumerate(loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=-1)
            all_probs.extend(probs.cpu().numpy())
            if (i + 1) % 100 == 0:
                print(f"  batch {i + 1}/{n_batches}", flush=True)

    df["economic_prob"] = np.array(all_probs)[:, 1]
    return df


def main() -> None:
    config, do_zip, model_type = parse_index_args()
    output_dir = config.output_dir / "index"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Import lazily so this script can run standalone
    from data import load_potrika_timeseries

    print("Loading potrika timeseries...", flush=True)
    splits = load_potrika_timeseries(config)
    df = pd.concat([splits["train"], splits["val"], splits["test"]], ignore_index=True)
    df = df.sort_values("publication_date").reset_index(drop=True)
    print(f"Total articles: {len(df)}", flush=True)
    print(f"Date range: {df['publication_date'].min()} to {df['publication_date'].max()}", flush=True)

    # --- Predict ---
    print(f"Running predictions with {model_type}...", flush=True)
    if model_type == "banglabert":
        df = _predict_banglabert(df, config)
    else:
        df = _predict_tfidf(df, config)

    df["economic_pred"] = (df["economic_prob"] > 0.5).astype(int)

    n_economic = df["economic_pred"].sum()
    print(f"Predicted economic: {n_economic}/{len(df)} ({n_economic / len(df) * 100:.1f}%)", flush=True)

    # --- Save full predictions ---
    full_out = output_dir / "full_predictions.parquet"
    cols_out = ["publication_date", "economic_prob", "economic_pred"]
    df[cols_out].to_parquet(str(full_out), index=False)
    print(f"Full predictions saved: {full_out}", flush=True)

    # --- Aggregate by month ---
    df["year_month"] = df["publication_date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("year_month", sort=True)
        .agg(
            n_articles=("economic_prob", "count"),
            mean_prob=("economic_prob", "mean"),
            economic_share=("economic_pred", "mean"),
            n_economic=("economic_pred", "sum"),
        )
        .reset_index()
    )
    monthly["month"] = pd.to_datetime(monthly["year_month"] + "-01")
    monthly = monthly[["month", "n_articles", "mean_prob", "economic_share", "n_economic"]]

    print(f"Monthly index: {len(monthly)} months", flush=True)
    print(monthly.tail(), flush=True)

    # --- Save monthly index ---
    index_path = output_dir / "narrative_index.csv"
    monthly.to_csv(index_path, index=False)
    print(f"Narrative index saved: {index_path}", flush=True)

    # --- Quick stats ---
    print("\n=== BENI Narrative Index Summary ===", flush=True)
    print(f"  Period: {monthly['month'].min().date()} to {monthly['month'].max().date()}", flush=True)
    print(f"  Months: {len(monthly)}", flush=True)
    print(f"  Mean monthly economic share: {monthly['economic_share'].mean():.3f}", flush=True)
    print(f"  Min share: {monthly['economic_share'].min():.3f} ({monthly.loc[monthly['economic_share'].idxmin(), 'month'].date()})", flush=True)
    print(f"  Max share: {monthly['economic_share'].max():.3f} ({monthly.loc[monthly['economic_share'].idxmax(), 'month'].date()})", flush=True)

    if do_zip:
        zip_outputs(config.output_dir, "beni_index")


if __name__ == "__main__":
    main()
