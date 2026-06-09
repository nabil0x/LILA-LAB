"""
Active learning simulation: how does classification performance scale
with annotation budget?

Uses 5-fold stratified cross-validation with TF-IDF + Logistic Regression.
Budgets: k = {50, 100, 150, 200, 250, 299} with 5 repeated trials per fold.

Uses the 299 Claude-annotated articles as labels (298 after alignment).

Usage:
    python3 run_active_learning.py

Output:
    exports/active_learning_results.json  — Full trial-level data
    exports/active_learning_plot.png      — Performance vs. budget figure
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold

EXPORTS_DIR = Path(__file__).parent / "exports"
GOLD_PATH = EXPORTS_DIR / "gold_standard.json"
LLM_PATH = EXPORTS_DIR / "llm_annotated_full.json"

Economic = "Economic"
NotEconomic = "Not Economic"

BUDGETS = [50, 100, 150, 200, 250, 299]
N_TRIALS = 5
N_FOLDS = 5
RANDOM_SEEDS = [42, 123, 456, 789, 1111]


def load_dataset() -> tuple[list[str], list[str]]:
    """Return (texts, labels) for articles in both gold standard and LLM file."""
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    gold_by_id = {g["id"]: g["economic_relevance"] for g in gold}

    llm_data = json.loads(LLM_PATH.read_text(encoding="utf-8"))
    texts, labels = [], []
    for item in llm_data:
        aid = item.get("id", "")
        label = gold_by_id.get(aid)
        if label is None:
            continue
        text = item.get("data", {}).get("text", "").strip()
        if not text:
            continue
        texts.append(text)
        labels.append(label)
    return texts, labels


def run_trial(
    train_texts: list[str], train_labels: list[str],
    test_texts: list[str], test_labels: list[str],
    econ_in_train: int,
) -> dict[str, float]:
    """Train TF-IDF + LogReg and return metrics."""
    if len(set(train_labels)) < 2:
        return {
            "accuracy": round(sum(1 for l in test_labels if l == NotEconomic) / len(test_labels), 4),
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "n_train": len(train_labels), "n_test": len(test_labels),
            "econ_train": econ_in_train, "econ_test": sum(1 for l in test_labels if l == Economic),
        }

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=80000, min_df=2, ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(class_weight="balanced", solver="liblinear", max_iter=1000)),
    ])
    pipe.fit(train_texts, train_labels)
    preds = pipe.predict(test_texts)

    labels_in_test = sorted(set(test_labels))
    if len(labels_in_test) < 2:
        return {
            "accuracy": round(accuracy_score(test_labels, preds), 4),
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "n_train": len(train_labels), "n_test": len(test_labels),
            "econ_train": econ_in_train, "econ_test": sum(1 for l in test_labels if l == Economic),
        }

    acc = accuracy_score(test_labels, preds)
    prec = precision_score(test_labels, preds, pos_label=Economic, zero_division=0)
    rec = recall_score(test_labels, preds, pos_label=Economic, zero_division=0)
    f1 = f1_score(test_labels, preds, pos_label=Economic, zero_division=0)

    return {
        "accuracy": round(acc, 4), "precision": round(prec, 4),
        "recall": round(rec, 4), "f1": round(f1, 4),
        "n_train": len(train_labels), "n_test": len(test_labels),
        "econ_train": econ_in_train, "econ_test": sum(1 for l in test_labels if l == Economic),
    }


def main():
    print("=" * 60)
    print("  Active Learning Simulation (5-Fold CV)")
    print("  Classifier: TF-IDF + Logistic Regression")
    print(f"  Budgets: {BUDGETS}")
    print(f"  Trials/budget: {N_TRIALS}, Folds: {N_FOLDS}")
    print("=" * 60)

    all_texts, all_labels = load_dataset()
    n_econ = sum(1 for l in all_labels if l == Economic)
    print(f"\nDataset: {len(all_texts)} articles ({n_econ} Economic, {n_econ/len(all_texts):.1%})")

    # Stratified K-Fold
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    y_binary = [1 if l == Economic else 0 for l in all_labels]

    # Collect all trial results
    all_trials: list[dict] = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(all_texts, y_binary)):
        fold_texts = [all_texts[i] for i in train_idx]
        fold_labels = [all_labels[i] for i in train_idx]
        fold_test_texts = [all_texts[i] for i in test_idx]
        fold_test_labels = [all_labels[i] for i in test_idx]

        econ_in_fold = sum(1 for l in fold_labels if l == Economic)
        econ_in_fold_test = sum(1 for l in fold_test_labels if l == Economic)

        print(f"\n{'─' * 50}")
        print(f"  Fold {fold + 1}/{N_FOLDS}: train={len(fold_labels)} ({econ_in_fold} econ) "
              f"test={len(fold_test_labels)} ({econ_in_fold_test} econ)")

        # Get indices of economic/non-economic in training fold
        econ_indices = [i for i, l in enumerate(fold_labels) if l == Economic]
        nonecon_indices = [i for i, l in enumerate(fold_labels) if l == NotEconomic]

        for budget in BUDGETS:
            for trial in range(N_TRIALS):
                seed = RANDOM_SEEDS[trial]
                rng = random.Random(seed + fold * 1000)

                # Stratified sampling: keep the same proportion of economic articles
                n_available_econ = len(econ_indices)
                target_econ_frac = n_available_econ / len(fold_labels)
                n_econ_target = max(1, round(budget * target_econ_frac))
                n_econ_sample = min(n_econ_target, n_available_econ)
                n_nonecon_sample = min(budget - n_econ_sample, len(nonecon_indices))

                sampled_econ = rng.sample(econ_indices, n_econ_sample)
                sampled_nonecon = rng.sample(nonecon_indices, n_nonecon_sample)
                sample_idx = sampled_econ + sampled_nonecon
                rng.shuffle(sample_idx)

                train_k = [fold_texts[i] for i in sample_idx]
                labels_k = [fold_labels[i] for i in sample_idx]

                metrics = run_trial(
                    train_k, labels_k,
                    fold_test_texts, fold_test_labels,
                    n_econ_sample,
                )
                metrics["fold"] = fold
                metrics["trial"] = trial
                metrics["budget"] = budget
                all_trials.append(metrics)

        print(f"  Budgets | Acc={np.mean([t['accuracy'] for t in all_trials if t['fold']==fold]):.2%}")

    # Aggregate by budget
    print(f"\n{'=' * 75}")
    print(f"  {'k':>5s}  {'Acc':>7s}  {'Prec':>7s}  {'Recall':>7s}  {'F1':>7s}  "
          f"{'Econ/tr':>8s}  {'Trials':>7s}")
    print(f"  {'─'*5}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*8}  {'─'*7}")

    summary = {}
    for budget in BUDGETS:
        trials = [t for t in all_trials if t["budget"] == budget]
        f1s = np.array([t["f1"] for t in trials])
        accs = np.array([t["accuracy"] for t in trials])
        precs = np.array([t["precision"] for t in trials])
        recs = np.array([t["recall"] for t in trials])
        econ_tr = np.mean([t["econ_train"] for t in trials])

        summary[str(budget)] = {
            "budget": budget,
            "n_trials": len(trials),
            "accuracy_mean": round(float(accs.mean()), 4),
            "accuracy_std": round(float(accs.std(ddof=1)), 4),
            "precision_mean": round(float(precs.mean()), 4),
            "precision_std": round(float(precs.std(ddof=1)), 4),
            "recall_mean": round(float(recs.mean()), 4),
            "recall_std": round(float(recs.std(ddof=1)), 4),
            "f1_mean": round(float(f1s.mean()), 4),
            "f1_std": round(float(f1s.std(ddof=1)), 4),
        }

        n_nonzero_f1 = sum(1 for f in f1s if f > 0)
        print(f"  {budget:5d}  {accs.mean():.2%} ±{accs.std():.2%}  "
              f"{precs.mean():.2%} ±{precs.std():.2%}  "
              f"{recs.mean():.2%} ±{recs.std():.2%}  "
              f"{f1s.mean():.2%} ±{f1s.std():.2%}  "
              f"{econ_tr:.0f}/{budget:3d}  {len(trials)}")

    # Save full results
    output = {
        "metadata": {
            "classifier": "TF-IDF + Logistic Regression",
            "n_total": len(all_texts),
            "n_economic": n_econ,
            "budgets": BUDGETS,
            "n_folds": N_FOLDS,
            "n_trials_per_budget": N_TRIALS * N_FOLDS,
        },
        "summary": summary,
        "trials": all_trials,
    }

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPORTS_DIR / "active_learning_results.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResults saved -> {out_path}")

    # Generate plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        budgets = BUDGETS

        for ax, metric, label, color in [
            (axes[0], "f1_mean", "F1 (Economic class)", "C0"),
            (axes[1], "accuracy_mean", "Accuracy", "C1"),
        ]:
            std_key = metric.replace("_mean", "_std")
            means = [summary[str(b)][metric] for b in budgets]
            stds = [summary[str(b)][std_key] for b in budgets]

            ax.errorbar(budgets, means, yerr=stds, fmt="o-", color=color,
                        capsize=4, capthick=1.5, markersize=6)
            ax.set_xlabel("Training set size (k)")
            ax.set_ylabel(label)
            ax.set_xticks(BUDGETS)
            ax.set_ylim(-0.02, 1.02)
            ax.grid(alpha=0.3)
            ax.axhline(y=0.439, color="gray", linestyle="--", alpha=0.5,
                       label="Full 298-model F1 (TF-IDF)")
            if metric == "f1_mean":
                ax.legend(fontsize=8)

        fig.suptitle("Active Learning Simulation: TF-IDF + LogReg (5-Fold CV)", fontsize=11)
        plt.tight_layout()
        plot_path = EXPORTS_DIR / "active_learning_plot.png"
        plt.savefig(plot_path, dpi=200, bbox_inches="tight")
        plt.close()
        print(f"Plot saved -> {plot_path}")

    except ImportError as e:
        print(f"Plotting unavailable: {e}")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
