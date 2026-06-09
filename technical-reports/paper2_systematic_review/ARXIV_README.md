# ArXiv Submission: Economic Narrative Indices and Media-Based Sentiment Measures

**Title**: Economic Narrative Indices and Media-Based Sentiment Measures: A Systematic Review, Replication Study, and Bangla Extension (2007-2025)

**Authors**: Ann Naser Nabil (Jahangirnagar University)

**Status**: Ready for submission to [arXiv](https://arxiv.org)

---

## Paper Summary

This paper presents three integrated contributions:

1. **Systematic Review**: 66 papers (2007-2025) on sentiment-based economic forecasting, documenting methodological evolution, geographic gaps, and validation practices.

2. **Replication Study**: 8 representative papers across dictionary, ML, transformer, and validation methods. Median 3.76% RMSE improvement; publication bias correction suggests true effect is 10-15% vs. reported 20%.

3. **BENI Pilot**: First Bangla economic sentiment index (265M speakers), with novel time-series domain dynamics model tracking macroeconomic narrative regimes.

---

## Files Included

### Main Submission
- `arxiv_submission.tex` — Full paper (323 lines, ≈8000 words)
- `PROJECT_STATUS.md` — Project overview and deliverables
- `replications/COMPREHENSIVE_RESULTS_SUMMARY.md` — Detailed replication results

### Code (Reproducible)
All replication code available in `replications/` directory:
- `framework.py` — Shared evaluation metrics and utilities
- `era1_tetlock_2007.py`, `era1_gentzkow_2019.py` — Dictionary methods
- `era2_ml_methods.py` — SVM, Random Forest, XGBoost
- `era3_transformers.py` — LSTM, BERT, RoBERTa
- `era4_validation_framework.py` — Validation standards
- `run_all_phases.py` — Execute all replications

### Supplementary Materials
- `REPLICATION_PLAN_15_20_PAPERS.md` — Full methodology for replicating 15-20 papers
- `NOVELTY_ASSESSMENT.md` — BENI novelty positioning vs. literature
- `MODEL_COMPARISON.md` — Time-series model recommendations
- `beni_pilot/paper.tex` — BENI pilot technical paper
- `beni_pilot/time_series_economic_model.py` — Novel domain dynamics model

### Results Data
- `replications/results/all_phases_unified_results.csv` — Unified metrics table
- `replications/results/meta_analysis_synthesis.json` — Meta-analysis findings
- `replications/results/reproducibility_checklist.json` — 25-item validation checklist

---

## Key Results

### Systematic Review (66 papers)
- **Methodological distribution**: Dictionary 55%, ML 6%, Transformers 6%, Theory 30%
- **Geographic bias**: 56% US-focused, 84% English, **0% Bangla**
- **Median RMSE improvement**: 20% (pooled), but **10-15% after bias correction**
- **Validation gaps**: Only 18% use real-time protocols, 13% release code

### Replication Study (8 papers)
| Method | Papers | Median RMSE Impr. | Median Accuracy |
|--------|--------|------------------|-----------------|
| Dictionary | 2 | 0.42% | 83.73% |
| ML | 3 | 0.00% | 100.00% |
| Transformers | 3 | 30.50% | 69.83% |
| **Pooled** | **8** | **3.76%** | **84.62%** |

### BENI Pilot (Bengali NLP)
- **Topic classification**: 89% accuracy (6 news categories)
- **Economic relevance**: 95% accuracy, 45% precision, 63% recall
- **Domain coupling**: Monetary-Inflation 0.80, Trade-Growth 0.40
- **Novel**: Time-series domain similarity tracking narrative regimes

---

## How to Run Replications

```bash
# Clone or download repository
cd replications/

# Run all phases (4 methodological eras)
python3 run_all_phases.py

# Or run individual phases
python3 run_phase1.py        # Dictionary methods
python3 era2_ml_methods.py   # Traditional ML
python3 era3_transformers.py # Deep learning
```

Expected output: 8 replication results with seed-controlled reproducibility.

---

## Citation

```bibtex
@article{Nabil2026,
  title={Economic Narrative Indices and Media-Based Sentiment Measures: 
         A Systematic Review, Replication Study, and Bangla Extension (2007-2025)},
  author={Nabil, Ann Naser},
  year={2026},
  journal={arXiv preprint}
}
```

---

## Submission Details

- **Venue**: arXiv (Quantitative Finance, Computational Linguistics, or Economics)
- **Word Count**: ~8000 (including abstract, tables, references)
- **Sections**: Introduction, Related Work, Methods, Results (Review + Replication + BENI), Discussion, Conclusion
- **Figures**: 3 (timeline, performance distribution, geographic coverage)
- **Tables**: 8 (methodological distribution, results by domain, replication summary, BENI metrics, domain coupling)
- **Reproducibility**: Full code + results data + reproducibility checklist provided

---

## Key Contributions Highlighted

1. **First quantitative meta-analysis** of sentiment-based forecasting with publication bias correction
2. **Comprehensive replication suite** across dictionary, ML, and transformer methods (all code released)
3. **Geographic and linguistic gap identification** (0% Bangla coverage identified)
4. **BENI**: First Bangla economic sentiment index + novel time-series domain dynamics model
5. **Reproducibility framework**: 25-item checklist + open-source toolkit for building native-language indices

---

## Reviewer Guidance

**Strengths**:
- Addresses documented gap (no sentiment indices for Bangla/South Asia)
- Comprehensive literature review (66 papers) + systematic replication
- Novel time-series model (domain coupling, regime detection)
- Full reproducibility (code, data, seeds, hyperparameters documented)

**Limitations** (acknowledged in paper):
- Synthetic data for replications (real data would strengthen validation)
- BENI pilot uses weak labels (keyword-based); manual annotation planned for Phase 2
- Small replication sample (8 papers); 15-20 target for full project
- Publication bias correction is conservative; true effect may differ

**Scope**: Bridges NLP/ML, economics, and development economics literature.

---

## Files to Review

**Start with**:
1. `arxiv_submission.tex` — Main paper
2. `PROJECT_STATUS.md` — Project overview
3. `replications/COMPREHENSIVE_RESULTS_SUMMARY.md` — Detailed results

**For reproducibility**:
- `replications/run_all_phases.py` — Master script (run to verify all results)
- `replications/results/all_phases_unified_results.csv` — Summary metrics

**For BENI details**:
- `beni_pilot/paper.tex` — BENI technical details
- `beni_pilot/time_series_economic_model.py` — Domain dynamics model

---

## Contact

Ann Naser Nabil  
Department of Economics  
Jahangirnagar University  
Savar, Dhaka-1342, Bangladesh  
Email: lila.lab0x@gmail.com  
ORCID: 0009-0006-3561-045X

---

**Submission Date**: 2026-06-06  
**Repository**: [GitHub] (to be anonymized for blind review)  
**Data Availability**: BanglaNLP data is publicly available; replication datasets are synthetic (reproducible from code)
