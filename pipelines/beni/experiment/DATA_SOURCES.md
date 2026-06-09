# Data Sources

## Potrika (primary BENI news source)

**Status**: ✅ Downloaded and processed locally (39 CSV files, 3.3 GB)

- **Source page**: https://data.mendeley.com/datasets/v362rp78dc/4
- **DOI**: `10.17632/v362rp78dc.4`
- **License**: CC BY 4.0
- **Period covered**: 2014–2020
- **Sources**: Jugantor, Jaijaidin, Ittefaq, Kaler Kontho, Inqilab, Somoyer Alo
- **Categories**: National, Sports, International, Entertainment, Economy, Education, Politics, Science & Technology
- **Raw size**: 664,880 articles, 185.51M words
- **Balanced size**: 320,000 articles (40,000 per category)
- **Local path**: `beni/experiment/data/raw/potrika/`

### Potrika files on disk

```
Economy_40k.csv, Education_40k.csv, ..., Sports_40k.csv           (8 balanced CSVs)
Inqilab__*_economy_text.csv, Inqilab__*_national_text.csv, ...     (raw newspaper CSVs)
Jaijaidin__*_economy_text.csv, ..., SomoyerAlo__*_worldnews_text.csv
```

### How to re-download

The Mendeley page offers a "Download All" button. Direct S3 URLs require authentication. Manual download recommended:
1. Go to https://data.mendeley.com/datasets/v362rp78dc/4
2. Download the ZIP
3. Extract to `beni/experiment/data/raw/potrika/`

### Processed export

```bash
python3 beni_pilot/potrika.py --category Economy
```

Output: `beni/experiment/data/processed/potrika_economy.csv` (40,451 Economy articles)

## Macroeconomic Indicators

**Status**: ✅ Downloaded via API

| Indicator | File | Source | Method | Period |
|-----------|------|--------|--------|--------|
| BDT/USD FX (monthly) | `fx_bdt_usd_bis_eop_monthly.csv` | BIS API | REST (`https://stats.bis.org/api/v1/`) | 2014-01 to 2025-12 |
| CPI Index (monthly) | `cpi_imf_bgd_index_monthly.csv` | IMF SDMX | SDMX REST (`http://sdmx.imf.org/`) | 2010-01 to 2026-04 |
| BDT/USD FX (monthly) | `fx_bdt_usd_imf_eop_monthly.csv` | IMF SDMX | SDMX REST | 1972-01 to 2026-04 |
| Reserves (annual) | `reserves_wb_annual.csv` | World Bank API v2 | `https://api.worldbank.org/v2/` | 2014 to 2024 |

**Script**: `beni/experiment/scripts/download_macro.py`

**Storage**: `beni/data/raw/macro/`

All four series are machine-accessible without authentication. No API keys required.

### Macro data notes

- **BIS FX**: End-of-period monthly spot rate, BDT per USD. `TIME_PERIOD` format: `YYYY-MM`. Direct CSV download from BIS statistics API.
- **IMF CPI**: Consumer Price Index, All items, Index. Country: Bangladesh (BGD). `TIME_PERIOD` format: `YYYY-Mmm`. Filtered to non-null observations (~2010 onward). Downloaded via IMF SDMX REST API.
- **IMF FX**: End-of-period exchange rate, national currency per USD (XDC_USD). `TIME_PERIOD` format: `YYYY-Mmm`. Downloaded via IMF SDMX REST API.
- **World Bank Reserves**: Total reserves (including gold, current US$). Indicator: `FI.RES.TOTL.CD`. Downloaded via World Bank API v2.

## BanglaNLP News Categorization (baseline only)

**Status**: ✅ Downloaded, used for initial prototype

- **Source**: https://banglanlp.github.io/bnlp-resources/news_categorization/
- **Repository**: https://github.com/banglanlp/bnlp-resources
- **License**: CC BY-NC-SA 4.0
- **Splits**: `train.tsv`, `dev.tsv`, `test.tsv`
- **Path**: `beni/experiment/data/raw/news_categorization/`

Labels: kolkata, state, national, sports, entertainment, international.

This dataset has no Economy class and no timestamps. Used only for initial pipeline validation (89% topic accuracy, 95% weak economic relevance). Replaced by Potrika for all production experiments.

## BARD (fallback)

- **Source**: https://data.mendeley.com/datasets/ntg3m8mw8d/1
- **Size**: 2,500 articles
- **Categories**: Economy, Entertainment, International, Sports, State
- **License**: CC BY 4.0
- **Status**: Not downloaded (Potrika provides better coverage)

## Pretrained Models

Both downloaded from Hugging Face:

| Model | Path | Size |
|-------|------|------|
| `csebuetnlp/banglabert` (Electra) | `beni/experiment/models/csebuetnlp-banglabert/` | 424 MB |
| `sagorsarker/bangla-bert-base` (BERT) | `beni/experiment/models/bangla-bert-base/` | 633 MB |

Downloaded via `transformers` `.from_pretrained()` — can be re-downloaded on Kaggle directly.
