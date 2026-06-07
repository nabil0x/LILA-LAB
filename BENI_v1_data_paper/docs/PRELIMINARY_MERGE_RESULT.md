# Preliminary BENI Unified Merge Result

Generated with:

```bash
python3 BENI_v1_data_paper/scripts/build_beni_v1_articles.py
```

## Merge Rule

The preliminary unified panel uses:

- Potrika dated raw files for 2014-2020.
- BNAD JSONL files for 2021-2024.

The release-folder BNAD path is:

```text
BENI_v1_data_paper/data/raw/bnad
```

It is currently a symlink to:

```text
beni/Bangla_News_Database
```

## Outputs

| Output | Purpose |
|---|---|
| `data/processed/potrika_articles_canonical.csv` | Canonical Potrika articles. |
| `data/processed/bnad_articles_canonical.csv` | Canonical BNAD post-2020 articles. |
| `data/processed/beni_unified_articles.csv` | Preliminary merged article file. |
| `data/processed/beni_unified_articles_deduped.csv` | Same rows with exact duplicate text flags. |
| `data/processed/beni_unified_articles_summary.json` | Machine-readable build summary. |

## Counts

| Component | Rows |
|---|---:|
| Potrika 2014-2020 | 471,723 |
| BNAD 2021-2024 | 995,982 |
| Merged preliminary panel | 1,467,705 |
| Unique exact text hashes | 1,453,510 |
| Exact duplicate rows flagged | 14,195 |
| Exact duplicate groups | 11,951 |

## Year Coverage

| Year | Rows |
|---|---:|
| 2014 | 2,516 |
| 2015 | 30,693 |
| 2016 | 88,059 |
| 2017 | 78,009 |
| 2018 | 97,642 |
| 2019 | 76,987 |
| 2020 | 97,817 |
| 2021 | 282,886 |
| 2022 | 281,822 |
| 2023 | 364,350 |
| 2024 | 66,924 |

## Interpretation

This confirms the preliminary finding: the two datasets can be merged into a long Bangla news panel if source provenance is retained and the 2020/2021 source transition is treated as a diagnostic issue rather than ignored.

For paper use, describe this as a harmonised extension, not a blind pool. The next empirical step is to run source-break diagnostics around 2020/2021 and compare Potrika-only, BNAD-only, and unified monthly indices.
