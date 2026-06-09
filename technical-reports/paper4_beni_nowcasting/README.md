# Paper 4: BENI Inflation Nowcasting

This folder implements the empirical plan for:

**Nowcasting Inflation with the Bangla Economic Narrative Index: Local-Language News as a High-Frequency Economic Indicator**

The current implementation uses the TF-IDF BENI index from Paper 3 as a placeholder instrument. Final paper results should be rerun after the BanglaBERT BENI index is frozen.

## Current Status

Implemented:

- Recursive pseudo-real-time forecasting for horizons `h=0`, `h=1`, and `h=3`.
- AR benchmark, AR + BENI, AR + BENI + FX, and nonlinear random forest robustness model.
- CPI inflation target from IMF CPI.
- BDT/USD FX control from BIS.
- Asymmetry analysis for acceleration/deceleration/stable inflation regimes.
- Feature correlation diagnostics.
- Figures and LaTeX-ready tables.
- Manuscript draft.

Current empirical finding:

- BENI is strongly correlated with CPI inflation in levels.
- The TF-IDF BENI placeholder does not materially improve h=0 or h=1 nowcasts.
- It gives a small RMSE gain at h=3 for AR + BENI.
- This should be treated as provisional until the Paper 3 BENI index is finalized.

## Reproduce

From the repository root:

```bash
python3 technical-reports/paper4_beni_nowcasting/scripts/run_nowcasting.py
```

Outputs are written to:

- `results/tables/forecast_metrics.csv`
- `results/tables/asymmetry_metrics.csv`
- `results/tables/feature_correlations.csv`
- `results/figures/beni_vs_inflation.png`
- `results/figures/nowcast_actual_vs_predicted.png`
- `results/summary.json`

## Inputs

Default inputs:

- `beni/experiment/outputs/index/narrative_index.csv`
- `beni/data/raw/macro/cpi_imf_bgd_index_monthly.csv`
- `beni/data/raw/macro/fx_bdt_usd_bis_eop_monthly.csv`

## Next Paper Tasks

- Replace TF-IDF BENI with the final Paper 3 BENI index.
- Add English-language benchmark data if available.
- Add food/core CPI if reliable monthly files are added.
- Add Diebold-Mariano tests and bootstrap confidence intervals.
- Add MIDAS/GDP controls once quarterly GDP data is in the repo.
- Recompile manuscript after final results.
