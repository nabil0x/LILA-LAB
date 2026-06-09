# BENI — Kaggle Experiment Guide

Full pipeline for the Bangla Economic Narrative Index (BENI):

```
Potrika news → classify economic relevance → aggregate by month → BENI index → correlate with macro
```

---

## 1. Local: Prepare & Upload Data Bundle

Run once on your local machine to gather all data:

```bash
cd beni/experiment/scripts/
python3 prepare_kaggle_data.py
```

This creates `beni/experiment/data/kaggle/beni-data/` with:

| Subdirectory | Contents | Size |
|---|---|---|
| `potrika/` | 47 Potrika CSV files (2014–2020, 8 categories) | 3.3 GB |
| `macro/` | BIS FX, IMF CPI, IMF FX, World Bank Reserves | ~200 KB |
| `models/` | Pre-trained TF-IDF + Logistic Regression model | 4 MB |
| `outputs/index/` | Previous TF-IDF narrative index + correlations (for continuity) | ~5 MB |

**Not included** (downloaded automatically in the notebook):
- BanglaBERT model (424 MB) — downloaded from Hugging Face at first use

Zip and upload as Kaggle Dataset:

```bash
cd beni/experiment/data/kaggle/
zip -r beni-data.zip beni-data/

# Upload beni-data.zip → Kaggle → Create Dataset → Private
# Dataset name: annnasernabil/beni-data
```

**⚠️ Dataset mount path note:** The zip contains a `beni-data/` root directory, so on Kaggle the data will be available at:
- `/kaggle/input/datasets/annnasernabil/beni-data/beni-data/` (explicit owner-slug path)
- The inner `beni-data/` is what you pass as `--data-dir`.

---

## 2. Kaggle Notebook: Full Pipeline Run

### Recommended: Use `kaggle_pipeline.py` (one-shot notebook)

The file `beni_pilot/kaggle_pipeline.py` is a self-contained notebook script designed for Kaggle T4 GPU.

**How to use:**
1. Create a new Kaggle Notebook with **GPU T4 x1** accelerator
2. Add the dataset `annnasernabil/beni-data` to the notebook (right sidebar → Add Data)
3. Upload `kaggle_pipeline.py` as a notebook source:
   - File → Import Notebook → Select `kaggle_pipeline.py`
   - Or paste cell-by-cell into a new notebook
4. **Run All** (≈3 hours total)

**What it does:**
| Cell | Step | Time |
|------|------|------|
| 1–3 | Install deps, detect data path, clone repo | ~2 min |
| 4 | **Train BanglaBERT** (70k × 3 epochs, batch_size=32) | ~2–3 hrs |
| 5 | **Build narrative index** (predict 120k articles) | ~45 min |
| 6 | **Correlate with macro** indicators | <30 sec |
| 7 | **Compare** BanglaBERT vs TF-IDF correlations | <30 sec |
| 8–9 | Zip outputs + list files | <1 min |

### Manual approach (if you prefer step-by-step)

#### Setup

```python
# In a Kaggle Notebook with GPU T4 x 1 accelerator,
# with dataset annnasernabil/beni-data added:

# Auto-detect data directory (handles both mount path formats)
import os
from pathlib import Path

for cand in [
    Path("/kaggle/input/datasets/annnasernabil/beni-data/beni-data"),
    Path("/kaggle/input/beni-data/beni-data"),
    Path("/kaggle/input/beni-data"),
]:
    if (cand / "potrika").exists():
        DATA_DIR = cand
        break
print(f"DATA_DIR={DATA_DIR}")

# Clone code
!git clone --depth 1 https://github.com/annnasernabil/economic-narrative-indices.git /kaggle/working/repo
%cd /kaggle/working/repo/beni/experiment/beni_pilot

# Install dependencies
!pip install -q transformers sentencepiece accelerate
```

#### Step 1 — Train BanglaBERT

```python
# T4, ~2–3 hours for 70k articles × 3 epochs
!python3 train.py \
    --task economic \
    --model-type banglabert \
    --data-source potrika-timeseries \
    --data-dir "{DATA_DIR}" \
    --banglabert-batch-size 32 \
    --banglabert-epochs 3
```

#### Step 2 — Build narrative index

```python
# Predict on all 120k articles → monthly index
!python3 build_index.py \
    --data-dir "{DATA_DIR}" \
    --model-type banglabert
```

#### Step 3 — Correlate with macro

```python
# Level + differenced + lead correlations
!python3 correlate.py \
    --data-dir "{DATA_DIR}"
```

#### Step 4 — Compare vs TF-IDF

```python
import pandas as pd

bangla = pd.read_csv("/kaggle/working/outputs/index/correlations.csv")
tfidf  = pd.read_csv(f"{DATA_DIR}/outputs/index/correlations.csv")

# Print comparison table (see kaggle_pipeline.py for full code)
```

### Download Results

```python
import shutil, os
from datetime import datetime
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_path = f"/kaggle/working/beni_full_pipeline_{ts}"
shutil.make_archive(zip_path, "zip", "/kaggle/working/outputs")
print(f"Zipped: {zip_path}.zip ({os.path.getsize(zip_path + '.zip')/1024**2:.0f} MB)")
```

Then in the notebook sidebar: **Data → Output** → find the zip under `/kaggle/working/` → download.

### TF-IDF Baseline Only (No GPU needed)

```python
!python3 build_index.py \
    --data-dir "{DATA_DIR}" \
    --model-type tfidf

!python3 correlate.py \
    --data-dir "{DATA_DIR}"
```

---

## 3. What the Outputs Mean

After running the pipeline, you'll have:

| File | Contents |
|---|---|
| `outputs/index/narrative_index.csv` | 79-month BENI index (2014-06 to 2020-12) |
| `outputs/index/full_predictions.parquet` | Per-article economic probability scores |
| `outputs/index/correlations.csv` | Level + differenced correlations with FX, CPI, Reserves |
| `outputs/reports/economic_potrika-timeseries_banglabert_metrics.json` | BanglaBERT test metrics |
| `outputs/models/banglabert_economic_potrika-timeseries/` | Fine-tuned BanglaBERT weights |

### Correlation Interpretation

| Correlation Type | FX (BDT/USD) | CPI | Reserves |
|---|---|---|---|
| **Level** | r ≈ -0.72 (long-run trend) | r ≈ -0.75 (long-run trend) | r ≈ -0.77 |
| **First-differenced** | r ≈ 0.10 (no short-run signal) | r ≈ -0.04 | — |

- Strong **level** correlations = economic news share tracks the long-run macro trajectory
- Weak **differenced** correlations = month-to-month movements don't predict short-run macro changes
- **Key question**: Does BanglaBERT improve the differenced signal? (That's the experiment.)

---

## 4. Re-running with New Data

To extend beyond 2020:

1. Download more Potrika CSVs → add to `potrika/` before re-bundling
2. Run `prepare_kaggle_data.py` again with updated data
3. Re-upload as a new Kaggle Dataset version
4. Re-train BanglaBERT on the expanded dataset
5. Rebuild index and correlations

For the macro data, update CSVs in `macro/` before bundling, or run `scripts/download_macro.py` locally.

---

## 5. File Reference

All Python scripts in `beni/experiment/beni_pilot/`:

| Script | Purpose | `--data-dir` support | `--zip` support |
|---|---|---|---|
| `train.py` | Train TF-IDF or BanglaBERT | ✅ | ✅ |
| `build_index.py` | Build narrative index from model | ✅ | ✅ |
| `correlate.py` | Correlate index with macro | ✅ | ✅ |
| `eval.py` | Evaluate saved model | ❌ | ❌ |
| `potrika.py` | Export Economy subset from Potrika | ❌ | ❌ |
| `predict.py` | Predict single text | ❌ | ❌ |
| `dashboard.py` | Streamlit dashboard | ❌ | ❌ |
| `banglabert.py` | BanglaBERT training module (imported by train.py) | — | — |
| `config.py` | Experiment configuration dataclass | — | — |
| `data.py` | Data loaders | — | — |
| `utils.py` | Helpers: zip, JSON, seed, dirs | — | — |

All scripts accept `--help` for full argument documentation.

---

## 6. Hardware Notes

| Stage | Recommended GPU | VRAM | Time |
|---|---|---|---|
| TF-IDF training | CPU (any) | — | ~2 minutes |
| BanglaBERT training (70k × 3 epochs) | T4 / P100 | 16 GB | ~2–3 hours |
| Narrative index (BanglaBERT, 120k articles) | T4 / P100 | 16 GB | ~45 min |
| Narrative index (TF-IDF, 120k articles) | CPU | — | ~2 min |
| Correlations | CPU | — | < 30 sec |
