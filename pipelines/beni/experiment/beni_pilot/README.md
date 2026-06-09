# BENI Pilot Experiment

First runnable pipeline for the Bangla Economic Narrative Index (BENI) project.

## Pipeline

```
Raw news → classify economic relevance → aggregate by month → BENI index → correlate with macro
   ✅            ✅ (TF-IDF)                 ✅                    ✅               ✅
```

## Data

### Potrika (primary source)
- **Source**: Mendeley Data `10.17632/v362rp78dc.4` (CC BY 4.0)
- **Period**: 2014-2020
- **Sources**: Jugantor, Ittefaq, Kaler Kontho, Inqilab, Jaijaidin, Somoyer Alo
- **Categories**: Economy, National, Politics, Worldnews, Sports, Education, Entertainment, Science & Technology
- **Local**: 39 CSV files, 3.3 GB in `../data/raw/potrika/`
- **Processor**: `potrika.py` exports Economy subset → `../data/processed/potrika_economy.csv` (40,451 articles)

### BanglaNLP (baseline only)
- News categorization benchmark from `banglanlp/bnlp-resources` (train/dev/test TSV)
- Used only for initial prototype; replaced by Potrika for actual experiments

### Macroeconomic indicators
| Series | Source | Period | File |
|--------|--------|--------|------|
| BDT/USD FX | BIS API | 2014–2025 monthly | `macro/fx_bdt_usd_bis_eop_monthly.csv` |
| CPI (Bangladesh) | IMF SDMX | 2010–2026 monthly | `macro/cpi_imf_bgd_index_monthly.csv` |
| BDT/USD FX | IMF | 1972–2026 monthly | `macro/fx_bdt_usd_imf_eop_monthly.csv` |
| Reserves | World Bank API | 2014–2024 annual | `macro/reserves_wb_annual.csv` |

Downloader: `../scripts/download_macro.py`

## Models

### TF-IDF + Logistic Regression (baseline — complete)
- `TfidfVectorizer(max_features=80000, min_df=2, ngram_range=(1,2))`
- `OneVsRestClassifier(LogisticRegression(class_weight='balanced'))`
- Trained on **potrika-timeseries** (70k train / 21k val / 30k test)

| Task | Dataset | Accuracy | Macro F1 |
|------|---------|----------|----------|
| Topic classification | BNLP test | 89.4% | 0.860 |
| Economic relevance | BNLP test (weak labels) | 95.0% | 0.750 |
| Economic relevance | **Potrika timeseries** | **91.7%** | **0.894** |

### BanglaBERT (wired — needs Kaggle for full training)
- Model: `csebuetnlp/banglabert` (Electra-based, 424 MB)
- Fine-tuning pipeline: `banglabert.py` with fp16 mixed precision
- Config tuned for 6 GB GPU: `batch_size=4`, `max_len=128`, `learning_rate=2e-5`
- Validated: forward pass + gradient step works locally
- Full 70k×3 epoch training → reserved for Kaggle (T4/P100)

## Scripts

| Script | Purpose |
|--------|---------|
| `train.py` | Train model (`--model-type tfidf` or `banglabert`, `--data-source bnlp/potrika/potrika-timeseries`) |
| `build_index.py` | Load trained TF-IDF model, predict on all 120k articles, aggregate monthly → narrative index |
| `correlate.py` | Merge narrative index with macro data, compute level + first-differenced correlations |
| `eval.py` | Evaluate saved model on a split |
| `narrative.py` | Lexicon-based narrative force/topic/target scoring (standalone) |
| `potrika.py` | Export Economy subset from Potrika CSVs |
| `dashboard.py` | Streamlit dashboard for exploration |

## Commands

```bash
# Train baseline
python3 train.py --task economic --model-type tfidf --data-source potrika-timeseries

# Build narrative index (from trained model)
python3 build_index.py

# Correlate with macro indicators
python3 correlate.py

# Export Potrika Economy articles
python3 potrika.py --category Economy

# Evaluate
python3 eval.py --task economic --model-type tfidf

# Predict single text
python3 predict.py --text "বাংলাদেশ ব্যাংক রিজার্ভ ও ডলার বাজার"
```

## Outputs

```
outputs/
├── models/
│   ├── topic_tfidf_logreg.joblib
│   ├── economic_tfidf_logreg.joblib
│   └── economic_potrika-timeseries_tfidf_logreg.joblib
├── reports/
│   ├── dataset_summary.json
│   ├── topic_metrics.json
│   ├── economic_metrics.json
│   ├── economic_potrika-timeseries_metrics.json
│   └── train_sample_with_pseudo_economic_labels.csv
└── index/
    ├── narrative_index.csv          # 79-month BENI index (2014-06 to 2020-12)
    ├── full_predictions.parquet     # All 120k article-level predictions
    └── correlations.csv             # 50 correlation pairs (level + differenced)
```

## Narrative Index — Key Results

- **79 monthly observations**, June 2014 – December 2020
- **Mean economic share**: 38.9% (range: 21.1% – 80.6%)
- **Declining trend**: economic news share dropped from ~75% (2014) to ~25% (2020)

### Correlations with Macro Indicators

| Measure | FX (BDT/USD) | CPI | Reserves |
|---------|--------------|-----|----------|
| **Level** (raw) | r = -0.72** | r = -0.75** | r = -0.77* |
| **First-differenced** (detrended) | r = 0.10 | r = -0.04 | — |

**Interpretation**: The strong level correlations are driven by shared long-run trends. Month-to-month movements in economic news share do not significantly correlate with month-to-month macro changes. This could mean the TF-IDF index captures structural shifts but not short-term noise — or that BanglaBERT is needed for finer-grained signal.

## Next Steps

1. Run full BanglaBERT training on Kaggle (T4/P100, ~2-3 hrs)
2. Rebuild narrative index with BanglaBERT predictions
3. Re-run correlations — does detrended signal improve?
4. Add manual annotation of 300 articles for proper validation
5. Extend to narrative force/topic layers (narrative.py)

## Requirements

See `requirements.txt`. Key dependencies:
- scikit-learn, pandas, numpy
- torch, transformers (for BanglaBERT)
- scipy (for correlations)
- joblib, pyarrow (for model/data serialization)
- streamlit, plotly (for dashboard)
