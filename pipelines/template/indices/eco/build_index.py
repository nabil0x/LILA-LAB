#!/usr/bin/env python3
"""
[X]ENI — Economic Narrative Index Builder

Aggregate article-level LLM predictions into monthly economic narrative index.
Adapted from BENI's build_narrative_index.py.

Usage:
    python build_index.py --predictions ../../experiment/outputs/predictions.csv --output ./

Deliverable:
    - Monthly economic narrative index CSV
    - Ready for validation against macroeconomic indicators
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_predictions(path: str):
    """Load article-level predictions.

    TODO: Load predictions CSV from your experiment outputs.
    Expected columns: article_id, date, economic_relevance, probability, ...
    """
    print("TODO: Implement load_predictions() for your pipeline")
    return []


def build_monthly_index(predictions):
    """Aggregate article-level predictions into monthly index.

    Steps:
    1. Group predictions by year-month
    2. Calculate mean probability per economic topic per month
    3. Apply source-weighting normalization
    4. Produce monthly index series
    """
    print("TODO: Implement build_monthly_index() for your pipeline")
    return []


def main():
    parser = argparse.ArgumentParser(description="Build Economic Narrative Index")
    parser.add_argument("--predictions", required=True, help="Article-level predictions CSV")
    parser.add_argument("--output", default="./", help="Output directory")
    args = parser.parse_args()

    predictions = load_predictions(args.predictions)
    index = build_monthly_index(predictions)

    logger.info(f"Index built: {len(index)} months")
    logger.info("Deliverable: monthly index CSV ready for validation.")


if __name__ == "__main__":
    main()
