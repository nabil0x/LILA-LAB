"""Model evaluation utilities.

Standard evaluation metrics for classification tasks.
"""

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    classification_report as sklearn_report,
    f1_score,
)


def evaluate_model(
    model: Any,
    texts: list[str],
    labels: list[str],
) -> dict[str, Any]:
    """Evaluate a trained model on test data.

    Args:
        model: Trained scikit-learn pipeline with predict() method.
        texts: Test texts.
        labels: True labels.

    Returns:
        Dictionary with accuracy, macro_f1, weighted_f1, and full report.
    """
    predictions = model.predict(texts)

    accuracy = accuracy_score(labels, predictions)
    macro_f1 = f1_score(labels, predictions, average="macro", zero_division=0)
    weighted_f1 = f1_score(labels, predictions, average="weighted", zero_division=0)

    report_dict = sklearn_report(labels, predictions, output_dict=True, zero_division=0)

    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "report": report_dict,
    }
