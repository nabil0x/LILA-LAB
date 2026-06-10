"""Inter-rater agreement statistics.

Canonical implementation of Cohen's kappa (with SE/z/p-value),
Fleiss' kappa, confusion matrix, and classification report.
"""

import math
from collections import Counter
from typing import Any


def cohens_kappa(y1: list[str], y2: list[str]) -> dict[str, Any]:
    """Compute Cohen's kappa with statistical inference.

    Args:
        y1: Annotations from rater 1.
        y2: Annotations from rater 2.

    Returns:
        Dictionary with kappa, observed agreement, SE, z, p-value,
        labels, and confusion matrix.
    """
    assert len(y1) == len(y2), "Annotation lists must have equal length"
    labels = sorted(set(y1) | set(y2))
    n = len(y1)

    # Observed agreement
    agree = sum(1 for a, b in zip(y1, y2) if a == b)
    po = agree / n if n > 0 else 0.0

    # Expected agreement
    counter1 = Counter(y1)
    counter2 = Counter(y2)
    pe = sum((counter1[l] / n) * (counter2[l] / n) for l in labels) if n > 0 else 0.0

    # Kappa
    denom = 1.0 - pe
    kappa = (po - pe) / denom if denom > 0 else 1.0

    # Standard error under null hypothesis
    se_null = math.sqrt(pe * (1 - pe)) / denom if denom > 0 else 0.0
    z = kappa / se_null if se_null > 0 else 0.0
    p_value = 2.0 * (1.0 - _norm_cdf(abs(z)))

    # Confusion matrix
    cm = {}
    for li, l1 in enumerate(labels):
        cm[l1] = {}
        for l2 in labels:
            cm[l1][l2] = sum(1 for a, b in zip(y1, y2) if a == l1 and b == l2)

    return {
        "kappa": round(kappa, 4),
        "observed_agreement": round(po, 4),
        "expected_agreement": round(pe, 4),
        "n": n,
        "se_null": round(se_null, 4),
        "z": round(z, 4),
        "p_value": round(p_value, 6),
        "labels": labels,
        "confusion_matrix": cm,
    }


def cohens_kappa_simple(y1: list[str], y2: list[str]) -> float:
    """Compute Cohen's kappa (simple float return)."""
    return cohens_kappa(y1, y2)["kappa"]


def fleiss_kappa(ratings: list[list[str]], labels: list[str] | None = None) -> dict[str, Any]:
    """Compute Fleiss' kappa for multi-rater agreement.

    Args:
        ratings: List of rating lists, one per subject.
        labels: Optional list of all possible labels.

    Returns:
        Dictionary with kappa, observed agreement, expected agreement.
    """
    if not ratings:
        return {"kappa": 0.0, "observed_agreement": 0.0, "expected_agreement": 0.0}

    if labels is None:
        labels = sorted(set(l for r in ratings for l in r))

    n_subjects = len(ratings)
    n_raters = len(ratings[0])
    label_to_idx = {l: i for i, l in enumerate(labels)}
    n_labels = len(labels)

    # Build category count matrix
    matrix = []
    for subject_ratings in ratings:
        counts = [0] * n_labels
        for r in subject_ratings:
            counts[label_to_idx[r]] += 1
        matrix.append(counts)

    # Compute P_i (extent of agreement for subject i)
    p_items = []
    for row in matrix:
        p_i = (
            (sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1))
            if n_raters > 1
            else 0.0
        )
        p_items.append(p_i)
    p_bar = sum(p_items) / n_subjects

    # Compute p_j (proportion of all assignments to category j)
    total_assignments = n_subjects * n_raters
    p_j = [
        sum(matrix[i][j] for i in range(n_subjects)) / total_assignments for j in range(n_labels)
    ]

    # Expected agreement
    pe = sum(p * p for p in p_j)

    # Fleiss' kappa
    denom = 1.0 - pe
    kappa = (p_bar - pe) / denom if denom > 0 else 1.0

    return {
        "kappa": round(kappa, 4),
        "observed_agreement": round(p_bar, 4),
        "expected_agreement": round(pe, 4),
        "n_subjects": n_subjects,
        "n_raters": n_raters,
    }


def confusion_matrix(
    y_true: list[str], y_pred: list[str], labels: list[str] | None = None
) -> dict[str, dict[str, int]]:
    """Build a confusion matrix.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        labels: Optional list of all possible labels.

    Returns:
        Nested dict: matrix[true][predicted] = count.
    """
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))

    matrix = {l1: {l2: 0 for l2 in labels} for l1 in labels}
    for t, p in zip(y_true, y_pred):
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1
    return matrix


def classification_report(
    y_true: list[str], y_pred: list[str], labels: list[str] | None = None
) -> dict[str, Any]:
    """Compute per-class precision, recall, F1, and support.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        labels: Optional list of all possible labels.

    Returns:
        Dictionary with per-class metrics and micro/macro averages.
    """
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))

    cm = confusion_matrix(y_true, y_pred, labels)
    report = {}

    for label in labels:
        tp = cm[label][label]
        fp = sum(cm[other][label] for other in labels if other != label)
        fn = sum(cm[label][other] for other in labels if other != label)
        support = sum(cm[label][other] for other in labels)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        report[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1-score": round(f1, 4),
            "support": support,
        }

    # Micro average
    total_tp = sum(cm[l][l] for l in labels)
    total_all = len(y_true)
    micro_acc = total_tp / total_all if total_all > 0 else 0.0

    # Macro average
    macro_p = sum(r["precision"] for r in report.values()) / len(labels) if labels else 0.0
    macro_r = sum(r["recall"] for r in report.values()) / len(labels) if labels else 0.0
    macro_f1 = sum(r["f1-score"] for r in report.values()) / len(labels) if labels else 0.0

    report["micro avg"] = {
        "precision": round(micro_acc, 4),
        "recall": round(micro_acc, 4),
        "f1-score": round(micro_acc, 4),
        "support": total_all,
    }
    report["macro avg"] = {
        "precision": round(macro_p, 4),
        "recall": round(macro_r, 4),
        "f1-score": round(macro_f1, 4),
        "support": total_all,
    }

    return report


def _norm_cdf(x: float) -> float:
    """Approximate the standard normal CDF using error function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
