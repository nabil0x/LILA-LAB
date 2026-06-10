#!/usr/bin/env python3
"""
[X]ENI — Model Evaluation

Evaluate trained classifiers against held-out test sets.
Compare across model types and against BENI benchmarks.

Usage:
    python evaluate.py --model models/model.pkl --test ../annotation/refset/test.jsonl

Deliverable:
    - Per-category performance metrics
    - Model comparison report
    - Article-level predictions for index construction
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from pipelines.shared.eval import evaluate_model as eval_fn
from pipelines.shared.io import ensure_dirs, read_csv_safe, read_jsonl, write_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_test_set(test_path: str) -> pd.DataFrame:
    """Load test data from a JSONL or CSV file.

    Args:
        test_path: Path to test data file.

    Returns:
        DataFrame with articles and their labels.

    Raises:
        ValueError: If the file format is unsupported.
    """
    path = Path(test_path)
    if path.suffix == ".jsonl":
        return pd.DataFrame(read_jsonl(path))
    elif path.suffix == ".csv":
        return read_csv_safe(path)
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. "
            f"Expected .jsonl or .csv"
        )


def _infer_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Infer text and label column names from a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (text_column, label_column).
    """
    text_col = "text" if "text" in df.columns else df.select_dtypes(
        include=["object"]
    ).columns[0]

    label_col = (
        "label"
        if "label" in df.columns
        else "economic_relevance"
        if "economic_relevance" in df.columns
        else df.columns[-1]
    )
    return text_col, label_col


def evaluate_single_model(
    model_path: str,
    test_path: str,
    output_path: str,
) -> dict[str, Any]:
    """Evaluate a trained model on a held-out test set.

    Args:
        model_path: Path to the saved model (joblib format).
        test_path: Path to the test data file.
        output_path: Directory in which to save the metrics report.

    Returns:
        Dictionary of evaluation metrics.
    """
    logger.info("Loading model from %s", model_path)
    model = joblib.load(model_path)

    logger.info("Loading test data from %s", test_path)
    df = load_test_set(test_path)
    text_col, label_col = _infer_columns(df)
    logger.info(
        "Loaded %d test articles. Text column: '%s', Label column: '%s'",
        len(df), text_col, label_col,
    )

    from pipelines.shared.data import normalize_text

    df["text_norm"] = df[text_col].apply(normalize_text)

    texts = df["text_norm"].tolist()
    labels = df[label_col].tolist()

    logger.info("Evaluating …")
    metrics = eval_fn(model, texts, labels)

    metrics["model_path"] = model_path
    metrics["test_path"] = test_path
    metrics["n_test"] = len(df)

    out_dir = Path(output_path)
    ensure_dirs(out_dir)

    report_path = out_dir / "evaluation_metrics.json"
    write_json(report_path, metrics)
    logger.info("Metrics saved: %s", report_path)

    logger.info(
        "Accuracy: %.4f, Macro F1: %.4f",
        metrics["accuracy"], metrics["macro_f1"],
    )

    return metrics


def compare_models(results_dir: str) -> dict[str, Any]:
    """Compare multiple model performances from a results directory.

    Recursively finds all ``evaluation_metrics.json`` files, compiles a
    comparison table, and identifies the best-performing model by macro F1.

    Args:
        results_dir: Directory containing subdirectories with evaluation results.

    Returns:
        Dictionary with a list of model entries and a comparison table.
    """
    results_path = Path(results_dir)
    comparison: dict[str, Any] = {
        "models": [],
        "comparison": {},
    }

    metrics_files = list(results_path.rglob("evaluation_metrics.json"))

    if not metrics_files:
        logger.warning(
            "No evaluation_metrics.json files found in %s", results_dir,
        )
        return comparison

    for mf in metrics_files:
        from pipelines.shared.io import read_json

        metrics = read_json(mf)
        model_info = {
            "model_path": str(mf.parent),
            "accuracy": metrics.get("accuracy"),
            "macro_f1": metrics.get("macro_f1"),
            "weighted_f1": metrics.get("weighted_f1"),
        }
        comparison["models"].append(model_info)

    # Build comparison table
    comp_df = pd.DataFrame(comparison["models"])
    comparison["comparison_table"] = comp_df.to_dict(orient="records")

    # Identify best model by macro F1
    if not comp_df.empty and "macro_f1" in comp_df.columns:
        best_idx = comp_df["macro_f1"].idxmax()
        comparison["best_model"] = comparison["models"][best_idx]

    out_path = results_path / "model_comparison.json"
    write_json(out_path, comparison)
    logger.info("Comparison saved: %s", out_path)

    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Narrative Classifier")
    parser.add_argument(
        "--model",
        help="Trained model path (joblib / pickle)",
    )
    parser.add_argument(
        "--test",
        help="Test set path (JSONL or CSV)",
    )
    parser.add_argument(
        "--compare",
        help="Directory with multiple model result subdirectories",
    )
    parser.add_argument(
        "--output",
        default="outputs/",
        help="Output directory for metrics reports",
    )
    args = parser.parse_args()

    if args.model and args.test:
        evaluate_single_model(args.model, args.test, args.output)
    elif args.compare:
        compare_models(args.compare)
    else:
        logger.error("Provide either --model + --test, or --compare")
        parser.print_help()
        return

    logger.info(
        "Evaluation complete. Deliverable: metrics report + predictions CSV."
    )


if __name__ == "__main__":
    main()
