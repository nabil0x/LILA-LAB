# Replication Plan: 15-20 Representative Papers from JER Systematic Review

## Overview
Replicate papers across 4 eras to build comprehensive research baseline for BENI validation.

---

## Era 1: Dictionary-Based Methods (2007-2015) — 4-5 Papers

### Paper 1.1: **Tetlock (2007)** — Foundation
- **Method**: General Inquirer lexicon + PCA
- **Data**: Wall Street Journal "Abreast of Market" column (1984-1999)
- **Target**: Stock returns, trading volume
- **Key Result**: Sentiment predicts next-day returns (15-25% RMSE reduction)
- **Reproducibility**: ✅ High (WSJ archive available)
- **Effort**: 2-3 days
- **Replication Path**:
  1. Load WSJ archive (or use NewsAPI proxy)
  2. Build General Inquirer encoder (77 word categories → PCA)
  3. Extract pessimism factor
  4. Regress on market returns (VAR framework)
  5. Validate Granger causality

### Paper 1.2: **Gentzkow, Shapiro & Taddy (2019)** — Policy Uncertainty
- **Method**: Keyword extraction + time-series aggregation
- **Data**: Newspaper archives (LexisNexis, public newspapers)
- **Target**: GDP growth, policy uncertainty
- **Key Result**: EPU index predicts recessions 3-12 months ahead
- **Reproducibility**: ✅ High (EPU index is published; replicate methodology)
- **Effort**: 3-4 days
- **Replication Path**:
  1. Define policy uncertainty keywords (tax, fiscal, regulation, uncertainty)
  2. Download newspaper text (ProPublica archive or similar)
  3. Count keyword frequency by date
  4. Normalize (z-score) by category
  5. Construct EPU index (average of categories)
  6. Correlate with recession timing

### Paper 1.3: **Lucey & Dowling (2005)** or Similar — Sentiment & Stock Volatility
- **Method**: Dictionary-based sentiment (simpler than Tetlock)
- **Data**: Financial news snippets
- **Target**: Volatility prediction
- **Key Result**: Sentiment predicts volatility (20-28% improvement)
- **Reproducibility**: ⚠️ Medium (depends on data source)
- **Effort**: 2-3 days
- **Replication Path**:
  1. Collect financial news (Yahoo Finance, Bloomberg proxies)
  2. Apply pre-built sentiment lexicon (Loughran-McDonald)
  3. Aggregate daily sentiment
  4. Forecast volatility (GARCH model)
  5. Compare with/without sentiment

### Paper 1.4: **Boudoukh et al. (2013)** or Similar — Media Tone & Commodities
- **Method**: Media tone analysis + event detection
- **Data**: News about commodities (oil, metals, agriculture)
- **Target**: Commodity prices
- **Key Result**: Tone predicts price movements (10-20% improvement)
- **Reproducibility**: ⚠️ Medium
- **Effort**: 2-3 days

### Paper 1.5: **One Additional Dictionary Study** (Domain-Specific)
- Examples: Healthcare sentiment, Real estate sentiment, etc.
- **Effort**: 2-3 days

**Era 1 Total Effort**: 12-16 days

---

## Era 2: Traditional ML Methods (2013-2019) — 3-4 Papers

### Paper 2.1: **Naive Bayes + TF-IDF Classification**
- **Method**: SVM or Naive Bayes for sentiment classification
- **Data**: Labeled financial news or tweets
- **Target**: Binary/ternary sentiment → Forecasting
- **Typical Result**: 75-85% accuracy, 12-18% RMSE improvement
- **Reproducibility**: ✅ High (standard ML pipeline)
- **Effort**: 2-3 days
- **Replication Path**:
  1. Load labeled news dataset (e.g., SemEval financial news corpus)
  2. Preprocess: tokenize, lemmatize, remove stopwords
  3. Vectorize: TF-IDF
  4. Train: SVM or NB with 80/20 split
  5. Evaluate: Accuracy, F1, ROC-AUC
  6. Use predictions for forecasting

### Paper 2.2: **Random Forest + Feature Engineering**
- **Method**: RF with hand-crafted features (word counts, sentiment scores, volatility indicators)
- **Data**: News + market data
- **Target**: Market movement (up/down/neutral)
- **Typical Result**: 75-85% accuracy
- **Reproducibility**: ✅ High
- **Effort**: 2-3 days

### Paper 2.3: **Gradient Boosting (XGBoost) + Time-Series Features**
- **Method**: XGBoost with lagged sentiment, technical indicators
- **Data**: Financial news + OHLCV data
- **Target**: Next-day return prediction
- **Typical Result**: 52-58% accuracy (barely above random, but robust)
- **Reproducibility**: ✅ High
- **Effort**: 2-3 days

### Paper 2.4: **Support Vector Machine (SVM) with Custom Kernels** (Optional)
- **Effort**: 2-3 days (if time permits)

**Era 2 Total Effort**: 8-12 days

---

## Era 3: Deep Learning / Transformers (2018-2025) — 5-6 Papers

### Paper 3.1: **LSTM for Sentiment Time-Series**
- **Method**: LSTM encoder → sentiment sequence → forecasting
- **Data**: Time-indexed news + prices
- **Target**: Price or volatility prediction
- **Typical Result**: 85-90% accuracy, 15-22% RMSE improvement
- **Reproducibility**: ✅ High (PyTorch/TensorFlow standard)
- **Effort**: 3-4 days
- **Replication Path**:
  1. Load financial news with timestamps
  2. Embed text (GloVe or pretrained)
  3. Build LSTM: input=text_embedding, hidden=128, output=sentiment_score
  4. Create time-series of sentiments
  5. LSTM forecasting: 30-day lookback → next-day return
  6. Evaluate: MAE, RMSE, direction accuracy

### Paper 3.2: **BERT / DistilBERT for Sentiment Classification**
- **Method**: Fine-tuned BERT on financial text
- **Data**: Labeled financial news or earnings calls
- **Target**: Sentiment (positive/negative/neutral) → Forecasting
- **Typical Result**: 85-92% accuracy
- **Reproducibility**: ✅ High (HuggingFace models)
- **Effort**: 3-4 days
- **Replication Path**:
  1. Load FinBERT or standard BERT
  2. Fine-tune on labeled financial news (e.g., SemEval-2017 Task 5)
  3. Evaluate: Accuracy, F1, Matthews CC
  4. Extract embeddings for downstream forecasting
  5. Compare to LSTM baseline

### Paper 3.3: **GPT/LLM Zero-Shot Sentiment** (Emerging Trend)
- **Method**: GPT-3 or similar for zero-shot sentiment classification
- **Data**: News snippets (no labeled training)
- **Target**: Sentiment category
- **Typical Result**: 88-95% accuracy (but inference cost high)
- **Reproducibility**: ⚠️ Medium (API costs, no training)
- **Effort**: 1-2 days (if using OpenAI API; skip if cost prohibited)

### Paper 3.4: **Attention Mechanisms for Interpretability**
- **Method**: BERT + attention weights for key phrase extraction
- **Data**: Financial news
- **Target**: Which phrases drive sentiment? Which predict prices?
- **Reproducibility**: ✅ High
- **Effort**: 2-3 days

### Paper 3.5: **Multi-Task Learning** (Domain + Sentiment)
- **Method**: BERT head for topic classification + sentiment head (like BENI pilot)
- **Data**: News with topic labels
- **Target**: Jointly predict topic and sentiment
- **Reproducibility**: ✅ High
- **Effort**: 2-3 days

### Paper 3.6: **RoBERTa for Cross-Domain Transfer** (Optional)
- **Method**: Fine-tune RoBERTa on one domain, test on another
- **Effort**: 2-3 days (if time permits)

**Era 3 Total Effort**: 15-21 days

---

## Era 4: Validation & Meta-Analysis (Cross-Paper Best Practices) — 2-3 Papers

### Paper 4.1: **Best Practices in Out-of-Sample Testing**
- **Extract from**: 5-10 papers that emphasize rigorous validation
- **Key Practices**:
  - Real-time data discipline (no look-ahead bias)
  - Walk-forward validation
  - Diebold-Mariano test for model comparison
  - Multiple baselines (AR(1), ARIMA, professional forecasts)
- **Reproducibility**: ✅ High (meta-analysis only)
- **Effort**: 2-3 days

### Paper 4.2: **Publication Bias & Meta-Regression**
- **Extract from**: Meta-analysis studies (e.g., Algaba et al. 2020)
- **Methods**:
  - Funnel plots (effect size vs. precision)
  - Trim-and-fill for bias correction
  - Meta-regression (study characteristics vs. effect size)
- **Reproducibility**: ✅ High (use metafor R package or Python equivalent)
- **Effort**: 2-3 days

### Paper 4.3: **Reproducibility Checklist**
- **Develop from**: Papers emphasizing transparency/reproducibility
- **Checklist Items**:
  - Code availability
  - Seed control
  - Hyperparameter specification
  - Dataset accessibility
  - Evaluation on held-out test set
- **Effort**: 1-2 days

**Era 4 Total Effort**: 5-8 days

---

## BENI Integration (Original Contribution) — 2-3 Days

### Integration Task 1: Domain-Aware Multi-Task Learning
- Extend BENI pilot (already done) to match Transformer best practices
- Add BERT backbone option (vs. TF-IDF)
- Implement walk-forward validation

### Integration Task 2: Time-Series Regime Detection (Novel)
- Implement Shift Detection algorithm (already drafted)
- Validate against synthetic + real data

### Integration Task 3: Comparison Matrix
- Compare BENI (time-series domain model) vs. replicated papers
- Metric: RMSE improvement, interpretability, computational cost

**BENI Integration Total Effort**: 2-3 days

---

## Total Project Timeline

| Era | Papers | Effort |
|-----|--------|--------|
| Dictionary-Based | 4-5 | 12-16 days |
| Traditional ML | 3-4 | 8-12 days |
| Transformers | 5-6 | 15-21 days |
| Validation/Meta | 2-3 | 5-8 days |
| BENI Integration | 1 (original) | 2-3 days |
| **TOTAL** | **15-20** | **42-60 days** |

---

## Phased Delivery

### Phase 1: Foundation (Weeks 1-2) — 8-10 days
- Replicate 2 dictionary papers (Tetlock, Gentzkow)
- Build data pipeline + evaluation framework
- Checkpoint: Validate 15-25% RMSE improvement claim

### Phase 2: Baselines (Weeks 3-4) — 8-10 days
- Replicate 3 ML papers (SVM, RF, XGBoost)
- Compare to dictionary baselines
- Checkpoint: Show ML outperforms dictionary on accuracy

### Phase 3: Deep Learning (Weeks 5-6) — 10-14 days
- Replicate 3-4 transformer papers (LSTM, BERT, RoBERTa)
- Implement attention visualization
- Checkpoint: Confirm 85-92% accuracy, 18-22% RMSE improvement

### Phase 4: Validation (Week 7) — 5-8 days
- Meta-analysis of best practices
- Build reproducibility checklist
- Checkpoint: Identify which papers use rigorous protocols (only 18% real-time)

### Phase 5: Integration (Week 8) — 2-3 days
- Integrate BENI into comparison framework
- Build reproducibility dashboard
- Final checkpoint: All 15-20 papers in unified evaluation

---

## Key Replication Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Data Unavailability** | Use NewsAPI, Yahoo Finance, public archives; synthetic proxies where needed |
| **Hyperparameter Details Missing** | Use standard defaults from similar papers; clearly mark assumptions |
| **Non-Reproducible Results** | Document why (data drift, randomness); validate on similar datasets |
| **Computational Cost** | Use smaller models (DistilBERT vs. BERT), subset data, batch processing |
| **Different Baselines Across Papers** | Standardize all replications to same baselines (AR(1), ARIMA, SPF) |

---

## Output Deliverables

1. **Per-Paper Implementation**:
   - `era1_tetlock_2007.py` (dictionary baseline)
   - `era2_svm_ml.py` (SVM classifier)
   - `era3_bert_transformer.py` (BERT sentiment)
   - etc.

2. **Unified Framework**:
   - `replications/` directory with all 15-20 papers
   - `config.yaml` (hyperparameters for all)
   - `comparison_matrix.py` (evaluation harness)

3. **Dashboard**:
   - `results/reproducibility_report.html`
   - Metrics table: Paper, Method, Accuracy, RMSE, Real-Time?, Reproducible?

4. **BENI Integration**:
   - `beni_integrated.py` (BENI in unified framework)
   - Comparison: BENI vs. dictionary vs. ML vs. transformers

5. **Meta-Analysis Report**:
   - Publication bias analysis
   - Effect size synthesis
   - Research gaps visualization

---

## Success Criteria

✅ **Replication Success**:
- Tetlock (2007): ±5% of reported 15-25% RMSE improvement
- Gentzkow et al.: Policy uncertainty index correlates with GDP (r > 0.6)
- ML papers: 75-85% accuracy ±3%
- Transformer papers: 85-92% accuracy ±2%

✅ **Framework Quality**:
- All code is modular, documented, seed-controlled
- Reproducible from scratch with single command: `python run_all_replications.py`
- Results logged with timestamps, hyperparameters, data splits

✅ **BENI Positioning**:
- Clear comparison: BENI (domain dynamics) vs. single-sentiment baselines
- Show novelty: Time-series regime detection outperforms snapshot sentiment on specific tasks

---

## Recommended Starting Point

**If you have 2 weeks**: Do Phase 1 (Dictionary methods) + Phase 2 (ML methods) = 16-20 days
- Validates field consensus: "Dictionary baseline + ML improves forecast"
- Foundation for BENI positioning

**If you have 4-5 weeks**: Do Phase 1-3 = 26-34 days
- Covers all methodological eras
- Strong empirical breadth

**If you have 8+ weeks**: Do all 5 phases = 42-60 days
- Complete reproducibility suite
- Meta-analysis + BENI integration
- Ready for publication-grade validation

Ready to start Phase 1?
