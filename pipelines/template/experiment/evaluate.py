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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_model(model_path: str, test_path: str):
    """Evaluate a trained model on test data.

    TODO: Implement for your language:
    - Load trained model from model_path
    - Load test data from test_path
    - Use: from pipelines.shared.eval import evaluate_model as eval_fn
    - Save metrics report
    """
    print("TODO: Implement evaluate_model() for your language")


def compare_models(results_dir: str):
    """Compare multiple model performances.

    TODO: Implement model comparison across TF-IDF, BERT, etc.
    """
    print("TODO: Implement compare_models() for your language")


def main():
    parser = argparse.ArgumentParser(description="Evaluate Narrative Classifier")
    parser.add_argument("--model", help="Trained model path")
    parser.add_argument("--test", help="Test set path")
    parser.add_argument("--compare", help="Directory with multiple model results")
    parser.add_argument("--output", default="outputs/", help="Output directory")
    args = parser.parse_args()

    if args.model and args.test:
        evaluate_model(args.model, args.test)
    elif args.compare:
        compare_models(args.compare)

    logger.info("Evaluation complete. Deliverable: metrics report + predictions CSV.")


if __name__ == "__main__":
    main()
