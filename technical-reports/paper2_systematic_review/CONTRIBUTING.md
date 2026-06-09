# Contributing to Paper 2 — Systematic Review & Replication Study

> **Title**: Economic Narrative Indices and Media-Based Sentiment Measures: A Systematic Review, Replication Study, and Bangla Extension (2007–2025)
>
> **Status**: ✅ Submitted to arXiv (June 2026)
>
> **Current phase**: Post-submission — open for replication validation, supplementary material expansion, and journal submission variants

---

## Open Contribution Areas

| Area | Effort | Skill needed | Status |
|------|--------|-------------|--------|
| **Replication validation** — re-run 8 replication scripts to verify results | 2–4 hrs | Python, ML basics | 🔄 Open |
| **Literature update** — screen 2025–2026 papers to extend the review | 4–8 hrs | Systematic review methods | 🔄 Open |
| **Journal formatting** — adapt manuscript for IJF/JEL/JES/JER submission formats | 2–3 hrs per venue | LaTeX | 🔄 Open |
| **Data extraction audit** — verify 66 extracted papers for consistency | 6–10 hrs | Attention to detail | 🔄 Open |
| **Supplementary materials** — build appendix tables, data dictionary | 3–5 hrs | LaTeX, R/Python | 🔄 Open |
| **Proofreading** — line-edit for clarity, grammar, consistency | 2–4 hrs | English, subject familiarity | 🔄 Open |

---

## Task Details

### Replication Validation

The replication suite is in `replications/`. It covers 8 papers across 4 methodological eras:

```bash
cd replications/
python3 run_all_phases.py   # Runs all 8 replications
```

**What to verify**:
- Do all scripts run without errors?
- Do the outputs match `results/` reference files?
- Are reproducibility instructions in the script headers accurate?
- Can a fresh environment reproduce the results?

**Log your results** in `technical-reports/contributions/OWNERS.csv` with `role=Replicator`.

### Data Extraction Audit

The main database is `data/papers_database.csv` (66 papers, 1979 lines). Each paper has:
- Bibliographic metadata
- Method classification (dictionary / ML / transformer)
- Validation approach
- Geographic/language focus
- Key findings

**What to verify**:
- Random sample 10–15 papers — re-extract from the original paper and compare
- Flag any inconsistencies in the `notes` column
- Update the coding if needed

**Log your audit** in `technical-reports/contributions/paper2_extraction_log.csv`.

### Literature Update (2025–2026)

The search covered papers through 2025. New relevant papers may have been published since.
- Search strategy: same as described in the manuscript's methodology section
- Target: 5–10 high-quality papers published 2025–2026
- Use the screening template in `technical-reports/contributions/paper2_screening_log.csv`

---

## Directory Map

```
paper2_systematic_review/
│
├── 📋 CONTRIBUTING.md            ← This file
│
├── 📋 arxiv_submission.tex       ← Primary manuscript (arXiv version)
├── 📋 beni_arxiv_final.tex       ← Development copy (from beni/)
│
├── 📁 drafts/                    ← Section-by-section LaTeX variants
│   ├── main.tex
│   ├── results_section.tex
│   ├── theory_section.tex
│   ├── validation_expanded_section.tex
│   ├── appendix_tables.tex
│   └── tables_figures_latex.tex
│
├── 📁 replications/              ← Replication suite (8 papers)
│   ├── run_all_phases.py
│   ├── era1_tetlock_2007.py
│   ├── era1_gentzkow_2019.py
│   ├── era2_ml_methods.py
│   ├── era3_transformers.py
│   ├── era4_validation_framework.py
│   └── results/
│
├── 📁 data/
│   ├── papers_database.csv       ← 66 papers with full coding
│   ├── literature_matrix_draft.csv
│   ├── results_data_raw.csv
│   └── refs.bib
│
├── 📁 planning/                  ← Submission guides, review docs
├── 📁 IJF_SUBMISSION/            ← Journal-specific variants
├── 📁 JEL_SUBMISSION/
├── 📁 JER_submission/
├── 📁 JES_submission/
│
└── 📋 README.md                  ← Paper overview & dependencies
```

---

## Recording Your Contribution

After completing any task, log it in `technical-reports/contributions/OWNERS.csv`:

```csv
name,role,paper,task,status,date_started,date_completed
Alice Smith,Replicator,paper2,"Validate era3_transformer replications",completed,2026-06-08,2026-06-10
```

For screening or extraction tasks, also update the respective log in `technical-reports/contributions/`.
