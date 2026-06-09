# PHASE 2: Theory & Depth - Implementation Guide

## Overview
Phase 2 adds ~2,500-3,000 words of theoretical grounding, methodological depth, and comprehensive analysis. This phase transforms the paper from narrative review to rigorous systematic analysis.

**Target**: Expand from 6,000-6,500 words (after Phase 1) → 8,500-9,000 words

---

## DELIVERABLES CHECKLIST

### Section A: Theory & Frameworks (~800 words)
**Status**: Needs writing  
**Location**: New section after Methodology

**Content Required**:

#### 3.1 Why Do Narratives Matter?
- Behavioral finance perspective (animal spirits, noise trading)
- Macroeconomic expectations channel (Phillips curve, consumption)
- Information aggregation argument
- Reference: Shiller (2017), Angeletos & La'O (2013), Baker & Wurgler (2006)

**Word target**: 200 words

#### 3.2 Sentiment vs. Noise: Unresolved Debates
- Tetlock (2007) vs. Da et al. (2015): return reversals evidence
- Fundamental information vs. behavioral overreaction
- Context-dependent distinction (crisis vs. normal times)
- Literature positions: Information channel vs. Noise trading channel

**Word target**: 200 words

#### 3.3 Causality Question: Do Narratives Drive Outcomes?
- Endogeneity concerns (reverse causality)
- Current evidence: mostly Granger causality, few IV/natural experiments
- Why causality matters: policy implications
- Gap: most studies show predictive power, not causal effect

**Word target**: 200 words

#### 3.4 Conceptual Framework
- How sentiment measures fit into forecasting models
- Channels: expectations, behavioral, policy communication
- Diagram/text: narrative → expectations → behavior → outcomes
- Role in broader economic models

**Word target**: 200 words

---

### Section B: Expanded Validation Section (~1,200 words, from 300)
**Status**: Needs major expansion  
**Location**: Expand existing "Validation and Robustness" section

**Current**: "42/50 studies use out-of-sample testing..." (too brief)

**New Content Required**:

#### 4.1 Out-of-Sample Validation Standards
- Rolling window approaches: expanding vs. sliding
- Real-time vs. pseudo-real-time data
- Hold-out periods and forward-looking tests
- Who uses what? (extract from Excel: "Validation Method")

**Word target**: 250 words

#### 4.2 Statistical Tests for Forecast Accuracy
- Diebold-Mariano test: standard adoption rate (~72%)
- Clark-West MSPE-adjusted test: nested models
- MCS/SPA tests: model confidence sets (~18% adoption)
- Granger causality as precursor to causality (~23% adoption)
- Which tests capture what trade-offs?

**Word target**: 250 words

#### 4.3 Performance Metrics and Their Limitations
- RMSE: universal but horizon-dependent
- MAE, MAPE: alternatives with trade-offs
- R² vs. R²_out-of-sample
- Classification metrics: accuracy, precision, recall, AUROC
- Economic metrics: Sharpe ratios, information ratios
- What metrics mask or reveal about true performance

**Word target**: 250 words

#### 4.4 Robustness Checks and Sensitivity Analysis
- Alternative specifications: different topics K, dictionaries
- Sub-sample analysis: pre/post crisis, different periods
- Cross-validation and parameter tuning
- Benchmark selection and its impact
- Gap: many studies skip robustness; best practices emerging

**Word target**: 250 words

#### 4.5 Best Practices vs. Actual Practice Gap
- What Q1 journals expect (comprehensive robustness)
- What literature actually does (often minimal)
- Emerging standards post-2020
- Recommendations for practitioners

**Word target**: 200 words

---

### Table 4: Literature Matrix (Appendix)
**Status**: Needs compilation  
**Deliverable**: Comprehensive table in appendix

**Format** (all 66 papers):
```
# | Authors | Year | Country | Domain | Data Source | Method | Target | Horizon | Result | Validation
1 | Tetlock | 2007 | USA | Finance | WSJ | Dictionary | Stock Returns | 1-6M | 30% RMSE ↓ | Diebold-Mariano
2 | Hájek & Olej | 2013 | CZE | Finance | SEC 10-K | SVM | Distress | - | 85% Accuracy | Cross-validation
...
66 | San Francisco Fed | 2025 | USA | Macro | Beige Book | LDA | Regional GDP | 1Q | 45% RMSE ↓ | Real-time
```

**Data extraction**:
- Columns: #, Citation, Year, Country, Domain, Data Source, NLP Method, Forecast Target, Horizon, Key Result, Validation
- Source: All columns from Excel "Detail Summery" sheet
- Format: Compact but complete (single table, sortable)

**Why**: Enables readers to:
- See full scope of 66 papers at a glance
- Sort by domain, method, country, year
- Cross-reference with text discussion
- Verify coverage claims

---

### Table 5: Risk-of-Bias Assessment
**Status**: Needs creation  
**Deliverable**: Quality scoring matrix

**Format**:
```
| Author/Year | Methodology | Data Quality | Validation | Sample Size | Quality Score | Comments |
|-------------|-------------|--------------|-----------|-------------|---------------|----------|
| Tetlock 2007 | High | High | High (DM+OOS) | Small | 8/10 | Limited to WSJ |
| Hong et al 2023 | High | High | High (OOS+MCS) | Large | 9/10 | Comprehensive |
| ... | ... | ... | ... | ... | ... | ... |
```

**Scoring criteria** (0-10 scale):
- Methodology (0-3): Dictionary=1, ML=2, BERT=2.5, LLM=3
- Data Quality (0-2): Small (<1K)=0.5, Medium=1, Large=1.5, Very Large=2
- Validation (0-2): OOS only=0.5, +Rolling=1, +DM test=1.5, +MCS/SPA=2
- Sample Size (0-2): <500 articles=0.5, 500-10K=1, 10K-1M=1.5, >1M=2
- Total: Sum of 0-10

**Purpose**: 
- Identify which studies are most rigorous
- Assess sensitivity to study quality
- Transparency on evidence grading

---

### Data Extraction Requirements

#### From Excel:
Extract and quantify:
1. **By Method Type** (from "NLP / Sentiment Method"):
   - Dictionary-based: count, list of studies
   - Traditional ML: count, list of studies
   - BERT/Transformers: count, list of studies
   - LLMs: count, list of studies

2. **By Validation Type** (from "Validation Method"):
   - Out-of-sample: count, %
   - Rolling windows: count, %
   - Diebold-Mariano: count, %
   - Real-time: count, %
   - Others: count, %

3. **By Quality Indicators**:
   - Dataset size (from "Key Findings")
   - Geographic scope (from "Country / Region")
   - Time period covered
   - Methodology sophistication

---

## Writing Structure for Phase 2

### Part A: Theory Section (800 words)
**Before: Methodological Evolution section**
**After: New Section 3.0 "Theoretical Foundations"**

```
3. Theoretical Foundations

3.1 Why Do Narratives Matter?
[200 words: behavioral + macro channels]

3.2 Sentiment vs. Noise
[200 words: fundamental vs. overreaction]

3.3 The Causality Question
[200 words: predictive power vs. causal effect]

3.4 Conceptual Framework
[200 words: channels linking sentiment to outcomes]
```

### Part B: Expanded Validation (1,200 words)
**Replace: Current "Validation and Robustness" section (300 words)**
**New: Section 5.0 "Validation Framework and Best Practices"**

```
5. Validation Framework and Best Practices

5.1 Out-of-Sample Standards
[250 words: rolling windows, real-time, hold-out]

5.2 Statistical Tests
[250 words: DM, MCS/SPA, Granger]

5.3 Performance Metrics
[250 words: RMSE, MAE, classification, economic metrics]

5.4 Robustness Checks
[250 words: alternatives, sub-samples, sensitivity]

5.5 Best Practices Consensus
[200 words: emerging standards, gaps in literature]
```

### Part C: Appendix Tables
**New Appendix A: Literature Matrix (66 papers)**
**New Appendix B: Risk-of-Bias Assessment**

---

## Word Count Target

| Section | Current | Phase 2 Add | New Total |
|---------|---------|------------|-----------|
| Theory | 0 | 800 | 800 |
| Validation | 300 | 900 | 1,200 |
| Other sections | 6,200 | 0 | 6,200 |
| **TOTAL** | **6,500** | **1,700** | **8,200** |

**Target**: 8,200-9,000 words (Q1-ready range)

---

## Implementation Sequence

**Week 2 (Phase 2):**

Day 1-2: Extract data from Excel
- Literature matrix data
- Risk-of-bias scores
- Validation method frequencies

Day 3-4: Write Theory section (~800 words)
- 3.1: Why narratives matter
- 3.2: Sentiment vs. noise debate
- 3.3: Causality question
- 3.4: Conceptual framework

Day 5-6: Expand Validation section (~1,200 words)
- 5.1: Out-of-sample standards
- 5.2: Statistical tests
- 5.3: Performance metrics
- 5.4: Robustness checks
- 5.5: Best practices

Day 7: Compile appendices
- Appendix A: Literature matrix (all 66 papers)
- Appendix B: Risk-of-bias assessment
- Format for LaTeX inclusion

---

## Key References for Theory Section

**Why Narratives Matter:**
- Shiller, R. J. (2017). Narrative economics. AER
- Angeletos, G.-M., & La'O, J. (2013). Sentiments. Econometrica
- Baker, S. R., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns

**Sentiment vs. Noise:**
- Tetlock, P. C. (2007). Giving content to investor sentiment
- Da, Z., Engelberg, J., & Gao, P. (2015). The sum of small things
- Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment

**Causality Issues:**
- Granger, C. W. J. (1969). Investigating causal relations by econometric models
- Angrist, J. D., & Pischke, J.-S. (2008). Mostly Harmless Econometrics

---

## Success Criteria

✅ Phase 2 Complete when:
- [ ] Theory section written (~800 words)
- [ ] Validation section expanded (~1,200 words)
- [ ] Literature matrix compiled (all 66 papers)
- [ ] Risk-of-bias assessment completed
- [ ] Appendices properly formatted for LaTeX
- [ ] Word count: 6,500 → 8,200-9,000
- [ ] Document recompiles without errors
- [ ] Cross-references between theory, methods, results verified

**Final Target**: 8,500-9,000 words (Q1-ready for JEL, JES, IJF)
