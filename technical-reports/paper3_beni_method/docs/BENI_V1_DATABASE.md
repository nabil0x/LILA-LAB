# BENI v1 Database for the Method Paper

## Decision

The method paper will use the BENI v1 database, not the older Potrika-only prototype index, as its main empirical database.

## Current BENI v1 Files

The method-paper folder links to the processed BENI v1 files through:

- `paper3_beni_method/data/processed/`

This points to:

- `BENI_v1_data_paper/data/processed/`

Main files:

- `beni_unified_articles.csv.zst`
- `beni_unified_articles_deduped.csv.zst`
- `potrika_articles_canonical.csv.zst`
- `bnad_articles_canonical.csv.zst`
- `beni_unified_articles_summary.json`
- `schema_audit/`

## Current Counts

From `beni_unified_articles_summary.json`:

- Potrika rows: 471,723
- BNAD rows: 995,982
- merged rows: 1,467,705
- deduped rows: 1,467,705
- duplicate rows flagged: 14,195
- release version: `BENI_unified_v1.0_frozen`
- merge rule: Potrika dated 2014-2020 plus BNAD post-2020

## Implication for the Manuscript

The current manuscript now uses the frozen BENI v1 validation outputs as the production baseline. The older 120,707 Potrika experiment should be treated as prototype evidence only.

The remaining work is manuscript alignment: make every reported count, table, and caption traceable to the frozen BENI v1 outputs and keep the legacy prototype results clearly labeled as such.
