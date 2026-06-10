"""Scikit-learn model builders.

Reusable pipeline factories for text classification.
"""

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline


def build_tfidf_logreg(
    *,
    max_features: int = 80_000,
    min_df: int = 2,
    ngram_range: tuple[int, int] = (1, 2),
    max_iter: int = 1_000,
    seed: int = 42,
    class_weight: str = "balanced",
    solver: str = "liblinear",
) -> Pipeline:
    """Build a TF-IDF + Logistic Regression classification pipeline.

    Args:
        max_features: Maximum vocabulary size.
        min_df: Minimum document frequency.
        ngram_range: N-gram range for TF-IDF.
        max_iter: Maximum iterations for logistic regression.
        seed: Random seed.
        class_weight: Class weighting strategy.
        solver: Solver for logistic regression.

    Returns:
        Scikit-learn Pipeline.
    """
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                max_features=max_features,
                min_df=min_df,
                ngram_range=ngram_range,
                token_pattern=r"(?u)\b\w+\b",
                sublinear_tf=True,
            ),
        ),
        (
            "clf",
            OneVsRestClassifier(
                LogisticRegression(
                    max_iter=max_iter,
                    class_weight=class_weight,
                    solver=solver,
                    random_state=seed,
                )
            ),
        ),
    ])
