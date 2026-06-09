# BENI v1.0 Release Manifest

This manifest records the files currently moved into the BENI v1.0 data-paper workspace.

## Raw News Data

Path:

- `data/raw/potrika/`
- `data/raw/bnad/`

Contents:

- Potrika category-balanced files.
- Potrika newspaper/category files for economy, national, politics, and world news.
- BNAD JSONL files linked from the already-downloaded local `beni/Bangla_News_Database` folder.

Use these as the upstream source for the canonical BENI v1.0 article file.

Current BNAD link:

- `data/raw/bnad -> ../../../beni/Bangla_News_Database`

## Raw Macro Data

Path:

- `data/raw/macro/`

Files:

- `cpi_imf_bgd_index_monthly.csv`
- `fx_bdt_usd_bis_eop_monthly.csv`
- `fx_bdt_usd_imf_eop_monthly.csv`
- `reserves_wb_annual.csv`

## Annotation Artifacts

Path:

- `data/annotations/`

Files:

- `llm_assisted_300_annotations.jsonl`
- `llm_assisted_300_summary.json`
- `beni_v0_1_annotations_locked.jsonl`
- `beni_v0_1_review_queue.csv`
- `model_comparison.json`
- `active_learning_results.json`

## Index Artifacts

Path:

- `data/index/`

Files:

- `narrative_index.csv`
- `correlations.csv`
- `full_predictions.parquet`

These are prototype outputs. Regenerate final `BENI_v1.0` outputs before submission.

## Model Artifacts

Path:

- `data/models/`

Files:

- `economic_potrika-timeseries_tfidf_logreg.joblib`

## Manuscript Draft

Path:

- `paper/paper3_beni_pipeline/`

This is the existing BENI pipeline manuscript draft. It still needs to be renumbered/framed as the second active paper if desired, and its claims must be reconciled with the final BENI v1.0 release files.

## Compatibility Links

Symlinks were left in the old locations:

- `beni/experiment/data/raw/potrika`
- `beni/data/raw/macro`
- `beni/experiment/outputs/index/narrative_index.csv`
- `beni/experiment/outputs/index/correlations.csv`
- `beni/experiment/outputs/index/full_predictions.parquet`
- `beni/experiment/outputs/models/economic_potrika-timeseries_tfidf_logreg.joblib`
- `technical-reports/paper3_beni_pipeline`

These links are for backward compatibility only. New work should use paths inside `BENI_v1_data_paper`.
