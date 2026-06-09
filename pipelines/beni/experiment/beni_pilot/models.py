from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from config import ExperimentConfig


def build_tfidf_logreg(config: ExperimentConfig) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    token_pattern=r"(?u)\b\w+\b",
                    max_features=config.max_features,
                    min_df=config.min_df,
                    ngram_range=(config.ngram_min, config.ngram_max),
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=config.max_iter,
                        class_weight="balanced",
                        solver="liblinear",
                        random_state=config.seed,
                    )
                ),
            ),
        ]
    )
