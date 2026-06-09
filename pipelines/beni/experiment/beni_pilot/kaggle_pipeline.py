"""
BENI — Full Pipeline for Kaggle T4 GPU
========================================
Trains BanglaBERT, builds the narrative index, and correlates with macro.
Run this script cell by cell in a Kaggle Notebook with GPU T4 x1 accelerator.

IMPORTANT: /kaggle/working/ is EPHEMERAL — it is wiped when the session ends.
Each step below creates a ZIP of outputs so you can download results BEFORE
the session shuts down. Download each zip from the Data → Output tab immediately.

Usage:
    In a Kaggle Notebook:
        1. Add dataset: annnasernabil/beni-data
        2. Settings → Accelerator → GPU T4 x1
        3. File → Import Notebook → Select this file
        4. Run All (≈3 hours) — OR run cells one at a time, downloading zips after each step
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 1 — Install dependencies
# ──────────────────────────────────────────────────────────────────────
"""
!pip install -q transformers sentencepiece accelerate
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 2 — Detect data directory & clone code
# ──────────────────────────────────────────────────────────────────────
"""
import os
from pathlib import Path

# The dataset "annnasernabil/beni-data" is mounted by Kaggle.
# Try the explicit owner-slug path first, then fall back to short path.
DATA_CANDIDATES = [
    Path("/kaggle/input/datasets/annnasernabil/beni-data/beni-data"),
    Path("/kaggle/input/beni-data/beni-data"),
    Path("/kaggle/input/beni-data"),
]

DATA_DIR = None
for cand in DATA_CANDIDATES:
    if (cand / "potrika").exists():
        DATA_DIR = cand
        break

if DATA_DIR is None:
    raise FileNotFoundError(
        f"Cannot find beni-data dataset. Checked: {DATA_CANDIDATES}. "
        "Make sure the dataset 'annnasernabil/beni-data' is added to this notebook."
    )

print(f"Data directory: {DATA_DIR}")
print(f"  potrika/  exists: {(DATA_DIR / 'potrika').exists()}")
print(f"  macro/    exists: {(DATA_DIR / 'macro').exists()}")
print(f"  models/   exists: {(DATA_DIR / 'models').exists()}")

# Verify potrika CSVs are present
potrika_files = list((DATA_DIR / "potrika").glob("*economy*"))
print(f"  Economy CSVs: {len(potrika_files)}")
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 3 — Clone the repo
# ──────────────────────────────────────────────────────────────────────
"""
!git clone --depth 1 https://github.com/nabil0x/economic-narrative-indices.git /kaggle/working/repo 2>&1 | tail -3
%cd /kaggle/working/repo/beni/experiment/beni_pilot
!pwd
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 4 — TRAINING: BanglaBERT on T4 (~2–3 hours)
# ──────────────────────────────────────────────────────────────────────
# Saves model to: /kaggle/working/outputs/models/banglabert_economic_potrika-timeseries/
# Zips outputs so you can download the trained model immediately.
"""
!python3 train.py \
    --task economic \
    --model-type banglabert \
    --data-source potrika-timeseries \
    --data-dir "{DATA_DIR}" \
    --banglabert-batch-size 32 \
    --banglabert-epochs 3 \
    --zip

# ⬇️ DOWNLOAD THIS ZIP: go to Data → Output → find beni_economic_potrika-timeseries_*.zip
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 4.5 — McNEMAR'S TEST: TF-IDF vs BanglaBERT on test set (~5 min)
# ──────────────────────────────────────────────────────────────────────
# Depends on: Cell 4 (trained model must exist)
# Tests if BanglaBERT's accuracy improvement over TF-IDF is statistically
# significant using McNemar's paired chi-square test.
"""
import sys, joblib, torch, numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score
from scipy.stats import chi2
from torch.utils.data import DataLoader

sys.path.insert(0, "/kaggle/working/repo/beni/experiment/beni_pilot")
from data import load_potrika_timeseries
from config import ExperimentConfig
from banglabert import BanglaBERTDataset
from transformers import ElectraForSequenceClassification, ElectraTokenizerFast

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"McNemar test device: {device}", flush=True)

# --- Load test set ---
cfg = ExperimentConfig(potrika_dir=DATA_DIR / "potrika")
splits = load_potrika_timeseries(cfg)
test = splits["test"]
texts = test["text_norm"].tolist()
labels = test["economic_relevance"].tolist()
print(f"Test set: {len(texts)} articles", flush=True)

# --- TF-IDF predictions ---
tfidf_path = DATA_DIR / "models" / "economic_potrika-timeseries_tfidf_logreg.joblib"
tfidf = joblib.load(tfidf_path)
tfidf_preds = tfidf.predict(texts)
tfidf_acc = accuracy_score(labels, tfidf_preds)
tfidf_f1 = f1_score(labels, tfidf_preds, average="macro")

# --- BanglaBERT predictions ---
model_path = "/kaggle/working/outputs/models/banglabert_economic_potrika-timeseries"
print(f"Loading BanglaBERT from {model_path}...", flush=True)
tokenizer = ElectraTokenizerFast.from_pretrained(str(model_path))
model = ElectraForSequenceClassification.from_pretrained(str(model_path))
model.to(device)
model.eval()

dataset = BanglaBERTDataset(texts, [0] * len(texts), tokenizer, cfg)
loader = DataLoader(dataset, batch_size=cfg.banglabert_batch_size, shuffle=False)

bert_preds = []
for batch in loader:
    input_ids = batch["input_ids"].to(device)
    attention_mask = batch["attention_mask"].to(device)
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=-1)
        bert_preds.extend(preds.cpu().numpy())

bert_acc = accuracy_score(labels, bert_preds)
bert_f1 = f1_score(labels, bert_preds, average="macro")

# --- Contingency table ---
n00 = n01 = n10 = n11 = 0
for t, a, b in zip(labels, tfidf_preds, bert_preds):
    if a == t and b == t:    n00 += 1
    elif a == t and b != t:  n01 += 1
    elif a != t and b == t:  n10 += 1
    else:                     n11 += 1

stat = (abs(n01 - n10) - 1) ** 2 / (n01 + n10 + 1e-10)
p = chi2.sf(stat, 1)

print("")
print("=" * 72)
print("McNemar's Test: TF-IDF vs BanglaBERT")
print("=" * 72)
print(f"  Test set size:        {len(texts)}")
print(f"  Both correct:         {n00:5d}")
print(f"  TF-IDF only correct:  {n01:5d}  (TF-IDF ✓, BanglaBERT ✗)")
print(f"  BanglaBERT only corr: {n10:5d}  (BanglaBERT ✓, TF-IDF ✗)")
print(f"  Both wrong:           {n11:5d}")
print(f"  χ² = {stat:.2f},  p = {p:.4f}")
print(f"  Significant at α=0.05: {'YES' if p < 0.05 else 'NO'}")
print(f"  BanglaBERT net improvement: {n10 - n01} fewer errors", flush=True)
print("")
print(f"  TF-IDF accuracy:      {tfidf_acc:.4f}  macro F1: {tfidf_f1:.4f}")
print(f"  BanglaBERT accuracy:  {bert_acc:.4f}  macro F1: {bert_f1:.4f}")
print(f"  Δ accuracy:           {bert_acc - tfidf_acc:+.4f}")
print("=" * 72)
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 5 — BUILD INDEX: Predict all 120k articles with BanglaBERT (~45 min)
# ──────────────────────────────────────────────────────────────────────
# Depends on: Cell 4 (trained model must exist)
"""
!python3 build_index.py \
    --data-dir "{DATA_DIR}" \
    --model-type banglabert \
    --zip

# ⬇️ DOWNLOAD THIS ZIP: beni_index_*.zip → contains narrative_index.csv + full_predictions.parquet
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 6 — CORRELATE: Level + differenced + lead correlations (<30 sec)
# ──────────────────────────────────────────────────────────────────────
# Depends on: Cell 5 (narrative_index.csv must exist)
"""
!python3 correlate.py \
    --data-dir "{DATA_DIR}" \
    --zip

# ⬇️ DOWNLOAD THIS ZIP: beni_correlate_*.zip → contains correlations.csv
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 7 — COMPARE: BanglaBERT vs TF-IDF correlations
# ──────────────────────────────────────────────────────────────────────
"""
import pandas as pd

# Load the new BanglaBERT correlations
bangla_corr = pd.read_csv("/kaggle/working/outputs/index/correlations.csv")

# Load the old TF-IDF correlations (backed up in the dataset)
tfidf_corr = pd.read_csv(DATA_DIR / "outputs" / "index" / "correlations.csv")

print("=" * 72)
print("TF-IDF vs BanglaBERT — Correlation Comparison")
print("=" * 72)

for _, row in bangla_corr.iterrows():
    freq = row["frequency"]
    x = row["x"]
    y = row["y"]
    r_new = row["pearson_r"]
    p_new = row["pearson_p"]
    n_new = row["n"]

    # Find matching row in TF-IDF
    match = tfidf_corr[
        (tfidf_corr["frequency"] == freq) &
        (tfidf_corr["x"] == x) &
        (tfidf_corr["y"] == y)
    ]
    if len(match) == 1:
        r_old = match.iloc[0]["pearson_r"]
        diff = r_new - r_old
        marker = " *** IMPROVED ***" if abs(r_new) > abs(r_old) and p_new < 0.1 else ""
        print(f"  [{freq:20s}] {x:15s} vs {y:12s}  "
              f"TF-IDF r={r_old:7.4f} → BanglaBERT r={r_new:7.4f} (Δ={diff:+.4f}){marker}")
    else:
        print(f"  [{freq:20s}] {x:15s} vs {y:12s}  r={r_new:7.4f}  (BanglaBERT only)")

print("")
print("Key question: Did BanglaBERT improve the differenced (short-run) correlations?")
"""

# ──────────────────────────────────────────────────────────────────────
# Cell 8 — Zip & download all outputs
# ──────────────────────────────────────────────────────────────────────
"""
import shutil
from datetime import datetime

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_path = f"/kaggle/working/beni_full_pipeline_{ts}"
shutil.make_archive(zip_path, "zip", "/kaggle/working/outputs")
final_path = f"{zip_path}.zip"

size_mb = os.path.getsize(final_path) / 1024**2
print(f"Results zipped: {final_path} ({size_mb:.0f} MB)")
print("")
print("To download:")
print("  1. In the notebook sidebar, go to Data → Output")
print(f"  2. Find {final_path.split('/')[-1]} under /kaggle/working/")
print("  3. Click the download button")
print("")
print("Or run this cell to list all output files:")
print("  !find /kaggle/working/outputs -type f")
"""

# ──────────────────────────────────────────────────────────────────────
# (Optional) Cell 9 — List all outputs + final safety zip
# ──────────────────────────────────────────────────────────────────────
# Use this after any cell to verify outputs exist and grab a complete zip.
"""
import os, shutil
from datetime import datetime
from pathlib import Path

# List everything
print("=== All output files ===")
for f in sorted(Path("/kaggle/working/outputs").rglob("*")):
    if f.is_file():
        size_mb = f.stat().st_size / 1024**2
        print(f"  {f.relative_to('/kaggle/working/outputs')} [{size_mb:.1f} MB]")

# Safety zip of everything
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_path = f"/kaggle/working/ALL_RESULTS_{ts}"
shutil.make_archive(zip_path, "zip", "/kaggle/working/outputs")
final = f"{zip_path}.zip"
print(f"\n⬇️  DOWNLOAD: {final} ({os.path.getsize(final)/1024**2:.0f} MB)")
print("    Go to Data → Output → click download button")
"""
