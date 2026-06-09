# Paper Readiness Declaration

## Current Status as of 2026-06-08

Paper 3 has moved from a loose prototype workspace to a partially frozen method-paper workspace.

The major change is that the BENI v1 processed article files were repaired. The earlier compressed BENI v1 files were truncated and failed decompression integrity checks. They have now been regenerated from raw Potrika and BNAD sources, verified with `zstd -t`, and streamed successfully through the Paper 3 QA script.

Current article-corpus status:

- canonical working file: `data/processed/beni_unified_articles_deduped.csv.zst`
- rows: 1,467,705
- unique article IDs: 1,467,705
- missing article IDs: 0
- duplicate article IDs: 0
- missing publication dates: 0
- missing clean text: 0
- zstd stream status: clean
- canonical BENI v1 release string: `BENI_unified_v1.0_frozen`

Current reference-label status:

- candidate reference labels: 300
- Economic labels: 120
- Not Economic labels: 180
- canonical BENI v1 article-ID mappings: 300/300
- unresolved review rows: 0
- high-confidence clean-validation rows before review: 186
- conservative exclusions: 114

Remaining comparison note:

- The current candidate label file has 120/300 Economic labels.
- The frozen BENI v1 comparison file uses the 186-row clean validation set and the repaired article-level predictions.
- The legacy `model_comparison.json` remains in the folder as prototype/calibration evidence.

## Current Decision

BENI v1.0 is being refined as a **data-and-measurement paper**.

It should not be submitted yet because the release still needs regenerated model-comparison tables and manuscript alignment.

## What Is Ready

- Upstream Potrika and BNAD data are present locally.
- BENI v1 processed article files have been regenerated and pass compression integrity checks.
- The canonical working article file streams cleanly through QA.
- Macro data are present locally.
- LLM-assisted 300-article annotation files are present.
- All 300 annotation rows now map to canonical BENI v1 article IDs.
- A review-decision sheet exists for unresolved labels.
- Scripts now exist for input-freeze reporting, label-review preparation, label-decision application, and annotation-to-corpus ID mapping.
- A TF-IDF model artifact is present, but it belongs to the prototype workflow.
- Prototype index outputs are present, but they should not be used as final BENI v1 results.
- The existing draft manuscript can be adapted.

## What Is Not Ready

- The manuscript must be updated to match the frozen BENI v1 outputs exactly.
- BanglaBERT remains legacy prototype evidence unless rerun and documented.

## Recommended Target Paper Claim

Use:

> This paper introduces BENI v1.0, a reproducible derived data release and measurement pipeline that transforms the Potrika Bangla news corpus into an economic narrative index for Bangladesh.

Avoid:

> This paper introduces a new raw Bangla news corpus.

## Readiness Rating

Current readiness:

- Dataset organization: high.
- Raw data availability: high.
- Article-corpus integrity: high.
- Annotation documentation: medium-high.
- Canonical label finality: medium-low.
- Canonical release file: high.
- Paper-table reproducibility: medium-low.
- Submission readiness: not yet.

Next milestone:

> Finish manuscript alignment and final release packaging around the frozen BENI v1 outputs.
