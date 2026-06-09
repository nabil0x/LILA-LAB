"""
Fine-tune BanglaBERT on BNLP keyword labels, predict on LabelStudio tasks,
and export pre-annotations for import.

Usage:
    python3 finetune_banglabert_for_prelabel.py
"""

import json
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
BENI_PILOT = REPO_ROOT / "beni" / "experiment" / "beni_pilot"
ANNOTATION_DIR = Path(__file__).parent
EXPORTS_DIR = ANNOTATION_DIR / "exports"
MODEL_OUTPUT_NAME = "banglabert_bnwp_prelabel"

sys.path.insert(0, str(BENI_PILOT))

import numpy as np
import torch
from torch.utils.data import DataLoader

from config import ExperimentConfig, ECONOMIC_KEYWORDS
from data import load_all_splits, add_economic_relevance_label, describe_splits
from banglabert import train_banglabert, BanglaBERTDataset, _predict
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast


def keyword_label_texts(texts: list[str]) -> list[int]:
    """Apply ECONOMIC_KEYWORDS matching same as add_economic_relevance_label."""
    pattern = "|".join(map(lambda w: w.replace("+", "\\+"), ECONOMIC_KEYWORDS))
    import re
    return [1 if re.search(pattern, t) else 0 for t in texts]


def load_ls_tasks(export_path: Path) -> tuple[list[str], list[str], list[dict]]:
    """Load LabelStudio export JSON and return texts, IDs, full tasks."""
    tasks = json.loads(export_path.read_text(encoding="utf-8"))
    texts = [t["data"]["text"] for t in tasks]
    ids = [t["id"] for t in tasks]
    return texts, ids, tasks


def predict_ls_tasks(
    model_path: Path,
    texts: list[str],
    config: ExperimentConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Run BanglaBERT inference and return preds, probs."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
    model = ElectraForSequenceClassification.from_pretrained(str(model_path))
    model.to(device)
    model.eval()

    dataset = BanglaBERTDataset(texts, [0] * len(texts), tokenizer, config)
    loader = DataLoader(dataset, batch_size=config.banglabert_batch_size, shuffle=False)

    preds, probs, _ = _predict(model, loader, device)
    return preds, probs


def export_ls_preannotations(
    tasks: list[dict],
    preds: np.ndarray,
    probs: np.ndarray,
    output_path: Path,
) -> None:
    """Add predictions to LabelStudio tasks and export for import.

    Format: each task gets a 'predictions' array with a single prediction.
    """
    label_map = {0: "Not Economic", 1: "Economic"}

    updated = []
    for task, pred, prob in zip(tasks, preds, probs):
        task_id = task["id"]
        label = label_map[int(pred)]
        confidence = float(prob[int(pred)])

        updated.append({
            "id": task_id,
            "data": task["data"],
            "predictions": [{
                "model_version": MODEL_OUTPUT_NAME,
                "score": confidence,
                "result": [{
                    "from_name": "economic_relevance",
                    "to_name": "article_text",
                    "type": "choices",
                    "value": {"choices": [label]},
                    "confidence": confidence,
                }],
            }],
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Exported {len(updated)} pre-annotations -> {output_path}", flush=True)


def main():
    config = ExperimentConfig(
        banglabert_epochs=3,
        banglabert_batch_size=8,
        banglabert_max_len=128,
        banglabert_learning_rate=2e-5,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}", flush=True)

    # ── Step 1: Load BNLP data with keyword labels ──
    print("\n=== Step 1: Load BNLP data ===", flush=True)
    splits = load_all_splits(config)
    summary = describe_splits(splits)
    for split_name, s in summary.items():
        print(f"  {split_name}: {s['rows']} articles, economic={s['economic_relevance']}", flush=True)

    train = add_economic_relevance_label(splits["train"])
    dev = add_economic_relevance_label(splits["dev"])
    test = add_economic_relevance_label(splits["test"])

    train_texts = train["text_norm"].tolist()
    train_labels = train["economic_relevance"].tolist()
    dev_texts = dev["text_norm"].tolist()
    dev_labels = dev["economic_relevance"].tolist()
    test_texts = test["text_norm"].tolist()
    test_labels = test["economic_relevance"].tolist()

    print(
        f"  train: {len(train_texts)} ({sum(train_labels)} economic)",
        flush=True,
    )
    print(
        f"  dev:   {len(dev_texts)} ({sum(dev_labels)} economic)",
        flush=True,
    )

    # ── Step 2: Fine-tune BanglaBERT ──
    print("\n=== Step 2: Fine-tune BanglaBERT ===", flush=True)
    result = train_banglabert(
        config=config,
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=dev_texts,
        val_labels=dev_labels,
        output_name=MODEL_OUTPUT_NAME,
    )
    print(f"  Best val macro F1: {result['best_val_macro_f1']:.4f}", flush=True)
    model_path = Path(result["model_path"])
    print(f"  Model saved: {model_path}", flush=True)

    # ── Step 3: Predict on test set ──
    print("\n=== Step 3: Test set evaluation ===", flush=True)
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    preds, probs, true = _predict(
        ElectraForSequenceClassification.from_pretrained(str(model_path)).to(device),
        DataLoader(
            BanglaBERTDataset(test_texts, test_labels,
                ElectraTokenizerFast.from_pretrained(str(model_path)), config),
            batch_size=config.banglabert_batch_size, shuffle=False,
        ),
        device,
    )
    print(f"  Test accuracy:  {accuracy_score(true, preds):.4f}", flush=True)
    print(f"  Test macro F1:  {f1_score(true, preds, average='macro'):.4f}", flush=True)
    print(f"  Test class F1:  {f1_score(true, preds, average='weighted'):.4f}", flush=True)

    # ── Step 4: Predict on LabelStudio tasks ──
    print("\n=== Step 4: Predict on LabelStudio tasks ===", flush=True)
    ls_export = EXPORTS_DIR / "bnlp_sample.json"
    if not ls_export.exists():
        print(f"  LS export not found: {ls_export}", flush=True)
        # Try to get tasks from LabelStudio API or use a fallback
        return

    texts, ids, tasks = load_ls_tasks(ls_export)
    print(f"  Loaded {len(texts)} LS tasks", flush=True)

    # Run prediction (re-load model fresh to avoid any training state)
    ls_preds, ls_probs = predict_ls_tasks(model_path, texts, config)

    econ_count = int(ls_preds.sum())
    print(
        f"  Predicted: {econ_count} economic / {len(ls_preds) - econ_count} not economic",
        flush=True,
    )
    mean_conf = float(ls_probs[np.arange(len(ls_preds)), ls_preds].mean())
    print(f"  Mean confidence: {mean_conf:.4f}", flush=True)

    # ── Step 5: Export pre-annotations ──
    print("\n=== Step 5: Export pre-annotations ===", flush=True)
    preannotations_path = EXPORTS_DIR / "bnlp_sample_with_predictions.json"
    export_ls_preannotations(tasks, ls_preds, ls_probs, preannotations_path)

    print("\n=== Done ===", flush=True)
    print(f"Pre-annotations: {preannotations_path}", flush=True)
    print("Import into LabelStudio via UI: Data Manager -> Import -> upload JSON", flush=True)


if __name__ == "__main__":
    main()
