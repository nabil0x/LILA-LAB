"""
Active learning simulation for BENI Paper 3.

Trains BanglaBERT at different annotation sizes (k = 50, 100, 150, 200, 250, 299)
and measures performance vs. annotation cost.

Usage:
    python3 active_learning.py --gold-standard path/to/gold_standard.json
    python3 active_learning.py --gold-standard path/to/gold_standard.json --output-dir outputs/active_learning
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader

from banglabert import BanglaBERTDataset, _predict, train_banglabert
from config import ExperimentConfig
from data import load_all_splits, add_economic_relevance_label
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast
from utils import set_seed, write_json


def load_gold_standard(gold_path: Path) -> tuple[list[str], list[int]]:
    """Load gold standard annotations and return texts + labels.

    Gold standard IDs use the format ``bnlp_{split}_{numeric_id}``
    (e.g. ``bnlp_train_1159``) while the TSV files use plain sequential
    integers.  We build the lookup table from the *raw* TSV rows so the
    positional index maps correctly.
    """
    with gold_path.open(encoding="utf-8") as f:
        gold = json.load(f)

    config = ExperimentConfig()
    splits = load_all_splits(config)

    # Build text lookup: parse the numeric index from the gold-standard
    # ID (e.g. "bnlp_train_1159" → split="train", idx=1159) and map
    # to the positional row in the TSV.
    text_lookup: dict[str, str] = {}
    for split_name, split_df in splits.items():
        for _, row in split_df.iterrows():
            # TSV files use sequential ints; build the gold-standard
            # style key so we can match.
            key = f"bnlp_{split_name}_{row['id']}"
            text_lookup[key] = row["text_norm"]

    texts, labels, ids = [], [], []
    missing = 0
    for item in gold:
        article_id = item["id"]
        if article_id in text_lookup:
            texts.append(text_lookup[article_id])
            labels.append(1 if item["economic_relevance"] == "Economic" else 0)
            ids.append(article_id)
        else:
            missing += 1

    if missing:
        print(f"WARNING: {missing}/{len(gold)} gold standard articles not found in BNLP splits")

    print(f"Loaded {len(texts)} gold standard articles")
    if texts:
        print(f"  Economic: {sum(labels)} ({sum(labels)/len(labels):.1%})")
        print(f"  Not Economic: {len(labels) - sum(labels)} ({(len(labels)-sum(labels))/len(labels):.1%})")

    return texts, labels, ids


def active_learning_curve(
    texts: list[str],
    labels: list[int],
    k_values: list[int],
    n_trials: int = 5,
    seed: int = 42,
) -> list[dict]:
    """Run active learning simulation at different annotation sizes.

    For each k, randomly subsamples k articles (stratified), trains BanglaBERT,
    and evaluates on the held-out set. Repeats n_trials for confidence intervals.
    """
    config = ExperimentConfig(
        banglabert_epochs=3,
        banglabert_batch_size=8,
        banglabert_max_len=128,
        banglabert_learning_rate=2e-5,
    )

    # Split into train pool and held-out test (80/20)
    rng = random.Random(seed)
    indices = list(range(len(texts)))
    rng.shuffle(indices)

    split_point = int(0.8 * len(indices))
    train_pool_idx = indices[:split_point]
    test_idx = indices[split_point:]

    test_texts = [texts[i] for i in test_idx]
    test_labels = [labels[i] for i in test_idx]

    print(f"\nActive learning simulation:")
    print(f"  Train pool: {len(train_pool_idx)} articles")
    print(f"  Held-out test: {len(test_idx)} articles")
    print(f"  Test economic rate: {sum(test_labels)/len(test_labels):.1%}")
    print(f"  k values: {k_values}")
    print(f"  Trials per k: {n_trials}")

    results = []

    for k in k_values:
        trial_metrics = []

        for trial in range(n_trials):
            econ_pool = [i for i in train_pool_idx if labels[i] == 1]
            non_pool = [i for i in train_pool_idx if labels[i] == 0]

            n_econ = min(len(econ_pool), max(1, int(k * 0.3)))
            n_non = min(len(non_pool), k - n_econ)
            actual_k = n_econ + n_non

            sampled_econ = rng.sample(econ_pool, n_econ)
            sampled_non = rng.sample(non_pool, n_non)
            sampled_idx = sampled_econ + sampled_non

            train_texts_k = [texts[i] for i in sampled_idx]
            train_labels_k = [labels[i] for i in sampled_idx]

            n_pos = sum(train_labels_k)
            n_neg = len(train_labels_k) - n_pos
            class_weights = torch.tensor([1.0, n_neg / max(n_pos, 1)], dtype=torch.float)

            result = train_banglabert(
                config=config,
                train_texts=train_texts_k,
                train_labels=train_labels_k,
                val_texts=None,
                val_labels=None,
                output_name=f"al_k{actual_k}_trial{trial}",
                class_weights=class_weights,
            )

            # Evaluate on held-out test
            model_path = Path(result["model_path"])
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
            model = ElectraForSequenceClassification.from_pretrained(str(model_path))
            model.to(device)

            test_dataset = BanglaBERTDataset(test_texts, test_labels, tokenizer, config)
            test_loader = DataLoader(test_dataset, batch_size=config.banglabert_batch_size, shuffle=False)
            preds, probs, true = _predict(model, test_loader, device)

            acc = float(accuracy_score(true, preds))
            f1_macro = float(f1_score(true, preds, average="macro"))
            f1_weighted = float(f1_score(true, preds, average="weighted"))

            trial_metrics.append({
                "accuracy": acc,
                "macro_f1": f1_macro,
                "weighted_f1": f1_weighted,
                "n_train": len(train_labels_k),
                "n_economic": sum(train_labels_k),
            })

            # Cleanup
            del model, tokenizer
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

            print(f"  k={k:3d} trial={trial+1}/{n_trials}: "
                  f"acc={acc:.4f} macro_f1={f1_macro:.4f} "
                  f"(n_econ={sum(train_labels_k)})")

        # Aggregate across trials
        avg_result = {
            "k": k,
            "accuracy_mean": np.mean([t["accuracy"] for t in trial_metrics]),
            "accuracy_std": np.std([t["accuracy"] for t in trial_metrics]),
            "macro_f1_mean": np.mean([t["macro_f1"] for t in trial_metrics]),
            "macro_f1_std": np.std([t["macro_f1"] for t in trial_metrics]),
            "weighted_f1_mean": np.mean([t["weighted_f1"] for t in trial_metrics]),
            "weighted_f1_std": np.std([t["weighted_f1"] for t in trial_metrics]),
            "n_train": trial_metrics[0]["n_train"],
            "trials": n_trials,
        }
        results.append(avg_result)

        print(f"  k={k:3d} MEAN: acc={avg_result['accuracy_mean']:.4f}±{avg_result['accuracy_std']:.4f} "
              f"macro_f1={avg_result['macro_f1_mean']:.4f}±{avg_result['macro_f1_std']:.4f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Active learning simulation for BENI")
    parser.add_argument("--gold-standard", type=Path, required=True,
                        help="Path to gold_standard.json")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/active_learning"),
                        help="Output directory for results")
    parser.add_argument("--k-values", type=str, default="50,100,150,200,250,299",
                        help="Comma-separated k values")
    parser.add_argument("--n-trials", type=int, default=5,
                        help="Number of trials per k value")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load gold standard
    texts, labels, ids = load_gold_standard(args.gold_standard)

    # Parse k values
    k_values = [int(k) for k in args.k_values.split(",")]
    k_values = [k for k in k_values if k <= len(texts)]

    print(f"\nRunning active learning simulation...")
    print(f"  Gold standard size: {len(texts)}")
    print(f"  k values: {k_values}")
    print(f"  n_trials: {args.n_trials}")

    # Run simulation
    results = active_learning_curve(
        texts=texts,
        labels=labels,
        k_values=k_values,
        n_trials=args.n_trials,
        seed=args.seed,
    )

    # Save results
    output_path = args.output_dir / "active_learning_results.json"
    write_json(output_path, results)
    print(f"\nResults saved: {output_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print("ACTIVE LEARNING CURVE SUMMARY")
    print("=" * 70)
    print(f"{'k':>5s} {'Accuracy':>12s} {'Macro F1':>12s} {'Weighted F1':>12s}")
    print("-" * 70)
    for r in results:
        print(f"{r['k']:5d} {r['accuracy_mean']:8.4f}±{r['accuracy_std']:.4f} "
              f"{r['macro_f1_mean']:8.4f}±{r['macro_f1_std']:.4f} "
              f"{r['weighted_f1_mean']:8.4f}±{r['weighted_f1_std']:.4f}")
    print("=" * 70)

    # Compute diminishing returns
    if len(results) >= 2:
        baseline_f1 = results[0]["macro_f1_mean"]
        best_f1 = results[-1]["macro_f1_mean"]
        improvement = best_f1 - baseline_f1
        print(f"\nImprovement from k={results[0]['k']} to k={results[-1]['k']}: "
              f"{improvement:+.4f} macro F1")

        # Find k that reaches 95% of max performance
        threshold = 0.95 * best_f1
        for r in results:
            if r["macro_f1_mean"] >= threshold:
                print(f"95% of max performance reached at k={r['k']}")
                break


if __name__ == "__main__":
    main()
