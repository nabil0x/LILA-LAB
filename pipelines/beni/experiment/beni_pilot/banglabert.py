from __future__ import annotations

import gc
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, f1_score
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset
from transformers import (
    ElectraForSequenceClassification,
    ElectraTokenizerFast,
    get_linear_schedule_with_warmup,
)

from config import ExperimentConfig
from utils import write_json


def _load_tokenizer_and_model(config: ExperimentConfig, num_labels: int = 2):
    model_path = config.banglabert_dir
    if model_path.exists():
        print(f"Loading BanglaBERT from local path: {model_path}", flush=True)
        tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
        model = ElectraForSequenceClassification.from_pretrained(
            str(model_path),
            num_labels=num_labels,
            ignore_mismatched_sizes=True,
        )
    else:
        print(f"Local model not found at {model_path}, downloading from HuggingFace hub...", flush=True)
        tokenizer = ElectraTokenizerFast.from_pretrained("csebuetnlp/banglabert")
        model = ElectraForSequenceClassification.from_pretrained(
            "csebuetnlp/banglabert",
            num_labels=num_labels,
            ignore_mismatched_sizes=True,
        )
        tokenizer.save_pretrained(str(model_path))
        model.save_pretrained(str(model_path))
        print(f"Saved BanglaBERT to {model_path} for reuse", flush=True)
    return tokenizer, model


class BanglaBERTDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer, config: ExperimentConfig):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = config.banglabert_max_len

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def _predict(model, dataloader: DataLoader, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    all_preds, all_probs, all_labels = [], [], []
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=-1)
            preds = torch.argmax(outputs.logits, dim=-1)
            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return np.array(all_preds), np.array(all_probs), np.array(all_labels)


def train_banglabert(
    config: ExperimentConfig,
    train_texts: list[str],
    train_labels: list[int],
    val_texts: list[str] | None = None,
    val_labels: list[int] | None = None,
    output_name: str = "banglabert_economic",
    class_weights: torch.Tensor | None = None,
) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)

    tokenizer, model = _load_tokenizer_and_model(config)
    model.to(device)

    use_amp = device.type == "cuda" and torch.cuda.get_device_capability() >= (7, 0)
    scaler = GradScaler(enabled=use_amp)
    print(f"fp16={use_amp} (device_cap={torch.cuda.get_device_capability() if device.type == 'cuda' else 'N/A'})", flush=True)

    weight_on_device = class_weights.to(device) if class_weights is not None else None
    ce_loss_fn = torch.nn.CrossEntropyLoss(weight=weight_on_device)

    train_dataset = BanglaBERTDataset(train_texts, train_labels, tokenizer, config)
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.banglabert_batch_size,
        shuffle=True,
        num_workers=2,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.banglabert_learning_rate)
    total_steps = len(train_loader) * config.banglabert_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
    )

    best_val_f1 = 0.0
    best_state = None
    history = []

    for epoch in range(config.banglabert_epochs):
        model.train()
        total_loss = 0
        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device, non_blocking=True)
            attention_mask = batch["attention_mask"].to(device, non_blocking=True)
            labels = batch["labels"].to(device, non_blocking=True)

            with autocast(enabled=use_amp):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                loss = ce_loss_fn(outputs.logits, labels)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()

            # Log every 500 steps so we see progress
            if step > 0 and step % 500 == 0:
                print(f"    step {step}/{len(train_loader)} loss={loss.item():.4f} gpu_mem={torch.cuda.memory_allocated()/1024**2:.0f}MiB", flush=True)

        avg_loss = total_loss / len(train_loader)

        val_metrics = {}
        if val_texts is not None and val_labels is not None:
            val_dataset = BanglaBERTDataset(val_texts, val_labels, tokenizer, config)
            val_loader = DataLoader(val_dataset, batch_size=config.banglabert_batch_size, shuffle=False)
            preds, probs, true = _predict(model, val_loader, device)
            val_f1 = float(f1_score(true, preds, average="macro"))
            val_acc = float(accuracy_score(true, preds))
            val_metrics = {"val_accuracy": val_acc, "val_macro_f1": val_f1}

            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        epoch_result = {"epoch": epoch + 1, "train_loss": round(avg_loss, 4), **val_metrics}
        history.append(epoch_result)
        print(f"  epoch {epoch+1}: loss={avg_loss:.4f} {val_metrics} gpu_mem={torch.cuda.memory_allocated()/1024**2:.0f}MiB", flush=True)

    # Restore best model
    if best_state is not None:
        model.load_state_dict(best_state)

    # Save model
    save_path = config.model_dir / output_name
    model.save_pretrained(str(save_path))
    tokenizer.save_pretrained(str(save_path))
    print(f"model saved: {save_path}")

    # Cleanup GPU memory
    del model
    gc.collect()
    torch.cuda.empty_cache()

    return {
        "output_name": output_name,
        "model_path": str(save_path),
        "history": history,
        "best_val_macro_f1": best_val_f1,
        "epochs": config.banglabert_epochs,
        "batch_size": config.banglabert_batch_size,
        "learning_rate": config.banglabert_learning_rate,
    }


def evaluate_banglabert(
    config: ExperimentConfig,
    test_texts: list[str],
    test_labels: list[int],
    model_name: str = "banglabert_economic",
) -> dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = config.model_dir / model_name
    tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
    model = ElectraForSequenceClassification.from_pretrained(str(model_path))
    model.to(device)
    model.eval()

    dataset = BanglaBERTDataset(test_texts, test_labels, tokenizer, config)
    loader = DataLoader(dataset, batch_size=config.banglabert_batch_size, shuffle=False)

    preds, probs, true = _predict(model, loader, device)

    report = {
        "accuracy": float(accuracy_score(true, preds)),
        "macro_f1": float(f1_score(true, preds, average="macro")),
        "weighted_f1": float(f1_score(true, preds, average="weighted")),
        "classification_report": classification_report(true, preds, output_dict=True, zero_division=0),
    }

    del model
    gc.collect()
    torch.cuda.empty_cache()

    return report
