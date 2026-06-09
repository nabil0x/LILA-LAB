# Paper 3 Focus Roadmap

## Role in the PhD

Paper 3 should be treated as the BENI method and measurement-foundation paper, not as the final macro-validation or nowcasting paper.

The strongest version of this paper is:

> A reproducible data-and-measurement paper showing how Bangla economic news can be transformed into a documented, versioned, locally interpretable narrative index.

The paper should not try to prove final predictive value. That belongs to the next BENI validation and nowcasting papers.

## Recommended Strategic Position

### Main Claim

Use this claim:

> BENI v1 provides a reproducible local-language measurement pipeline for converting Bangla news into article-level economic relevance scores and monthly narrative indicators for Bangladesh.

### Secondary Claim

Use this only after regenerated results are available:

> Calibration evidence shows that label quality matters more than model complexity in this low-resource economic-text setting.

### Avoid

- Do not claim that BENI already improves inflation nowcasting.
- Do not claim that the prototype Potrika index is the final BENI v1 index.
- Do not claim that LLM labels are independent human gold-standard labels.
- Do not treat BanglaBERT as the production model unless it is rerun, documented, and clearly superior on the relevant metrics.
- Do not let the paper become a generic NLP benchmark paper. The economics contribution is measurement infrastructure.

## Current Diagnosis

The folder is consolidated and the article corpus is now QA-ready, but the reference-label set and final index are not frozen.

Ready:

- BENI v1 processed database exists through `data/processed/`.
- Potrika and BNAD have been harmonised into a preliminary BENI v1 database.
- The earlier truncated compressed processed files have been regenerated.
- The regenerated article corpus passes `zstd -t` and full streaming QA.
- The canonical working article file contains 1,467,705 rows with no missing article IDs, missing dates, duplicate article IDs, or missing clean text.
- LLM-assisted annotation artifacts exist.
- All 300 annotation rows map to canonical BENI v1 article IDs.
- A label-review decision sheet exists and the unresolved rows have been conservatively excluded from clean validation.
- Prototype TF-IDF model, monthly index, and macro correlations exist.
- Manuscript draft and compiled PDF exist.

Not ready:

- The authoritative label set is now the clean frozen subset with ambiguous rows excluded.
- The older model-comparison file uses a 22/298 Economic evaluation universe, while the current candidate label set has 120/300 Economic labels.
- The current monthly index is still a prototype from the older Potrika subset.
- Final article-level BENI v1 predictions have been regenerated from the repaired corpus.
- Final source-balanced monthly indices have been generated from the repaired predictions.
- Manuscript numbers still mix BENI v1 database counts with older Potrika calibration results.
- Paper tables are not yet reproducible from final BENI v1 outputs.

## Paper 3 Must Deliver

Minimum publication package:

- Frozen BENI v1 article-level file.
- Frozen BENI v1 reference-label file.
- Frozen article-level prediction file.
- Frozen monthly index file.
- Source-balanced monthly index as the default index.
- Article-weighted monthly index as a robustness version.
- Annotation protocol documentation.
- Model comparison table.
- Coverage table by source, category, and year.
- Monthly index summary table.
- Conservative macro-validation diagnostic table.
- Reproducible scripts that generate the tables from the frozen files.
- Manuscript whose numbers match those files exactly.

## Roadmap

### Phase 1: Freeze the Measurement Object

Goal: create the canonical files that all later papers can cite.

Tasks:

- Treat `beni_unified_articles_deduped.csv.zst` as the canonical working BENI v1 article file for Paper 3.
- Document the exact merge rule: Potrika dated 2014-2020 plus BNAD post-2020.
- Confirm required columns: article ID, source, publication date, title, body text, category, language, duplicate group or text hash, economic seed label, model-ready text, model version fields.
- Add a release version string that is no longer `preliminary` once frozen.
- Keep `docs/PAPER3_INPUT_FREEZE_REPORT.md` updated with file hashes, row counts, and creation date.

Exit criteria:

- One canonical article file exists. Done for working analysis.
- One summary JSON exists. Done.
- One manifest/report names the canonical files and versions. Done as candidate freeze report.
- Final release version naming is still pending.

### Phase 2: Resolve the Label Set

Goal: make the annotation story defensible.

Tasks:

- Reconcile the two apparent label universes: the 120/300 Economic label set and the 22/298 Economic model-comparison set.
- Decide which label set is authoritative for Paper 3.
- Resolve the review queue by assigning each row one of: keep, revise, ambiguous-exclude.
- Create `beni_v1_reference_labels.jsonl`.
- Include fields for article ID, final label, confidence, review status, annotator type, source file, and version.
- Report LLM labels as reference labels, not human gold labels.
- If possible, manually adjudicate a small high-value subset of borderline cases and report that as human audit evidence.

Exit criteria:

- No unresolved review queue is required for the main results.
- Label counts in the manuscript match the frozen reference-label file.
- The paper can explain exactly how many labels are LLM-only, reviewed, revised, and excluded.

### Phase 3: Choose the Production Classifier

Goal: avoid model glamour and select the most defensible measurement model.

Recommended default:

- Use TF-IDF plus logistic regression as the production baseline unless BanglaBERT is rerun and clearly improves minority-class F1, calibration, or index stability.

Tasks:

- Rerun TF-IDF/logistic regression using the frozen label and weak-label protocol.
- Evaluate against the frozen reference-label file.
- Report accuracy, precision, recall, F1 for Economic, macro F1, Cohen's kappa, and calibration diagnostics.
- Treat BanglaBERT as either a documented comparison model or an appendix result unless it is production-ready.
- Save the final model artifact with a versioned name.

Exit criteria:

- One production model is named.
- One model-comparison table is regenerated from scripts.
- The manuscript no longer implies that model complexity is a contribution by itself.

### Phase 4: Generate BENI v1 Predictions

Goal: create the frozen article-level measurement layer.

Tasks:

- Run the production classifier on the canonical BENI v1 article file.
- Save article-level predictions with article ID, date, source, category, economic probability, binary label, model version, and prediction timestamp.
- Check missing dates, missing text, and duplicate handling.
- Decide whether duplicate rows are excluded, downweighted, or retained with a duplicate flag.

Exit criteria:

- `beni_v1_article_predictions.parquet` or equivalent exists.
- Prediction counts match the canonical article file after documented exclusions.
- A short QA report confirms date range, source counts, and missingness.

### Phase 5: Build Monthly BENI Indices

Goal: produce the index that later papers will use.

Tasks:

- Construct monthly economic-attention index.
- Construct article-weighted monthly index.
- Construct source-balanced monthly index.
- Treat source-balanced BENI as the preferred specification.
- Add confidence bands or uncertainty notes if feasible.
- Generate summary statistics by period and source.
- Save frozen monthly files with versioned names.

Exit criteria:

- `beni_v1_monthly_index.csv` exists.
- It includes article-weighted and source-balanced variants.
- Later validation and nowcasting papers can use it without recomputing the whole pipeline.

### Phase 6: Rebuild Validation Diagnostics

Goal: provide modest external validation without overclaiming prediction.

Tasks:

- Align monthly BENI with CPI, food inflation if available, exchange rate, reserves, and other macro indicators.
- Report level and first-difference correlations.
- Report lead-lag diagnostics.
- Separate pre-COVID, COVID, and post-COVID periods where sample size permits.
- Clearly label these as validation diagnostics, not nowcasting tests.
- Do not use these diagnostics as the main contribution if results are weak.

Exit criteria:

- One macro-validation table is regenerated from final BENI v1.
- Null first-difference results are reported plainly if they remain weak.

### Phase 7: Rewrite the Manuscript Around the Right Claim

Goal: make the paper coherent and submission-ready.

Tasks:

- Update abstract so it does not mix final BENI v1 with prototype Potrika results.
- Move old Potrika-only results into a calibration subsection or appendix.
- Ensure every number in the manuscript comes from a named output file.
- Add a data availability and reproducibility section.
- Add a limitations paragraph on LLM labels, source imbalance, and low positive-class prevalence.
- Add a clear bridge to the next validation and nowcasting papers.

Exit criteria:

- All tables and numbers are traceable.
- No section asks the reader to trust a prototype as final evidence.
- The paper reads as a data-and-measurement contribution in economics.

### Phase 8: Submission Readiness

Goal: prepare the package for a realistic first venue.

Tasks:

- Fix LaTeX warnings that affect layout or references.
- Produce final PDF.
- Create a release manifest.
- Create a replication README.
- Create a dataset card or data appendix.
- Create a short cover-letter paragraph emphasizing multilingual economic measurement.

Exit criteria:

- Manuscript, data, code, and documentation agree.
- The paper can be submitted without needing hidden local context.

## Suggested Task Order

1. Regenerate model comparison from the frozen validation set.
2. Rebuild tables.
3. Rewrite manuscript.
4. Compile and package.

## What To Defer

Defer these to the next papers:

- Granger causality as a central result.
- Inflation nowcasting.
- ARIMA, ARIMAX, MIDAS, Diebold-Mariano, or Clark-West tests.
- Strong claims about policy forecasting value.
- Full thematic sub-indices unless the annotation/modeling framework already supports them.

## Practical Weekly Plan

### Week 1

- Resolve labels.
- Create frozen reference-label file.
- Decide production model.
- Write annotation-method subsection.

### Week 2

- Generate article-level predictions.
- Build article-weighted and source-balanced monthly indices.
- Produce QA report.

### Week 3

- Regenerate tables.
- Rebuild validation diagnostics.
- Update methods and results sections.

### Week 4

- Rewrite introduction, abstract, discussion, and limitations.
- Compile PDF.
- Prepare release manifest and replication notes.

## Personal Research Secretary Advice

The fastest publishable path is not to chase a better model. The fastest path is to make BENI v1 auditable.

For this paper, the reader should come away thinking:

> This is a careful, reproducible measurement system for Bangla economic narratives. The author knows exactly where the labels, models, uncertainty, and macro-validation limits are.

That is stronger than claiming the index already nowcasts inflation. The nowcasting claim should be earned in the next paper using the frozen index from this one.
