#!/usr/bin/env python3
"""
[X]ENI — Health Discourse Index Builder

Aggregate article-level LLM predictions into monthly health discourse index.

Usage:
    python build_index.py --predictions ../../experiment/outputs/predictions.csv --output ./

Deliverable:
    - Monthly health discourse index CSV
    - Ready for validation against health outcome indicators
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_monthly_index(predictions):
    """Aggregate article-level predictions into monthly health index.

    TODO: Implement for your language:
    - Group predictions by year-month
    - Calculate mean probability per health topic per month
    - Apply source-weighting normalization
    - Produce monthly health index series
    """
    print("TODO: Implement build_monthly_index() for your health pipeline")
    return []


def main():
    parser = argparse.ArgumentParser(description="Build Health Discourse Index")
    parser.add_argument("--predictions", required=True, help="Article-level predictions CSV")
    parser.add_argument("--output", default="./", help="Output directory")
    _args = parser.parse_args()

    # TODO: Load predictions, build index, save output
    logger.info("Health index builder ready. Implement aggregation logic.")

    logger.info("Deliverable: monthly health index CSV ready for validation.")


if __name__ == "__main__":
    main()
