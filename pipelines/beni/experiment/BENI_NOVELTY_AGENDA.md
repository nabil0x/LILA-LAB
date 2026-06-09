# BENI Novelty Agenda

## Starting Point

The JER manuscript establishes the research gap: economic narrative and sentiment indices are concentrated in English-language, US/European settings, with no Bangla economic narrative index despite Bangladesh's large media ecosystem and macroeconomic volatility.

The BENI experiment folder already has:

- a reproducible Bangla news baseline classifier;
- weak economic relevance labels;
- a Potrika Economy loader;
- a time-series narrative-model sketch;
- a Nietzsche-inspired valuation framework for collective newspaper consciousness.

The next work should not be another generic Bangla news classifier. That space already exists. The novel contribution is to build a Bangla economic narrative index that measures how economic meaning travels across newspaper sections, not only whether text is positive or negative.

## Highest-Potential Novel Paper

### Title

**From Economic News to Collective Economic Consciousness: A Bangla Economic Narrative Index from Newspaper Section Dynamics**

### Core Research Question

How do Bangla newspapers transform macroeconomic events into collective public meaning across Economy, Politics, National, International, and Editorial sections?

### Main Novelty

Most published economic sentiment indices treat news as a single stream. BENI can instead treat the newspaper as a structured social machine:

- Economy pages translate events into technical-policy language.
- Politics pages translate them into blame and legitimacy.
- National pages translate them into household burden.
- International pages translate them into external shock and dependence.
- Editorial pages condense them into moral interpretation.

The novel unit is therefore not only article sentiment. It is **sectional narrative migration**: the movement of economic language from technical reporting into political, household, or moral frames.

## Proposed Index Components

### 1. Economic Relevance

Binary or probabilistic classification:

- economic vs non-economic;
- trained first with weak labels, then improved with 300-500 human labels.

### 2. Economic Topic

Multi-label topic layer:

- inflation;
- exchange rate;
- reserves;
- banking;
- fiscal policy;
- trade;
- employment;
- growth/investment.

### 3. Narrative Force

Frame layer:

- crisis;
- burden;
- blame;
- reform;
- stability;
- uncertainty;
- resilience;
- recovery.

### 4. Valuation Target

Who or what receives responsibility:

- government;
- Bangladesh Bank;
- banks;
- businesses;
- market syndicates;
- global economy;
- consumers/households;
- unnamed system.

### 5. Sectional Migration Score

Measure whether an economic topic remains in the Economy section or spreads into other sections.

Example:

```text
Inflation in Economy only        -> technical-policy signal
Inflation in National            -> household-burden signal
Inflation in Politics            -> blame/legitimacy signal
Inflation in Editorial           -> moralized crisis signal
```

This is the most publishable novelty because it is interpretable, local to Bangladesh, and methodologically different from standard sentiment indices.

## Primary Hypotheses

### H1: Sectional Migration Hypothesis

Economic narratives become socially salient when they migrate from Economy pages into National, Politics, and Editorial sections.

### H2: Blame Intensification Hypothesis

Economic topics appearing in Politics and Editorial sections carry stronger blame and crisis language than the same topics in Economy sections.

### H3: Household Burden Hypothesis

Inflation and food-price narratives become more negative when reported through National/local sections than through Economy/business sections.

### H4: External Dependence Hypothesis

Exchange-rate, reserves, remittance, and import narratives are more likely to be framed through International/external-shock language than purely domestic policy language.

### H5: Narrative Lead Hypothesis

Narrative pressure in newspapers leads official macroeconomic indicators or policy responses by several weeks, especially around inflation, exchange-rate pressure, and reserves.

## Minimum Viable Study

### Data

Use Potrika if available:

- Economy;
- Politics;
- National;
- International;
- Editorial if separately available or scraped later.

If Potrika lacks editorial pages, start with the available sections and add editorial scraping as a second dataset.

### Sample

Minimum:

- 2,000 articles total;
- 400 Economy;
- 400 Politics;
- 400 National;
- 400 International;
- 200-400 manually annotated for topic, force, and valuation target.

Stronger:

- full Potrika Economy plus balanced section samples;
- all date-stamped articles from 2014-2020;
- post-2020 extension from Prothom Alo, Daily Star Bangla, TBS Bangla, and Dhaka Tribune Bangla.

### Models

Baseline:

- TF-IDF + logistic regression;
- keyword dictionaries for topic and narrative force;
- section-level aggregation.

Research-grade:

- BanglaBERT or XLM-R for classification;
- seeded topic model or BERTopic for topic discovery;
- dynamic factor model to combine narrative-force signals into BENI;
- rolling-window validation against CPI, exchange rate, reserves, policy rate, and remittance data.

## Validation Design

### Text Validation

- train/dev/test split by time, not random only;
- macro-F1 for economic topic and narrative force;
- calibration curves for predicted probabilities;
- inter-annotator agreement on human labels;
- temporal robustness test: train on earlier years, test on later years.

### Economic Validation

Use BENI as a predictor for:

- CPI inflation;
- exchange rate pressure;
- reserves;
- remittance flow;
- policy-rate changes;
- DSE market movement if useful.

Models:

- AR benchmark;
- AR + BENI;
- MIDAS regression if using high-frequency news and monthly/quarterly indicators;
- Diebold-Mariano test for forecast comparison;
- Granger causality only as supporting evidence, not causal proof.

## Paper Contributions

1. First Bangla Economic Narrative Index for Bangladesh.
2. First section-aware economic narrative measure, distinguishing technical, political, household, external, and moralized economic language.
3. A local-language validation framework connected to the JER review's identified gaps.
4. A manually annotated Bangla economic narrative dataset.
5. Evidence on whether newspaper narrative pressure leads macroeconomic indicators or policy responses.

## Why This Is Novel Enough

Existing Q1 work already builds newspaper-based sentiment and uncertainty indices. BENI should not compete by merely translating those methods into Bangla.

The stronger novelty is conceptual:

> Economic narratives do not only vary over time; they move across institutional spaces inside the newspaper.

That movement is measurable. Once inflation leaves the Economy page and enters Politics, National, and Editorial pages, it has stopped being only a macroeconomic statistic. It has become a collective social fact.

## Immediate Build Plan

1. Obtain Potrika manually from Mendeley and place it under:

```text
_prep/beni_experiment/data/raw/potrika/
```

2. Export section/category subsets:

```bash
cd _prep/beni_experiment/beni_pilot
python3 potrika.py --category Economy
python3 potrika.py --category Politics --output ../data/processed/potrika_politics.csv
python3 potrika.py --category National --output ../data/processed/potrika_national.csv
python3 potrika.py --category International --output ../data/processed/potrika_international.csv
```

3. Create a 300-article annotation sheet with columns:

```text
article_id, source, date, section, headline, text,
economic_relevance, topic, narrative_force, valuation_target, notes
```

4. Implement section-level BENI features:

```text
economic_density
topic_density
crisis_force
blame_force
burden_force
uncertainty_force
sectional_migration_score
cross_source_convergence
```

5. Build the first BENI paper around section dynamics before moving to transformer-heavy modeling.

## Best Target Framing

For economics journals:

**A local-language economic narrative index for Bangladesh with real-time validation.**

For computational social science journals:

**A section-aware model of how newspapers manufacture collective economic meaning.**

For NLP journals:

**A Bangla economic narrative dataset and benchmark with multi-layer labels.**

The strongest version is economics plus computational social science: interpretable, empirical, and clearly motivated by the JER systematic review.
