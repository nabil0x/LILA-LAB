# Paper 2 — Systematic Review & Replication Study

> **Title**: Economic Narrative Indices and Media-Based Sentiment Measures: A Systematic Review, Replication Study, and Bangla Extension (2007–2025)
>
> **Status**: ✅ Submitted to arXiv (June 2026)
>
> **Role in program**: Establishes the gap — 84% English, 0% Bangla, 66 papers reviewed, 8 replications.

---

## Directory Contents

```
paper2_systematic_review/
│
│── 📋 1.md                              ← Brief paper overview / scratch notes
│
│── 📋 arxiv_submission.tex              ← arXiv submission LaTeX
│── 📋 arXiv_submission.zip              ← arXiv submission bundle
│── 📋 ARXIV_README.md                   ← arXiv submission instructions
│── 📋 ARXIV_SUBMISSION_CHECKLIST.md     ← arXiv submission checklist
│── 📋 arxiv_submission.log              ← arXiv build log
│── 📁 arXiv_submission/                 ← arXiv submission package files
│
│── 📋 beni_arxiv_final.tex              ← Canonical Paper 2 manuscript (copy from beni/)
│── 📋 beni_arxiv_final.pdf              ← Compiled manuscript PDF
│── 📋 references.bib                    ← Bibliography
│── 📋 beni_timeseries.pdf               ← Figure: BENI time series (copy from beni/figures/)
│── 📋 funnel_plot_publication_bias.pdf  ← Figure: Publication bias funnel plot
│
│── 📁 data/                             ← Review data
│── 📁 drafts/                           ← Earlier drafts
│── 📁 planning/                         ← Review planning docs
│
│── 📁 replications/                     ← Replication suite (8 papers)
│── 📋 REPLICATION_PLAN_15_20_PAPERS.md  ← Replication plan
│
│── 📁 IJF_SUBMISSION/                   ← International Journal of Forecasting submission
│── 📁 JEL_SUBMISSION/                   ← Journal of Economic Literature submission
│── 📁 JER_submission/                   ← Journal of Economic Reviews submission
│── 📁 JES_submission/                   ← Journal of Economic Surveys submission
│── 📁 JES_submission_archive.zip        ← JES submission archive
│
│── 📋 NOVELTY_ASSESSMENT.md             ← Novelty assessment for the paper
│
└── (various symlinks to technical-reports/ and beni/ for backward compatibility)
```

---

## Derivative Map

| Content | Source | Notes |
|---------|--------|-------|
| `beni_arxiv_final.tex` | Copied from `beni/beni_arxiv_final.tex` | This is the canonical copy for the paper directory |
| `beni_arxiv_final.pdf` | Copied from `beni/` | — |
| `references.bib` | Copied from `beni/references.bib` | — |
| `beni_timeseries.pdf` | Copied from `beni/figures/` | Figure from BENI development |
| `funnel_plot_publication_bias.pdf` | Copied from `beni/figures/` | Figure from BENI development |
| `arxiv_submission.tex` | Standalone arXiv build | Separate from the development manuscript |
| Journal submission dirs | Derived from the core manuscript | Each has its own formatting |

---

## Relationship to Other Papers

- **Upstream dependency**: `beni/` — the manuscript was developed inside `beni/` alongside the codebase
- **Sibling paper**: `paper3_beni_method/` — Paper 2 includes a BENI pilot (Section 4) as proof of concept
- **Feeds into**: `paper5_text_as_data_survey/` — Paper 2's systematic review is subsumed into Paper 5 as one discipline section (economics, 2007–2025)
- **Standalone**: Paper 2 does not depend on any other paper

---

## For Research Agents

- The canonical manuscript is `beni_arxiv_final.tex`. The `arxiv_submission.tex` is a build variant.
- The `replications/` directory contains the independent replication code for 8 papers from the systematic review.
- Journal submission directories (IJF, JEL, JER, JES) contain submission-specific formatting and cover letters.
- The `beni_arxiv_final.tex` was originally developed inside `beni/` alongside the annotation pipeline and index construction. It was copied here so the paper is self-contained.
