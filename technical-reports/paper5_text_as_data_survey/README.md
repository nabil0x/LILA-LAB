# Paper 5: Text as Data in Social Science

This folder implements a prototype package for:

**Text as Data in Social Science: A Systematic Review of the Evolution of Language-Based Methods from Content Analysis to Large Language Models (1916-2026)**

The current implementation is a seed-review prototype, not the final systematic review. It uses a curated seed database of canonical papers to build the manuscript structure, taxonomy, figures, and analysis workflow. The final paper should expand the database through formal Web of Science, Scopus, JSTOR, SSRN, and arXiv searches.

## Implemented

- Seed literature database.
- Crossref candidate search with 301 unscreened records.
- Ranked screening queue for candidate inclusion/exclusion.
- Coding schema for the full review.
- Era/method/discipline/validation summary script.
- Timeline, method adoption, validation, language-gap, and LLM capability figures.
- LaTeX-ready tables.
- Manuscript draft.
- Makefile for reproducibility.

## Reproduce

```bash
make assets
make pdf
```

## Main Files

- `data/seed_literature_database.csv`
- `data/crossref_candidate_papers.csv`
- `data/crossref_screening_queue.csv`
- `data/search_log.md`
- `data/coding_schema.md`
- `scripts/build_review_assets.py`
- `scripts/search_crossref_candidates.py`
- `scripts/screen_crossref_candidates.py`
- `manuscript/paper5_text_as_data_survey.tex`
- `results/tables/`
- `results/figures/`

## Expansion Required Before Submission

- Screen `data/crossref_screening_queue.csv`, starting with `screen_first`.
- Run formal database searches in Web of Science, Scopus, JSTOR, SSRN, and arXiv when access is available.
- Expand from 28 seed papers to 200-400 screened papers.
- Add PRISMA flow diagram.
- Add DOI/URL, citation counts, and exclusion reasons.
- Add cross-disciplinary citation network analysis.
- Add geographic mapping from coded country fields.
- Freeze a literature cutoff date for the LLM section.
