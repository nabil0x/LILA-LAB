# Paper 3 — BENI Pipeline Manuscript (LaTeX Source)

> **Title**: Building Local-Language Economic Narrative Indices: A Replicable Pipeline from Raw News to Validated Index
>
> **Status**: 🔄 Finishing sprint — manuscript drafted, BENI v1 frozen
>
> **Timeline**: July 2026 submission

This directory contains the canonical LaTeX source for the Paper 3 manuscript.

---

## Contents

| File | Purpose |
|------|---------|
| `main.tex` | Main manuscript LaTeX |
| `references.bib` | Bibliography |
| `main.pdf` | Compiled manuscript |
| `PLAN.md` | Detailed paper plan |
| `main.{aux,bbl,blg,log,out}` | LaTeX build artifacts |
| `drafts/` | Earlier manuscript drafts |

---

## Symlink Access Points

This directory is reachable through two symlinks:

| Symlink | Resolves To |
|---------|-------------|
| `technical-reports/paper3_beni_pipeline` | `technical-reports/paper3_beni_method/manuscript/paper3_beni_pipeline/` |
| `data-paper/paper/paper3_beni_pipeline` | `technical-reports/paper3_beni_method/manuscript/paper3_beni_pipeline/` (via `../../`) |

Both point to the same canonical location.

---

## Dependencies

- **Data**: The manuscript uses `technical-reports/paper3_beni_method/data/` which includes symlinks to `data-paper/data/` for canonical files
- **BENI index**: Built from `beni/index/build_narrative_index.py`
- **Annotations**: From `beni/annotation/` pipeline
- **Macro data**: From `beni/data/raw/macro/`
