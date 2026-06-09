# Paper 5 Coding Schema

Each reviewed paper should be coded at the paper level. The seed database is deliberately small and curated; the final review should expand it through formal database search, deduplication, and screening.

## Required Fields

- `paper_id`: stable short identifier.
- `year`: publication or working-paper year.
- `authors`: author string.
- `title`: paper title.
- `discipline`: primary field.
- `era`: historical era used in the manuscript.
- `method_family`: dominant method family.
- `task`: main research task.
- `language`: primary language coverage.
- `geographic_focus`: main country/region focus.
- `data_type`: dominant text source.
- `validation`: strongest validation type used.
- `llm_relevance`: `none`, `pre_llm_foundation`, `direct_llm`.
- `notes`: short coding rationale.

## Era Values

- `content_analysis_1916_1950`
- `quant_content_1950_1980`
- `computer_assisted_1980_2000`
- `dictionary_2000_2010`
- `topic_ml_2010_2018`
- `transformers_2018_2022`
- `llm_2022_2026`

## Validation Values

- `conceptual`
- `manual_coding`
- `intercoder_reliability`
- `dictionary_validation`
- `heldout_accuracy`
- `external_outcome_validation`
- `forecast_validation`
- `benchmark_leaderboard`
- `human_llm_comparison`

## Final Review Expansion

The final systematic review should add:

- Search source.
- Search query.
- Screening decision.
- Exclusion reason.
- DOI/URL.
- Citation count.
- Country and language codes.
- Multiple-method flags.
- Replication/data availability.
