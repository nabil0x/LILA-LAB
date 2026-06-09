# Paper 3 — BENI Method / Pipeline Paper

> **Title**: Building Local-Language Economic Narrative Indices: A Replicable Pipeline from Raw News to Validated Index
>
> **Status**: 🔄 Finishing sprint — manuscript drafted, BENI v1 frozen
>
> **Timeline**: July 2026 submission

---

## Directory Layout

```
paper3_beni_method/
│
├── 📁 manuscript/paper3_beni_pipeline/   ← LaTeX source, references, compiled draft, paper plan
│                                           (canonical manuscript — also accessible via
│                                            technical-reports/paper3_beni_pipeline symlink)
│
├── 📁 data/
│   ├── 📁 annotations/   ← LLM-assisted labels, locked labels, review queue,
│   │                         model comparison, active-learning results
│   ├── 📁 processed/     ← symlink → data-paper/data/processed/ (canonical BENI v1 DB)
│   ├── 📁 index/         ← older monthly BENI prototype index, predictions, macro correlations
│   ├── 📁 models/        ← TF-IDF/logistic-regression model artifact
│   └── 📁 raw/macro/     ← CPI, FX, reserves source files
│
├── 📁 scripts/           ← Method-specific scripts from annotation/index workflow
├── 📁 docs/              ← Readiness & next-action notes
├── 📋 FOCUS_ROADMAP.md   ← Current focus roadmap
└── 📋 README.md          ← This file
```

---

## Database Decision

This paper should use the **BENI v1 database** as its main empirical base:

| Item | Location |
|------|----------|
| Release | `BENI_unified_v1.0_preliminary` |
| Canonical data | `data-paper/data/processed/` |
| Main article file | `data/processed/beni_unified_articles_deduped.csv.zst` |
| Source components | Potrika (2014–2020) + BNAD (post-2020) |

The older `data/index/` outputs are prototype artifacts. The manuscript should be regenerated from BENI v1 before submission.

---

## Symlinks & Cross-References

| Path | Points To |
|------|-----------|
| `technical-reports/paper3_beni_pipeline` | `technical-reports/paper3_beni_method/manuscript/paper3_beni_pipeline/` |
| `data-paper/paper/paper3_beni_pipeline` | Same canonical manuscript target (via `../../`) |
| `data-paper/data/annotations` | (if symlink exists) |
| `data-paper/data/index` | (if symlink exists) |
| `data-paper/data/models` | (if symlink exists) |
| `data-paper/data/raw/macro` | (if symlink exists) |

---

## Derivative Map

| Content | Source |
|---------|--------|
| `data/processed/` (symlink) | `data-paper/data/processed/` |
| `data/annotations/` | Originally from `beni/annotation/` pipeline outputs |
| `data/index/` | Originally built by `beni/index/build_narrative_index.py` |
| `data/models/` | Trained from `beni/experiment/` |
| `manuscript/` | Independent LaTeX source (references `data/` for numbers) |

---

## Remaining Alignment Work

Before submission:

1. Standardize the authoritative LLM label set
2. Regenerate predictions, index files, and paper tables from BENI v1
3. Align manuscript numbers with the final data files
4. Fix LaTeX/PDF build warnings
