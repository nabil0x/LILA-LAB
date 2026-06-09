# Paper 3 Input Freeze Report

Generated at: `2026-06-08T13:07:16+00:00`

## Decision

This is the BENI v1 input freeze snapshot for Paper 3. The article database can be treated as the current empirical base, and the reference labels are now frozen with the ambiguous rows conservatively excluded from clean validation.

## Article Database

- file: `data/processed/beni_unified_articles_deduped.csv.zst`
- sha256: `e519989e0bcbc0fbbc5856e6c8468b588ee720ad7ac68ddc2ef92ee7ef9c6c55`
- streamed rows: 1,467,705
- unique article IDs: 1,467,705
- missing article IDs: 0
- duplicate article IDs: 0
- missing publication dates: 0
- missing clean text: 0
- rows with replacement characters during UTF-8 streaming: 1
- zstdcat return code: 0
- stream completed cleanly: True
- missing required columns: none

Counts from streamed article file:

- dataset sources: `{'bnad': 995982, 'potrika': 471723}`
- release versions: `{'BENI_unified_v1.0_frozen': 1467705}`
- duplicate flags: `{'false': 1453510, 'true': 14195}`
- languages: `{'bn': 1467705}`
- years: `{'2014': 2516, '2015': 30693, '2016': 88059, '2017': 78009, '2018': 97642, '2019': 76987, '2020': 97817, '2021': 282886, '2022': 281822, '2023': 364350, '2024': 66924}`
- top categories: `{'national': 780271, 'other_or_unknown': 369643, 'international': 79608, 'sports': 67729, 'economy': 57792, 'politics': 53714, 'entertainment': 39335, 'education': 9442, 'technology_science': 5544, 'health': 4627}`

Counts from existing summary JSON:

- release version: `BENI_unified_v1.0_frozen`
- merge rule: Potrika dated 2014-2020 plus BNAD post-2020.
- merged rows: 1,467,705
- duplicate rows flagged: 14,195

Important QA note: if `stream completed cleanly` is false, this compressed CSV should not be treated as a final frozen corpus file until it is regenerated or recompressed successfully.

## Reference Labels

- candidate file: `data/annotations/beni_v1_reference_labels_candidate.jsonl`
- sha256: `3aff2c312c1cf65fc0216d8408218620fd49e9c16e6665e55ee38f1bdc3c16eb`
- locked labels: 300
- LLM annotation rows: 300
- candidate label counts: `{'Not Economic': 180, 'Economic': 120}`
- annotation status counts: `{'llm_assisted': 186, 'needs_review': 114}`
- confidence counts: `{'3': 186, '2': 114}`
- difficulty counts: `{'None': 180, 'Clear-cut': 69, 'Borderline': 51}`
- rows requiring review: 0
- clean validation rows: 186
- locked-vs-LLM label mismatches: 0
- canonical BENI v1 IDs mapped: 300

## Review Queue

- exists: True
- rows unresolved: 0
- rows excluded from clean validation: 114
- label counts among excluded rows: `{'Not Economic': 63, 'Economic': 51}`
- confidence counts among excluded rows: `{'2': 114}`
- difficulty counts among excluded rows: `{'': 63, 'Borderline': 51}`

## Model-Comparison Mismatch To Resolve

The candidate reference-label file has 120 Economic and 180 Not Economic labels. The frozen BENI v1 comparison file uses the clean 186-row validation set:

- model comparison metadata: `{'n_total': 186, 'n_economic_gold': 69, 'n_economic_tfidf': 55, 'n_economic_majority_baseline': 0, 'n_excluded_from_clean_validation': 114, 'n_included_in_clean_validation': 186}`

The older `model_comparison.json` remains in the folder as prototype evidence only.

## Next Actions

1. Regenerate any remaining manuscript tables from the frozen comparison and monthly outputs.
2. Keep the legacy prototype comparison clearly labeled as prototype evidence.
