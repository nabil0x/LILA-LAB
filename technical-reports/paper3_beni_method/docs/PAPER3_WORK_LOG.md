# Paper 3 Work Log

## 2026-06-08

### Completed

- Created `FOCUS_ROADMAP.md` to define Paper 3 as the BENI method and measurement-foundation paper.
- Added `scripts/freeze_paper3_inputs.py`.
- Detected that the earlier BENI v1 compressed processed files were truncated:
  - `beni_unified_articles.csv.zst`
  - `beni_unified_articles_deduped.csv.zst`
  - `bnad_articles_canonical.csv.zst`
- Regenerated BENI v1 processed article files from raw Potrika and BNAD sources using `BENI_v1_data_paper/scripts/build_beni_v1_articles.py`.
- Verified all four regenerated compressed files with `zstd -t`.
- Reran the Paper 3 input-freeze report after repair.
- Created `data/annotations/beni_v1_reference_labels_candidate.jsonl`.
- Created `data/annotations/beni_v1_label_review_decisions.csv`.
- Added `scripts/prepare_label_review_sheet.py`.
- Added `scripts/apply_label_review_decisions.py`.
- Created a draft frozen-label file and summary that explicitly report unresolved review rows.
- Applied the review-decision sheet so the 114 ambiguous rows are now conservatively excluded from clean validation.
- Added `scripts/map_reference_labels_to_beni_v1.py`.
- Created `data/annotations/beni_v1_reference_label_corpus_map.csv`.
- Mapped all 300 original annotation IDs to canonical BENI v1 article IDs with zero unmatched rows.
- Updated candidate and frozen reference-label outputs to carry both original annotation IDs and canonical BENI v1 IDs.
- Added `scripts/build_beni_v1_article_predictions.py`.
- Added `scripts/build_beni_v1_monthly_index.py`.
- Rebuilt `data/index/beni_v1_article_predictions.parquet` from the repaired corpus and the TF-IDF/logistic model artifact.
- Built `data/index/beni_v1_monthly_index.csv` plus article-weighted and source-balanced variants from the repaired predictions.

### Current Corpus Status

The repaired BENI v1 deduped article file streams cleanly:

- rows: 1,467,705
- unique article IDs: 1,467,705
- missing article IDs: 0
- duplicate article IDs: 0
- missing publication dates: 0
- missing clean text: 0
- zstd stream status: clean

Use:

- `data/processed/beni_unified_articles_deduped.csv.zst`

### Current Label Status

The reference labels are not final yet.

- candidate labels: 300
- Economic: 120
- Not Economic: 180
- rows requiring review: 0
- clean high-confidence rows before review: 186
- conservative exclusions: 114
- canonical BENI v1 IDs mapped: 300/300

### Current Prediction Status

- prediction builder exists: yes
- output file complete: `data/index/beni_v1_article_predictions.parquet`
- output status: frozen
- monthly index output complete: `data/index/beni_v1_monthly_index.csv`
- next step: refresh manuscript tables from the frozen BENI v1 comparison and monthly outputs

Important comparison note:

- candidate label file has 120/300 Economic labels.
- frozen BENI v1 comparison uses the 186-row clean validation set.
- legacy `model_comparison.json` remains as prototype/calibration evidence.

### Next Task

Refresh manuscript tables from the frozen BENI v1 comparison and monthly outputs.
