# Paper 3 Current Status and Todo

Updated: 2026-06-08

## Current Status

Paper 3 is now in the **frozen-input and comparison stage**.

The corpus problem has been fixed. The earlier BENI v1 processed `.zst` files were truncated and failed decompression checks. They have now been regenerated from raw Potrika and BNAD sources and verified.

Use this as the canonical working article file:

- `data/processed/beni_unified_articles_deduped.csv.zst`

Current corpus QA:

- rows: 1,467,705
- unique article IDs: 1,467,705
- missing article IDs: 0
- duplicate article IDs: 0
- missing publication dates: 0
- missing clean text: 0
- compression integrity: passed
- streaming QA: passed

Current label QA:

- candidate reference labels: 300
- Economic: 120
- Not Economic: 180
- canonical BENI v1 article-ID mappings: 300/300
- unresolved review rows: 0
- clean high-confidence rows before review: 186
- conservative exclusions: 114

Important methodological note:

- The frozen BENI v1 comparison file uses the 186-row clean validation set and the repaired article-level predictions.
- The legacy `model_comparison.json` remains in the folder as prototype/calibration evidence.

## Completed

- [x] Regenerate BENI v1 processed article files from raw Potrika and BNAD.
- [x] Verify regenerated `.zst` files with `zstd -t`.
- [x] Stream QA the deduped BENI v1 article file.
- [x] Create candidate reference-label file.
- [x] Create label-review decision sheet.
- [x] Map all 300 annotation rows to canonical BENI v1 article IDs.
- [x] Create Paper 3 input-freeze report.
- [x] Create Paper 3 work log.
- [x] Add scripts for input freeze, label-review preparation, label-decision application, and annotation-to-corpus ID mapping.

## Priority 1: Freeze Labels

File to use:

- `data/annotations/beni_v1_label_review_decisions.csv`

Current state:

- all 114 review rows have been resolved conservatively as exclusions from clean validation
- frozen reference labels can now be regenerated from the current decision sheet

Run:

```bash
python3 paper3_beni_method/scripts/apply_label_review_decisions.py
python3 paper3_beni_method/scripts/freeze_paper3_inputs.py
```

Exit criteria:

- unresolved review rows: 0
- frozen reference-label summary has stable label counts
- manuscript can report exactly how many labels were LLM-only, reviewed, revised, and excluded

## Priority 2: Regenerate Model Comparison

Use the selected frozen validation set:

- `data/annotations/beni_v1_reference_labels_frozen.jsonl`

Tasks:

- Update model-comparison script to use canonical BENI v1 article IDs.
- Decide whether evaluation uses all included labels or only `include_in_clean_validation == true`.
- Regenerate TF-IDF baseline results.
- Treat BanglaBERT as a comparison or appendix result unless rerun cleanly and documented.
- Save a new model-comparison file with a BENI v1-specific name.

Exit criteria:

- frozen comparison file exists for the repaired BENI v1 validation set
- production classifier is explicitly named

## Priority 3: Article-Level Predictions

Input:

- `data/processed/beni_unified_articles_deduped.csv.zst`

Output target:

- `data/index/beni_v1_article_predictions.parquet`

Required fields:

- canonical article ID
- publication date
- year-month
- source/newspaper
- harmonised category
- economic probability
- economic prediction
- model version
- prediction timestamp

Exit criteria:

- prediction row count matches documented inclusion rules
- no missing dates or IDs
- model version is frozen

Current note:

- `data/index/beni_v1_article_predictions.parquet` has been rebuilt from the repaired corpus.
- `data/index/beni_v1_monthly_index.csv` and the weighted variants now exist.
- use the frozen prediction and monthly files for downstream comparison and manuscript tables.

## Priority 4: Build Monthly BENI v1 Indices

Output target:

- `data/index/beni_v1_monthly_index.csv`

Required index variants:

- article-weighted economic attention
- source-balanced economic attention
- source-balanced version as preferred/default

Also produce:

- monthly source coverage table
- monthly category coverage table
- index QA summary

Exit criteria:

- later validation and nowcasting papers can use the frozen monthly file without rebuilding article predictions

## Priority 5: Regenerate Paper Tables

Minimum tables:

- data coverage by source/category/year
- annotation label counts and review outcomes
- model comparison
- monthly index summary
- conservative macro-validation diagnostics

Rule:

- Every table must be generated from files inside `paper3_beni_method`.

## Priority 6: Align Manuscript

Tasks:

- Remove final-result wording around old Potrika-only prototype numbers.
- Keep the old 120,707-article results in calibration/prototype framing or appendix.
- Update abstract, data, methods, results, and discussion to match frozen BENI v1 files.
- State clearly that LLM labels are reference labels, not independent human gold labels.
- State clearly that nowcasting is deferred to the next paper.

Exit criteria:

- every number in the manuscript can be traced to a frozen output file
- no claims depend on the old prototype index as if it were the final BENI v1 index

## Immediate Next Command Sequence

```bash
python3 paper3_beni_method/scripts/build_beni_v1_model_comparison.py
```
