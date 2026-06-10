#!/usr/bin/env python3
"""
[X]ENI — Classifier Training

Train narrative classifiers on annotated data. Start with TF-IDF baseline,
progress to multilingual transformer models.

Usage:
    python train.py --refset ../annotation/refset/ --output models/ --model-type tfidf

Deliverable:
    - Trained model artifacts
    - Training metrics report
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_tfidf(refset_path: str, output_path: str):
    """Train TF-IDF + logistic regression baseline.

    TODO: Implement for your language:
    - Load annotated data from refset_path
    - Use: from pipelines.shared.models import build_tfidf_logreg
    - Use: from pipelines.shared.eval import evaluate_model
    - Save trained model to output_path
    """
    print("TODO: Implement train_tfidf() for your language")


def train_bert(refset_path: str, output_path: str):
    """Fine-tune multilingual/BERT model for your language.

    TODO: Implement BERT fine-tuning for your language.
    Consider: XLM-RoBERTa, mBERT, or language-specific models.
    """
    print("TODO: Implement train_bert() for your language")


def main():
    parser = argparse.ArgumentParser(description="Train Narrative Classifier")
    parser.add_argument("--refset", required=True, help="Annotated reference set")
    parser.add_argument("--output", default="models/", help="Model output directory")
    parser.add_argument("--model-type", default="tfidf", choices=["tfidf", "bert", "ensemble"])
    args = parser.parse_args()

    if args.model_type == "tfidf":
        train_tfidf(args.refset, args.output)
    elif args.model_type == "bert":
        train_bert(args.refset, args.output)
    elif args.model_type == "ensemble":
        # Train both and ensemble
        train_tfidf(args.refset, args.output)
        train_bert(args.refset, args.output)

    logger.info(f"Training complete. Deliverable: {args.model_type} model in {args.output}")


if __name__ == "__main__":
    main()
