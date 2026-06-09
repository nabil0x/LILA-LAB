"""Train BanglaBERT on the full 299-article gold standard with class weights."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from banglabert import evaluate_banglabert, train_banglabert
from config import ExperimentConfig
from active_learning import load_gold_standard
from utils import set_seed, write_json


def main():
    set_seed(42)
    gold_path = Path("../../annotation/exports/gold_standard.json")
    output_dir = Path("outputs/banglabert_human")
    output_dir.mkdir(parents=True, exist_ok=True)

    texts, labels, ids = load_gold_standard(gold_path)

    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    class_weights = torch.tensor([1.0, n_neg / max(n_pos, 1)], dtype=torch.float)
    print(f"\nClass weights: [1.0, {class_weights[1].item():.2f}]")
    print(f"  Economic: {n_pos} ({n_pos/len(labels):.1%})")
    print(f"  Not Economic: {n_neg} ({n_neg/len(labels):.1%})")

    config = ExperimentConfig(
        banglabert_epochs=5,
        banglabert_batch_size=8,
        banglabert_max_len=384,
        banglabert_learning_rate=2e-5,
    )

    print(f"\nTraining BanglaBERT on {len(texts)} human-labeled articles (5 epochs)...")
    result = train_banglabert(
        config=config,
        train_texts=texts,
        train_labels=labels,
        val_texts=None,
        val_labels=None,
        output_name="banglabert_human_299",
        class_weights=class_weights,
    )

    print(f"\nTraining complete. Model saved to: {result['model_path']}")

    metrics = {
        "model": "banglabert_human_299",
        "train_size": len(texts),
        "n_economic": n_pos,
        "n_not_economic": n_neg,
        "class_weights": [1.0, round(class_weights[1].item(), 2)],
        "epochs": result["epochs"],
        "best_val_macro_f1": result["best_val_macro_f1"],
        "history": result["history"],
    }
    write_json(output_dir / "training_metrics.json", metrics)
    print(f"Metrics saved to: {output_dir / 'training_metrics.json'}")


if __name__ == "__main__":
    main()
