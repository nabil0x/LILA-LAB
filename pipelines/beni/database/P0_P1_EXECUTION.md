# BENI Index + Database P0/P1 Execution

## P0 status

Current dataset version: `BENI_v0.1`

Completed:

- Locked the 300-record annotation set.
- Created a human review queue for uncertain/borderline labels.
- Created SQLite schema with `articles`, `annotations`, `sources`, `model_predictions`, `index_values`, and `macro_indicators`.
- Imported locked annotations into SQLite.
- Trained and evaluated the first supervised economic relevance filter.
- Imported a 20,000-article corpus slice for pipeline verification.
- Stored model predictions for the imported corpus slice.
- Built a monthly BENI prototype index.
- Imported macro indicators and generated level/first-difference correlations.

Still required before claiming a full P0 research prototype:

- Complete human review of `beni/annotation/exports/beni_v0_1_review_queue.csv`.
- Re-import corrected `human_verified` labels.
- Run `import-corpus` without `--max-articles` for the full corpus.
- Re-run prediction, index construction, and validation on the full corpus.

## P0 commands

```bash
python3 beni/database/beni_p0_pipeline.py freeze-annotations
python3 beni/database/beni_p0_pipeline.py init-db
python3 beni/database/beni_p0_pipeline.py import-annotations
python3 beni/database/beni_p0_pipeline.py train-filter
python3 beni/database/beni_p0_pipeline.py import-corpus --max-articles 20000
python3 beni/database/beni_p0_pipeline.py predict-corpus --model-path beni/database/outputs/beni_v0_1_tfidf_logreg_20260607.joblib
python3 beni/database/beni_p0_pipeline.py import-macro
python3 beni/database/beni_p0_pipeline.py build-index --model-version beni_v0_1_tfidf_logreg_20260607
python3 beni/database/beni_p0_pipeline.py validate-index
```

For the full corpus, remove the import cap:

```bash
python3 beni/database/beni_p0_pipeline.py import-corpus
```

## Current outputs

- `beni/annotation/exports/beni_v0_1_annotations_locked.jsonl`
- `beni/annotation/exports/beni_v0_1_review_queue.csv`
- `beni/database/beni_v0_1.sqlite`
- `beni/database/outputs/beni_v0_1_filter_metrics.json`
- `beni/database/outputs/beni_v0_1_tfidf_logreg_20260607.joblib`
- `beni/database/outputs/BENI_v0_1_monthly_monthly_index.csv`
- `beni/database/outputs/BENI_v0_1_monthly_macro_correlations.csv`

## P1 backlog

- Expand labels from 300 to 1,000 with uncertainty sampling.
- Add topic labels: inflation, exchange rate, reserves, banking, fiscal policy, trade, employment, growth/investment.
- Add narrative force labels: crisis, burden, blame, reform, stability, uncertainty, resilience, neutral.
- Improve date parsing beyond the current Bangla date parser.
- Add stronger duplicate clustering beyond text hash identity.
- Compare raw article-weighted and source-balanced BENI variants.
- Add rolling out-of-sample validation and AR benchmark comparisons.
- Write dataset card, model card, annotation guideline, and index construction memo.
