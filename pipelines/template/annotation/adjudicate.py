#!/usr/bin/env python3
"""
[X]ENI — Adjudication Script

Resolve disagreements between multiple LLM annotators or human annotators.
Produces a locked reference set of gold-standard labels.

Usage:
    python adjudicate.py --input annotations/ --method majority --output refset/

Deliverable:
    - Locked reference set with adjudicated labels
    - Adjudication report showing agreement metrics
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_annotations(input_dir: str) -> list[dict]:
    """Load multi-annotator outputs.

    TODO: Implement for your language:
    - Load annotation files from the input directory
    - Group by article ID
    - Return list of {article_id, annotator_id, annotations}
    """
    print("TODO: Implement load_annotations() for your language")
    return []


def majority_vote(annotations: list[dict]) -> dict:
    """Resolve by majority voting.

    TODO: Implement majority voting logic per field.
    Use: from pipelines.shared.stats.agreement import classification_report
    """
    print("TODO: Implement majority_vote() for your language")
    return {}


def confidence_weighted(annotations: list[dict]) -> dict:
    """Resolve by confidence-weighted voting.

    TODO: Implement confidence-weighted voting.
    """
    print("TODO: Implement confidence_weighted() for your language")
    return {}


def main():
    parser = argparse.ArgumentParser(description="Adjudication Pipeline")
    parser.add_argument("--input", required=True, help="Input annotations directory")
    parser.add_argument(
        "--method", default="majority", choices=["majority", "confidence", "human_review"]
    )
    parser.add_argument("--output", default="refset/", help="Output directory")
    args = parser.parse_args()

    # TODO: Load annotations, resolve disagreements, save reference set
    logger.info(f"Adjudicating with method: {args.method}")

    logger.info("Adjudication complete. Deliverable: locked reference set with gold labels.")


if __name__ == "__main__":
    main()
