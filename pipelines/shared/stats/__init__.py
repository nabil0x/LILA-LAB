"""
LILA Lab — Shared Statistics Module

Inter-annotator agreement metrics and classification reporting.

Explicit re-exports:
    from pipelines.shared.stats import cohens_kappa, fleiss_kappa
    from pipelines.shared.stats import confusion_matrix, classification_report
"""

from pipelines.shared.stats.agreement import (
    classification_report,
    cohens_kappa,
    confusion_matrix,
    fleiss_kappa,
)

__all__ = [
    "cohens_kappa",
    "fleiss_kappa",
    "confusion_matrix",
    "classification_report",
]
