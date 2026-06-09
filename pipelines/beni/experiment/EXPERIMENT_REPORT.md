# BENI Pilot Experiment Report

## 1. Overview

End-to-end pipeline for the Bangla Economic Narrative Index (BENI):

```
Potrika news CSVs → load + clean → TF-IDF classifier → predict 120k articles → monthly aggregation → correlation with macro indicators
                                                                                                                          
BanglaBERT (wired, pending Kaggle) ────────────────────────→ upgrade classifier → rebuild index → compare correlations
```

## 2. Data

### Potrika News (primary)
- **Source**: Mendeley Data `10.17632/v362rp78dc.4` — 664,880 articles from 6 Bangla newspapers
- **Period**: 2014–2020
- **Categories**: Economy, National, Politics, Worldnews, Sports, Education, Entertainment, Science & Technology
- **Local storage**: 39 CSV files, 3.3 GB in `data/raw/potrika/`
- **Timeseries loader**: `load_potrika_binary_timeseries()` loads Economy (positive, 38k) + samples National/Politics/Worldnews (negative, ~82k) with date-based train/val/test split
- **Split sizes**: train=69,735, val=20,765, test=30,207

### Macroeconomic Indicators
| Indicator | Source | Frequency | Period | Method |
|-----------|--------|-----------|--------|--------|
| BDT/USD FX | BIS API | Monthly | 2014–2025 | Direct API (no auth) |
| CPI Index | IMF SDMX | Monthly | 2010–2026 | SDMX REST API |
| BDT/USD FX | IMF | Monthly | 1972–2026 | SDMX REST API |
| Reserves (USD) | World Bank API | Annual | 2014–2024 | World Bank API v2 |

All downloaded programmatically via `scripts/download_macro.py`.

## 3. Models

### TF-IDF + Logistic Regression (baseline — complete)

**Architecture**: `TfidfVectorizer(max_features=80000, min_df=2, ngram_range=(1,2), sublinear_tf=True)` + `OneVsRestClassifier(LogisticRegression(class_weight='balanced', solver='liblinear'))`

**Results on Potrika timeseries test set**:
- Accuracy: **91.7%**
- Macro F1: **0.894**
- Predicted economic articles: 34.2% (vs ~31.5% positive in ground truth)

The classifier is meaningful but not perfect — it confounds Economy articles with general Policy/State reporting.

### BanglaBERT (wired — full training on Kaggle)

**Architecture**: `csebuetnlp/banglabert` (Electra-based, 423 MB) → `ElectraForSequenceClassification(num_labels=2)`

**Local validation passed**:
- Model loads on GPU (6 GB GTX, compute cap 7.5)
- Forward pass + gradient step works with fp16 mixed precision
- Batch size 4, max_len 128 fits in 1.3 GB GPU memory

**Pending**: Full 70k×3 epoch training on Kaggle (T4/P100, ~2-3 hrs).

## 4. Narrative Index Construction

**Script**: `build_index.py`

**Process**:
1. Load trained TF-IDF pipeline
2. Predict `economic_probability` on all 120,707 articles
3. Aggregate by month → `economic_share` (proportion with prob > 0.5) + `mean_prob`

**Output**: 79 monthly observations, 2014-06 to 2020-12

| Metric | Value |
|--------|-------|
| Months | 79 |
| Mean economic share | 38.9% |
| Min | 21.1% (2020-11) |
| Max | 80.6% (2014-09) |
| Trend | Declining: ~75% → ~25% over period |

## 5. Correlation with Macro Indicators

**Script**: `correlate.py`

**Method**: Pearson + Spearman correlations on both raw levels and first-differences (month-over-month change).

### Level correlations (raw)

| Index component | vs FX (BDT/USD) | vs CPI | vs Reserves |
|----------------|-----------------|--------|-------------|
| economic_share | r = -0.72** | r = -0.75** | r = -0.77* |
| mean_prob | r = -0.69** | r = -0.73** | r = -0.74 |

** p < 0.001, * p < 0.05

### First-differenced correlations (detrended)

| Index component | vs ΔFX | vs ΔCPI |
|----------------|--------|---------|
| Δeconomic_share | r = 0.10 (p=0.38) | r = -0.04 (p=0.73) |
| Δmean_prob | r = 0.11 (p=0.35) | r = -0.06 (p=0.63) |

### Interpretation

The level correlations are strong and significant, but the first-differenced correlations are essentially zero. This means:

1. **Long-run co-movement exists**: The narrative index and macro variables trend together over years. When economic news share was high (2014), the taka was stronger and inflation was lower. As economic share declined, the taka depreciated and inflation rose.

2. **Short-run relationship is absent**: Month-to-month changes in economic news share do not predict or correlate with month-to-month changes in FX or CPI.

3. **Two possible explanations**:
   - (A) The TF-IDF classifier is too coarse — it captures the broad structural shift in news composition but misses the subtle month-to-month narrative signals that a fine-tuned BanglaBERT might detect.
   - (B) The relationship is genuinely long-run only — economic narrative share is a structural variable that moves at annual frequency, not monthly.

Hypothesis (A) can be tested by rebuilding the index with BanglaBERT predictions and re-running the correlations.

## 6. BanglaBERT Training Plan

| Item | Detail |
|------|--------|
| Platform | Kaggle (free T4/P100 GPU, 16 GB VRAM) |
| Model | csebuetnlp/banglabert (Electra) |
| Data | potrika-timeseries (70k train, 21k val, 30k test) |
| Config | batch_size=16, max_len=256, epochs=3, lr=2e-5 |
| Est. time | ~2-3 hours |
| Output | Compare test metrics vs TF-IDF; rebuild index + re-correlate |

## 7. Key Files

| File | Purpose |
|------|---------|
| `beni_pilot/config.py` | Paths, hyperparameters |
| `beni_pilot/data.py` | Data loaders (BNLP + Potrika) |
| `beni_pilot/models.py` | TF-IDF pipeline |
| `beni_pilot/train.py` | Training entry point |
| `beni_pilot/banglabert.py` | BanglaBERT fine-tuning |
| `beni_pilot/build_index.py` | Narrative index construction |
| `beni_pilot/correlate.py` | Macro correlation analysis |
| `beni_pilot/narrative.py` | Lexicon-based narrative scoring |
| `scripts/download_macro.py` | Macro data downloader |
