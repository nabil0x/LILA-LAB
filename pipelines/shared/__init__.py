"""
LILA Lab — Shared Pipeline Library

Language-agnostic utilities for XENI pipeline construction:
data loading, model training, evaluation, LLM annotation,
statistical agreement, and configuration management.

Explicit re-exports for direct import:
    from pipelines.shared import BaseExperimentConfig
    from pipelines.shared import evaluate_model, build_tfidf_logreg
    from pipelines.shared import normalize_text, set_seed
"""

from pipelines.shared.config import BaseExperimentConfig
from pipelines.shared.data import label_by_keywords, normalize_text, set_seed
from pipelines.shared.eval import evaluate_model
from pipelines.shared.io import (
    read_csv_safe,
    read_json,
    read_jsonl,
    save_jsonl,
    write_json,
    zip_outputs,
)
from pipelines.shared.models import build_tfidf_logreg

__all__ = [
    "BaseExperimentConfig",
    "normalize_text",
    "set_seed",
    "label_by_keywords",
    "evaluate_model",
    "build_tfidf_logreg",
    "write_json",
    "read_json",
    "save_jsonl",
    "read_jsonl",
    "read_csv_safe",
    "zip_outputs",
]
