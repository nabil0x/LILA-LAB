# BENI — Core Codebase & Data Infrastructure

> 39 GB workspace containing the annotation pipeline, index construction, experiments, news corpus, and macroeconomic data that underpin Papers 2–4 of the research program.

---

## Directory Structure

```
beni/
│
├── 📁 annotation/                ← LLM-assisted economic relevance annotation pipeline
│   ├── 📋 ANNOTATION_SCHEMA.md      12-field schema (topic, sentiment, frame, etc.)
│   ├── 📋 ANNOTATOR_GUIDE.md        Human annotator instructions
│   ├── 📋 ADJUDICATION_PROTOCOL.md  How to resolve annotation disagreements
│   ├── 🐍 llm_annotate.py           Core LLM annotation (Claude, GPT)
│   ├── 🐍 annotate_batch.py         Batch processing for large-scale annotation
│   ├── 🐍 multi_llm_ensemble.py     Multi-LLM ensemble voting
│   ├── 🐍 kaggle_3llm_ensemble.py   Kaggle-specific 3-LLM ensemble runner
│   ├── 🐍 analyze_llm_annotations.py  Annotation quality & cost analysis
│   ├── 🐍 ensemble_report.py        Ensemble consistency reports
│   ├── 🐍 build_annotation_batch.py  Construct annotation batches from corpus
│   ├── 🐍 export_for_labelstudio.py  Export to Label Studio format
│   ├── 🐍 create_llm_assisted_300.py Build 300-article LLM reference set
│   ├── 🐍 run_active_learning.py     Active learning loop
│   ├── 🐍 run_model_comparison.py    Compare classifier models
│   ├── 🐍 finetune_banglabert_for_prelabel.py  Fine-tune BanglaBERT
│   ├── 🐍 add_ml_predictions.py      Add model predictions to annotation set
│   ├── 🐍 adjudicate.py             Adjudication script
│   ├── 🐍 setup_project.py          Project setup
│   ├── 📋 label_config.xml          Label Studio config
│   ├── 📁 exports/                  Labeled data exports
│   ├── 📁 projects/                 Label Studio project files
│   ├── 📁 logs/                     Annotation run logs
│   └── 📁 __pycache__/
│
├── 📁 Bangla_News_Database/      ← Raw news corpus (Potrika + BNAD)
│   ├── 📋 *.jsonl                    Per-newspaper article files
│   ├── 📋 category.txt               Category taxonomy
│   └── 📋 source_code.zip            BNAD source code
│
├── 📁 data/                      ← Processed data artifacts
│
├── 📁 database/                  ← Database files (SQLite, etc.)
│
├── 📁 experiment/                ← Full experiment suite
│   ├── 📋 EXPERIMENT_REPORT.md       Consolidated experiment findings
│   ├── 📋 FINDINGS_ECONOMIC_TRENDS.md Economic trend analysis from narratives
│   ├── 📋 MODEL_COMPARISON.md        Model comparison results
│   ├── 📋 DATA_SOURCES.md            Data provenance
│   ├── 📋 BENI_NOVELTY_AGENDA.md     Novelty assessment
│   ├── 📋 NIETZSCHE_LANGUAGE_FRAMEWORK_FOR_BENI.md  Theoretical framing
│   ├── 📁 beni_pilot/                BENI pilot experiments
│   ├── 📁 bnlp-resources/            Bangla NLP resources
│   ├── 📁 data/                      Experiment-specific data splits
│   ├── 📁 models/                    Trained model artifacts (TF-IDF, logistic reg)
│   ├── 📁 scripts/                   Experiment scripts
│   └── 📁 outputs/                   Experiment outputs (predictions, indices)
│       ├── 📁 index/                  BENI narrative index CSV outputs
│       └── (other experiment outputs)
│
├── 📁 index/                     ← BENI index construction
│   ├── 🐍 build_narrative_index.py   Main index builder (article predictions → monthly index)
│   ├── 🐍 visualize.py               Index visualization
│   └── 📁 outputs/                   Generated index files
│
├── 📁 figures/                   ← Paper figures
│   ├── 📋 beni_timeseries.pdf
│   └── 📋 funnel_plot_publication_bias.pdf
│
├── 📋 beni_arxiv_final.tex       ← Paper 2 manuscript (development copy)
│                                     Canonical copy → papers/paper2_systematic_review/
├── 📋 references.bib             ← Bibliography for Paper 2 manuscript
├── 📋 beni_arxiv_final.pdf       ← Compiled Paper 2
├── 📋 beni_arxiv_final.{aux,bbl,blg,log,out}  ← LaTeX build artifacts
│
├── 📋 BENI_ROADMAP.md            ← BENI project roadmap
├── 📋 PROJECT_STATUS.md          ← Current project status
└── 📋 ensemble_results.tar.gz    ← Archived ensemble results
```

---

## Dependency Map — How beni/ Feeds Into Each Paper

```
beni/annotation/ ──LLM labels──▶  paper3_beni_method/ (trains classifier)
beni/index/      ──BENI index──▶  paper4_beni_nowcasting/ (nowcast input)
beni/figures/    ──figures─────▶  paper2_systematic_review/ (copied)
beni/data/       ──macro data──▶  paper3_beni_method/, paper4_beni_nowcasting/
beni/experiment/ ──results─────▶  paper3_beni_method/ (method validation)
beni/Bangla_News_Database/      ▶  data-paper/ (upstream corpus)
beni/beni_arxiv_final.tex       ▶  papers/paper2_systematic_review/ (copy)
```

---

## Key Pipelines

### 1. Annotation Pipeline (`annotation/`)
```
Raw news articles
    → LLM annotate (llm_annotate.py)
    → Multi-LLM ensemble (multi_llm_ensemble.py)
    → Active learning (run_active_learning.py)
    → Model training (run_model_comparison.py)
    → Adjudication (adjudicate.py)
    → Locked reference set
```

### 2. Index Construction (`index/`)
```
Article-level predictions (from annotation pipeline or experiment/outputs/)
    → build_narrative_index.py
    → Monthly BENI index CSV
    → Macro validation against CPI, FX, reserves
```

### 3. Experiment Suite (`experiment/`)
Codes in `experiment/scripts/` run model comparisons, produce outputs in `experiment/outputs/`, and generate findings documented in `EXPERIMENT_REPORT.md`, `MODEL_COMPARISON.md`, etc.

---

## Notes for Research Agents

- **This is the upstream dependency** for Papers 2, 3, and 4. Changes to `beni/annotation/` or `beni/index/` propagate to those paper directories.
- `beni/experiment/outputs/` contains the raw prediction files that `paper3_beni_method/` references.
- `data-paper/` was built by extracting canonical data from `beni/data/` and `beni/index/outputs/`.
- The `beni_arxiv_final.tex` in this dir is the **development copy** of Paper 2 — the canonical copy lives in `papers/paper2_systematic_review/`.
