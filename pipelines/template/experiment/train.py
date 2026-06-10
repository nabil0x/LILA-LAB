#!/usr/bin/env python3
"""
[X]ENI — Classifier Training

Train narrative classifiers on annotated data. Start with TF-IDF baseline,
progress to multilingual transformer models.

Usage:
    python train.py --refset ../annotation/refset/ --output models/ --model-type tfidf

Deliverable:
    - Trained model artifacts
    - Training metrics report
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from pipelines.shared.config import BaseExperimentConfig
from pipelines.shared.data import normalize_text, set_seed
from pipelines.shared.eval import evaluate_model
from pipelines.shared.io import ensure_dirs, read_csv_safe, read_jsonl, write_json
from pipelines.shared.models import build_tfidf_logreg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_refset(refset_path: str) -> pd.DataFrame:
    """Load annotated reference set from a directory or file.

    Supports JSONL and CSV formats. Looks for train.jsonl, train.csv,
    refset.jsonl, refset.csv, or uses the path directly if it is a file.

    Args:
        refset_path: Path to reference set directory or file.

    Returns:
        DataFrame with articles and their labels.

    Raises:
        FileNotFoundError: If no suitable file is found.
        ValueError: If the file format is unsupported.
    """
    path = Path(refset_path)

    if path.is_file():
        if path.suffix == ".jsonl":
            data = read_jsonl(path)
            return pd.DataFrame(data)
        elif path.suffix == ".csv":
            return read_csv_safe(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    # Directory — look for common file names
    candidates = [
        path / "train.jsonl",
        path / "train.csv",
        path / "refset.jsonl",
        path / "refset.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            if candidate.suffix == ".jsonl":
                return pd.DataFrame(read_jsonl(candidate))
            else:
                return read_csv_safe(candidate)

    raise FileNotFoundError(
        f"No training data found in {refset_path}. "
        f"Expected a JSONL/CSV file or a directory containing "
        f"train.jsonl, train.csv, refset.jsonl, or refset.csv."
    )


def _infer_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Infer text and label column names from a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (text_column, label_column).
    """
    text_col = "text" if "text" in df.columns else df.select_dtypes(
        include=["object"]
    ).columns[0]

    label_col = (
        "label"
        if "label" in df.columns
        else "economic_relevance"
        if "economic_relevance" in df.columns
        else df.columns[-1]
    )
    return text_col, label_col


def train_tfidf(
    refset_path: str,
    output_path: str,
    config: BaseExperimentConfig | None = None,
) -> dict[str, Any]:
    """Train a TF-IDF + logistic regression baseline model.

    Args:
        refset_path: Path to annotated reference set.
        output_path: Directory to save model and metrics.
        config: Optional experiment configuration (defaults to BaseExperimentConfig).

    Returns:
        Dictionary with model path and evaluation metrics.
    """
    if config is None:
        config = BaseExperimentConfig()

    logger.info("Loading reference set from %s", refset_path)
    df = load_refset(refset_path)
    text_col, label_col = _infer_columns(df)
    logger.info(
        "Loaded %d articles. Text column: '%s', Label column: '%s'",
        len(df), text_col, label_col,
    )

    # Normalize text
    df["text_norm"] = df[text_col].apply(normalize_text)

    # Train / validation / test split
    from sklearn.model_selection import train_test_split

    train_df, test_df = train_test_split(
        df,
        test_size=config.test_size,
        random_state=config.seed,
        stratify=df[label_col],
    )
    train_df, val_df = train_test_split(
        train_df,
        test_size=config.val_size / (1 - config.test_size),
        random_state=config.seed,
        stratify=train_df[label_col],
    )

    logger.info(
        "Split: train=%d, val=%d, test=%d",
        len(train_df), len(val_df), len(test_df),
    )

    # Build and train model
    logger.info("Building TF-IDF + LogisticRegression pipeline …")
    model = build_tfidf_logreg(
        max_features=config.max_features,
        min_df=config.min_df,
        ngram_range=config.ngram_range,
        max_iter=config.max_iter,
        seed=config.seed,
    )

    logger.info("Training …")
    model.fit(train_df["text_norm"].tolist(), train_df[label_col].tolist())

    # Save model
    output_dir = Path(output_path)
    ensure_dirs(output_dir)
    model_file = output_dir / "tfidf_logreg.joblib"
    joblib.dump(model, model_file)
    logger.info("Model saved: %s", model_file)

    # Evaluate
    report: dict[str, Any] = {
        "model_type": "tfidf",
        "model_path": str(model_file),
        "n_train": len(train_df),
        "n_val": len(val_df),
        "n_test": len(test_df),
        "label_distribution": df[label_col].value_counts().to_dict(),
    }

    report["val"] = evaluate_model(
        model, val_df["text_norm"].tolist(), val_df[label_col].tolist(),
    )
    report["test"] = evaluate_model(
        model, test_df["text_norm"].tolist(), test_df[label_col].tolist(),
    )

    report_path = output_dir / "training_metrics.json"
    write_json(report_path, report)
    logger.info("Metrics saved: %s", report_path)

    return report


def train_bert(
    refset_path: str,
    output_path: str,
    config: BaseExperimentConfig | None = None,
) -> dict[str, Any]:
    """Fine-tune a multilingual transformer model (BERT-style).

    Sets up a Hugging Face ``Trainer`` scaffold.  Full training requires
    a GPU; on CPU-only machines the model is saved untrained so the user
    can transfer it to a GPU environment.

    Args:
        refset_path: Path to annotated reference set.
        output_path: Directory to save model and metrics.
        config: Optional experiment configuration.

    Returns:
        Dictionary with model path and evaluation results.
    """
    if config is None:
        config = BaseExperimentConfig()

    logger.info("Loading reference set from %s", refset_path)
    df = load_refset(refset_path)
    text_col, label_col = _infer_columns(df)

    from sklearn.model_selection import train_test_split

    train_df, test_df = train_test_split(
        df,
        test_size=config.test_size,
        random_state=config.seed,
        stratify=df[label_col],
    )
    train_df, val_df = train_test_split(
        train_df,
        test_size=config.val_size / (1 - config.test_size),
        random_state=config.seed,
        stratify=train_df[label_col],
    )

    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    model_name = "xlm-roberta-base"
    num_labels = df[label_col].nunique()
    label_list = sorted(df[label_col].unique())
    label2id = {l: i for i, l in enumerate(label_list)}
    id2label = {i: l for i, l in enumerate(label_list)}

    logger.info(
        "Using model: %s with %d classes: %s",
        model_name, num_labels, label_list,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )

    def tokenize_fn(examples: list[str]) -> dict[str, Any]:
        return tokenizer(
            examples, padding=True, truncation=True, max_length=256,
            return_tensors="pt",
        )

    class TextDataset(torch.utils.data.Dataset):
        """Simple torch Dataset wrapping texts and labels."""

        def __init__(self, texts: list[str], labels: list[int]) -> None:
            self.encodings = tokenize_fn(texts)
            self.labels = labels

        def __getitem__(self, idx: int) -> dict[str, Any]:
            item = {k: v[idx] for k, v in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
            return item

        def __len__(self) -> int:
            return len(self.labels)

    train_labels = train_df[label_col].map(label2id).tolist()
    val_labels = val_df[label_col].map(label2id).tolist()
    test_labels = test_df[label_col].map(label2id).tolist()

    train_dataset = TextDataset(train_df[text_col].tolist(), train_labels)
    val_dataset = TextDataset(val_df[text_col].tolist(), val_labels)
    test_dataset = TextDataset(test_df[text_col].tolist(), test_labels)

    output_dir = Path(output_path)
    ensure_dirs(output_dir)

    training_args = TrainingArguments(
        output_dir=str(output_dir / "bert_checkpoints"),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        load_best_model_at_end=True,
        logging_dir=str(output_dir / "logs"),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    logger.info("Starting BERT training (GPU recommended for practical runtime) …")
    try:
        trainer.train()
        logger.info("BERT training complete.")
    except RuntimeError as exc:
        logger.warning(
            "BERT training failed (likely no GPU): %s. "
            "Model saved untrained for later transfer.",
            exc,
        )

    # Save model & tokenizer
    model_dir = output_dir / "bert_model"
    model.save_pretrained(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    logger.info("Model saved: %s", model_dir)

    # Evaluate
    predictions = trainer.predict(test_dataset)
    pred_labels = predictions.predictions.argmax(-1).tolist()
    true_labels = test_labels

    from sklearn.metrics import (
        accuracy_score,
        f1_score,
    )
    from sklearn.metrics import (
        classification_report as sk_report,
    )

    report: dict[str, Any] = {
        "model_type": "bert",
        "model_name": model_name,
        "model_path": str(model_dir),
        "n_train": len(train_df),
        "n_val": len(val_df),
        "n_test": len(test_df),
        "label_mapping": label2id,
    }

    report["test_accuracy"] = round(accuracy_score(true_labels, pred_labels), 4)
    report["test_macro_f1"] = round(
        f1_score(true_labels, pred_labels, average="macro"), 4
    )
    report["test_report"] = sk_report(
        true_labels, pred_labels,
        target_names=label_list, output_dict=True, zero_division=0,
    )

    report_path = output_dir / "bert_training_metrics.json"
    write_json(report_path, report)
    logger.info("Metrics saved: %s", report_path)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Narrative Classifier")
    parser.add_argument(
        "--refset", required=True,
        help="Annotated reference set (directory or file)",
    )
    parser.add_argument(
        "--output", default="models/",
        help="Model output directory",
    )
    parser.add_argument(
        "--model-type", default="tfidf",
        choices=["tfidf", "bert", "ensemble"],
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--max-features", type=int, default=80000,
        help="Max vocabulary size for TF-IDF",
    )
    args = parser.parse_args()

    set_seed(args.seed)

    config = BaseExperimentConfig(
        seed=args.seed,
        max_features=args.max_features,
    )

    if args.model_type == "tfidf":
        train_tfidf(args.refset, args.output, config)
    elif args.model_type == "bert":
        train_bert(args.refset, args.output, config)
    elif args.model_type == "ensemble":
        tfidf_report = train_tfidf(args.refset, args.output, config)
        bert_report = train_bert(args.refset, args.output, config)
        ensemble_path = Path(args.output) / "training_metrics.json"
        write_json(ensemble_path, {"tfidf": tfidf_report, "bert": bert_report})

    logger.info(
        "Training complete. Deliverable: %s model in %s",
        args.model_type, args.output,
    )


if __name__ == "__main__":
    main()
