# Contributing to Paper 5 — Text as Data in Social Science (1916–2026)

> **Title**: Text as Data in Social Science: A Systematic Review of the Evolution of Language-Based Methods from Content Analysis to Large Language Models (1916–2026)
>
> **Status**: 🔄 Active expansion — Seed prototype complete, 301 Crossref candidates awaiting screening
>
> **Timeline**: October–December 2026

---

## Open Contribution Areas

| Area | Effort | Skill needed | Priority |
|------|--------|-------------|----------|
| **Screening** — Screen 301 Crossref candidates (title + abstract) | 4–6 hrs | Systematic review methods | 🔴 High |
| **Data extraction** — Code 200–400 papers from included set | 20–40 hrs | Attention to detail, subject familiarity | 🔴 High |
| **Database search** — Run WoS, Scopus, JSTOR, arXiv, SSRN queries | 2–4 hrs per source | Literature search skills | 🟡 Medium |
| **Citation network** — Build cross-disciplinary citation graph | 3–5 hrs | Python (networkx) | 🟡 Medium |
| **Geographic mapping** — Build world heatmap of text-as-data research | 2–3 hrs | Python (plotly/geopandas) | 🟢 Low |
| **Figure regeneration** — Replace seed figures with full-review versions | 3–5 hrs | Python (matplotlib/seaborn), LaTeX | 🟡 Medium |
| **Proofreading** — Line-edit 10-page manuscript | 2–4 hrs | English, subject familiarity | 🟢 Low |

---

## Screening Workflow

The screening queue is at `data/crossref_screening_queue.csv` (306 rows).

### Inclusion criteria
- Must analyze text data empirically (not just propose methods)
- Must be a social science discipline: economics, political science, sociology, communication, psychology, computational social science
- Time period: 1916–2026
- Language: Any (we code language as metadata)

### Exclusion criteria
- Pure CS/NLP benchmarks without social science application
- Method papers with no empirical demonstration
- Non-English papers without English abstract

### How to screen

1. Open `data/crossref_screening_queue.csv`
2. For each row, set `screening_status` from `candidate` to `screened`
3. Set `include_decision` to `include` or `exclude`
4. If excluding, fill `exclusion_reason`
5. Add optional notes in the `notes` column

**Recommended batch size**: 30–50 papers per session.

### Logging your screening

After each batch, update `technical-reports/contributions/paper5_screening_log.csv`:

```csv
contributor,date,batch_start,batch_end,n_screened,n_included,n_excluded,notes
Your Name,2026-10-15,1,50,50,8,42,Started with economics section
```

---

## Data Extraction Workflow

The coding schema is at `data/coding_schema.md`. Fields to extract per paper:

| Field | Values |
|-------|--------|
| discipline | economics / political_science / sociology / communication / psychology / computational_social_science |
| era | content_analysis / quant_content / computer_assisted / dictionary / topic_model / transformer / llm |
| method_family | manual / dictionary / supervised_ml / unsupervised_ml / embedding / llm |
| task | description / measurement / prediction / causal_inference / discovery |
| language | Language name |
| geographic_focus | Country or region |
| validation_type | manual_coding / gold_standard / interrater / external_validation / none |

---

## Directory Map

```
paper5_text_as_data_survey/
│
├── 📋 CONTRIBUTING.md              ← This file
│
├── 📁 data/
│   ├── seed_literature_database.csv      ← 28 curated canonical papers (seed)
│   ├── crossref_candidate_papers.csv     ← 301 unscreened candidates
│   ├── crossref_screening_queue.csv      ← Screening queue (add your decisions here)
│   ├── coding_schema.md                  ← Full extraction schema
│   └── search_log.md                     ← Search protocol documentation
│
├── 📁 literature/
│   ├── pdfs/                        ← Downloaded PDFs
│   ├── download_manifest.csv        ← PDF download tracking
│   └── local_pdf_inventory.csv      ← Local PDF inventory
│
├── 📁 scripts/                      ← Build, screen, extraction scripts
├── 📁 manuscript/                   ← LaTeX manuscript
├── 📁 results/                      ← Figures and tables
│
└── 📋 README.md                     ← Paper overview & dependencies
```
