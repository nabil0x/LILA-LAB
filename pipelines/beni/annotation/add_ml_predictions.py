"""
Add ML pre-labels to the 300-article annotation batch.

Two models available:
  1. TF-IDF + Logistic Regression (trained on Potrika categories, 91.7% accuracy)
  2. BanglaBERT (fine-tuned on keyword labels)

The TF-IDF model produces better-calibrated pre-labels for economic relevance
detection on this data. BanglaBERT was trained on 4.4% base-rate keyword data
and tends to under-predict.

Usage:
    python3 add_ml_predictions.py --model tfidf
    python3 add_ml_predictions.py --model banglabert --append

    Use --append to keep existing predictions (e.g. TF-IDF) and add a new model.
    Without --append, existing predictions are overwritten.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from joblib import load as joblib_load
from torch.utils.data import DataLoader
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast

BENI_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = BENI_ROOT / "experiment"
BENI_PILOT = EXPERIMENT_DIR / "beni_pilot"

sys.path.insert(0, str(BENI_PILOT))

from banglabert import BanglaBERTDataset, _predict

BATCH_PATH = Path(__file__).parent / "exports" / "beni_300_batch.json"
OUTPUT_PATH = Path(__file__).parent / "exports" / "beni_300_batch_with_ml.json"
TFIDF_MODEL_PATH = (
    EXPERIMENT_DIR / "outputs" / "models" / "economic_potrika-timeseries_tfidf_logreg.joblib"
)
BANGALABERT_MODEL_PATH = (
    EXPERIMENT_DIR / "outputs" / "models" / "banglabert_bnwp_prelabel"
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict_tfidf(texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
    pipe = joblib_load(TFIDF_MODEL_PATH)
    probs = pipe.predict_proba(texts)
    if probs.shape[1] == 2:
        econ_probs = probs[:, 1]
    else:
        econ_probs = probs[:, 0]
    preds = (econ_probs >= 0.5).astype(int)
    confs = np.where(preds == 1, econ_probs, 1 - econ_probs)
    return preds, np.column_stack((1 - econ_probs, econ_probs))


def predict_banglabert(texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
    tokenizer = ElectraTokenizerFast.from_pretrained(str(BANGALABERT_MODEL_PATH))
    model = ElectraForSequenceClassification.from_pretrained(str(BANGALABERT_MODEL_PATH))
    model.to(DEVICE)
    model.eval()

    class Config:
        banglabert_max_len = 128
        banglabert_batch_size = 8

    config = Config()
    dataset = BanglaBERTDataset(texts, [0] * len(texts), tokenizer, config)
    loader = DataLoader(dataset, batch_size=8, shuffle=False)
    preds, probs, _ = _predict(model, loader, DEVICE)
    return preds, probs


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["tfidf", "banglabert"], default="tfidf")
    parser.add_argument("--append", action="store_true", help="Append to existing predictions instead of overwriting")
    args = parser.parse_args()

    print(f"Model: {args.model}" + (" (append mode)" if args.append else ""))

    source_path = OUTPUT_PATH if args.append and OUTPUT_PATH.exists() else BATCH_PATH
    tasks = json.loads(source_path.read_text(encoding="utf-8"))
    if args.append:
        print(f"Loaded {len(tasks)} articles from existing {OUTPUT_PATH.name} (append mode)")
    else:
        print(f"Loaded {len(tasks)} articles from {BATCH_PATH.name}")
    texts = [t["data"]["text"][:5000] for t in tasks]
    print(f"Loaded {len(texts)} articles")

    if args.model == "tfidf":
        preds, probs = predict_tfidf(texts)
        model_version = "tfidf_potrika_timeseries"
    else:
        preds, probs = predict_banglabert(texts)
        model_version = "banglabert_bnwp_prelabel"

    label_map = {0: "Not Economic", 1: "Economic"}
    new_prediction = lambda label, conf, ver: {
        "model_version": ver,
        "score": conf,
        "result": [
            {
                "from_name": "economic_relevance",
                "to_name": "article_text",
                "type": "choices",
                "value": {"choices": [label]},
                "confidence": conf,
            },
        ],
    }
    for task, pred, prob in zip(tasks, preds, probs):
        label = label_map[int(pred)]
        confidence = float(prob[int(pred)])
        entry = new_prediction(label, confidence, model_version)
        existing = task.get("predictions", [])
        replaced = False
        for i, p in enumerate(existing):
            if p.get("model_version") == model_version:
                existing[i] = entry
                replaced = True
                break
        if not replaced:
            existing.append(entry)
        task["predictions"] = existing

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    econ_count = int(preds.sum())
    mean_conf = float(
        np.mean([probs[i, int(preds[i])] for i in range(len(preds))])
    )
    print(f"Predicted: {econ_count} economic / {len(preds) - econ_count} not economic")
    print(f"Mean confidence: {mean_conf:.4f}")
    print(f"Exported -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
