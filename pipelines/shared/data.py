"""Data processing utilities.

Text normalization, keyword-based labeling, and general data helpers.
"""

import random
import re
from typing import Any

import numpy as np
import pandas as pd


# Generic Unicode punctuation regex (covers most scripts)
UNICODE_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)

# Whitespace normalization
SPACE_RE = re.compile(r"\s+")


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def normalize_text(text: str, punct_re: re.Pattern | None = None) -> str:
    """Normalize text by removing BOM, extra whitespace, and optionally punctuation.

    Args:
        text: Input text.
        punct_re: Optional regex for punctuation to strip. If None, strips
                  generic Unicode punctuation.

    Returns:
        Normalized text.
    """
    if not isinstance(text, str):
        return ""

    # Remove BOM
    text = text.replace("\ufeff", "")

    # Strip punctuation if provided
    regex = punct_re or UNICODE_PUNCT_RE
    text = regex.sub(" ", text)

    # Collapse whitespace
    text = SPACE_RE.sub(" ", text).strip()

    return text


def label_by_keywords(
    frame: pd.DataFrame,
    text_column: str,
    keywords: list[str],
    label_column: str = "economic_relevance",
    case_insensitive: bool = True,
) -> pd.DataFrame:
    """Label rows based on keyword presence in text.

    Args:
        frame: Input DataFrame.
        text_column: Column containing text to search.
        keywords: List of keywords/phrases to match.
        label_column: Output column name for labels (1 = match, 0 = no match).
        case_insensitive: Whether to ignore case when matching.

    Returns:
        DataFrame with the new label column added.
    """
    flags = re.IGNORECASE if case_insensitive else 0
    pattern = re.compile("|".join(re.escape(kw) for kw in keywords), flags)

    frame = frame.copy()
    frame[label_column] = frame[text_column].apply(
        lambda t: 1 if isinstance(t, str) and pattern.search(t) else 0
    )
    return frame
