# Bangla Economic Narrative Index (BENI): Research Roadmap

## Research Direction

BENI is the natural applied extension of the systematic review: a Bangla-language, news-based economic narrative index for Bangladesh and Bangla-speaking markets. The review establishes the absence. BENI should make that absence measurable.

The central question is simple, but not small: can Bangla news narratives reveal inflation pressure, output conditions, exchange-rate stress, and wider economic anxiety before official statistics fully absorb them?

## Core Claim To Test

News sentiment should not be treated as a magical forecasting layer, as if the newspaper knows the economy by instinct. For Bangladesh, the plausible value of BENI is more specific: it can act as a high-frequency proxy for expectation pressure and institutional stress in an economy where official data arrive late, informal activity is large, and financial-market channels are thinner than in the US and Europe.

The review's 10–15% realistic value-added estimate should be treated as an upper-bound benchmark, not a promise.

## Phase 1: Corpus Construction

Target sources:

- Prothom Alo
- The Daily Star
- Dhaka Tribune
- Financial Express
- New Age
- Business Standard Bangladesh, if coverage is usable
- Bangladesh Bank press releases and monetary-policy statements
- Ministry of Finance releases, where text is consistently available

Initial time window:

- Pilot: 2022–2025
- Full build: 2018–2025

Minimum fields:

- article_id
- source
- publication_date
- title
- body_text
- url
- language
- section/category
- scrape_timestamp
- duplicate_group_id

Data problems to expect early:

- Mixed Bangla-English text
- OCR or encoding noise in older material
- Article duplication across syndication
- Political/economic boundary ambiguity
- Paywalls or inconsistent archive structures

## Phase 2: Economic Filtering

The filtering problem matters because Bangladesh's economic news rarely arrives in a neat macroeconomic container. Price anxiety may appear in a market report, a political speech, a garment export story, or a household welfare frame. A two-stage filter is the safest starting point:

1. Broad economic relevance filter using Bangla and English keywords.
2. Supervised article classifier separating macroeconomic news from general politics, crime, sports, and lifestyle.

Candidate topic groups:

- inflation and prices
- exchange rate and reserves
- monetary policy and banking
- exports, garments, and trade
- remittances and migration
- energy and imports
- employment and wages
- fiscal policy and public finance
- political uncertainty with economic consequence

## Phase 3: Sentiment and Narrative Extraction

Baseline methods:

- Dictionary baseline using SentiBangla and domain-specific economic terms
- BanglaBERT sentiment classifier
- XLM-R or MuRIL comparison model

Narrative layer:

- keyATM for seeded narrative themes
- BERTopic as an exploratory robustness check if embeddings behave well
- Manual audit of topic coherence by domain experts

The design principle is interpretability. BENI should not only produce a sentiment line. It should show which economic stories are moving that line, because a black-box index is not very useful to a central banker, journalist, or researcher trying to understand why the mood shifted.

## Phase 4: Index Construction

Candidate indices:

- BENI Aggregate Sentiment Index
- BENI Inflation Pressure Index
- BENI Exchange-Rate Pressure Index
- BENI Banking/Financial Stress Index
- BENI External Sector Index
- BENI Uncertainty Index

Aggregation options:

- Daily article-weighted sentiment
- Source-balanced daily sentiment
- Topic-weighted sentiment
- Dynamic factor model combining sentiment and narrative prevalence

High-volume newspapers should not dominate the index merely because they publish more. Source weighting needs to be tested explicitly; otherwise the index may measure media scale rather than economic narrative pressure.

## Phase 5: Validation

Forecast targets:

- CPI inflation
- food inflation
- exchange rate
- foreign-exchange reserves
- import payments
- export receipts
- remittance inflows
- industrial production proxy, if available
- policy-rate changes or monetary-policy stance

Validation tests:

- lead-lag correlations
- Granger causality
- MIDAS regression for mixed-frequency nowcasting
- rolling-window out-of-sample tests
- Diebold-Mariano or Clark-West tests
- comparison against AR benchmarks and available survey/proxy indicators

Validation discipline:

- Use real-time vintages where available.
- Freeze model specifications before final test windows.
- Report null results directly.
- Benchmark against South Asian studies before comparing against US-heavy medians.

## Phase 6: Initial BENI Paper

Working title:

"The Bangla Economic Narrative Index: Local-Language News Sentiment and Real-Time Macroeconomic Monitoring in Bangladesh"

Proposed paper structure:

1. Motivation: why Bangladesh needs a local-language narrative index.
2. Data: corpus construction and economic filtering.
3. Method: sentiment, topic extraction, and index design.
4. Validation: inflation, exchange-rate pressure, reserves, and external-sector indicators.
5. Interpretation: what BENI captures that official data and English-language sources miss.
6. Policy use: central-bank nowcasting and early-warning dashboards.

## Immediate Next Actions

1. Create a source inventory with archive URLs and scraping feasibility.
2. Build a 1,000-article pilot corpus from 2022–2025.
3. Manually label 300 articles for economic relevance and sentiment.
4. Test BanglaBERT against a dictionary baseline.
5. Create the first monthly BENI prototype for inflation and exchange-rate narratives.
6. Compare BENI against CPI, food inflation, exchange rate, and reserves.
7. Write a short methods memo before expanding to the full corpus.

The first milestone should be modest: not a national index, not a dashboard, not a grand claim about prediction. The first milestone is a defensible pilot showing that Bangla economic narratives can be collected, filtered, scored, and compared against a small set of macroeconomic targets without methodological shortcuts.

## Decision Points

- Start with Bangla-only sources or include English Bangladeshi newspapers from the beginning?
- Build the first index around inflation only, or attempt a broader macroeconomic condition index?
- Position BENI first as a policy nowcasting tool, or as a methodological contribution in multilingual NLP for economics?
- Prototype in Python notebooks first, or build a reproducible package from day one?
