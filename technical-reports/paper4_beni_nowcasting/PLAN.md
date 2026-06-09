# Paper 4 — Nowcasting Inflation with the Bangla Economic Narrative Index: Local-Language News as a High-Frequency Economic Indicator

**Status**: ✅ Prototype implemented — TF-IDF BENI evaluated, manuscript drafted, awaiting Paper 3 frozen index
**Timeline**: August–September 2026 (6 weeks). **Dependent on Paper 3** — final results require the frozen BanglaBERT BENI index.
**Current state**: Nowcasting pipeline built (pseudo-real-time, h=0/1/3), 4 models evaluated, asymmetry analysis done, manuscript drafted (135 lines). Prototype results show BENI correlated with CPI in levels but TF-IDF placeholder does not materially improve nowcasts.

---

## 1. What We Learned from the Prototype

The TF-IDF BENI prototype run tells us:

| Finding | Detail | Implication |
|---------|--------|-------------|
| **Level correlation** | BENI vs CPI: $r = 0.54$ (mean prob), $r = 0.53$ (economic share) | BENI tracks the inflation environment — useful as monitoring indicator |
| **h=0 nowcast** | AR+BENI RMSE is **0.88% worse** than AR | TF-IDF BENI adds noise at same-month horizon |
| **h=1 nowcast** | AR+BENI RMSE is **2.50% worse** than AR | One-month ahead: TF-IDF BENI hurts |
| **h=3 nowcast** | AR+BENI RMSE improves **0.68%** vs AR | Small gain at quarter horizon — possible lead signal |
| **Asymmetry** | No clear acceleration advantage at h=0; modest at h=3 | Too few regime months to conclude |
| **Random forest** | Does not improve over linear AR | Nonlinear gains not present in this short sample |
| **FX control** | Adding BDT/USD weakens forecast | Exchange rate may not be the right control (or sample too short) |

**Key lesson**: The TF-IDF BENI is too coarse for short-horizon nowcasting. The signal is in the long-run co-movement. The BanglaBERT version (from Paper 3) may improve the short-run signal by reducing classification noise.

---

## 2. Core Research Question

> Can a local-language economic narrative index (BENI) improve inflation nowcasting in Bangladesh compared to models using only official statistics and English-language news?

### Sub-questions
1. Does BENI contain incremental predictive content for CPI inflation beyond autoregressive dynamics?
2. How does BENI compare against English-language news-based indices (e.g., Google Trends)?
3. Does BENI perform asymmetrically — better at detecting inflation accelerations vs. decelerations?
4. Which narrative domains (inflation, exchange rate, trade, fiscal) carry the most predictive signal?

---

## 3. Contribution (Refined After Prototype)

| Layer | Contribution | Cited By |
|-------|-------------|----------|
| **Empirical** | First inflation nowcasting model using Bangla-language news | Development economists, central bankers |
| **Methodological** | Pseudo-real-time nowcasting protocol with narrative data | Time-series econometricians |
| **Comparative** | Local-language vs English-language news for Bangladesh (if Google Trends available) | NLP + economics cross-linguistic research |

The paper now has a clearer narrative arc:
1. BENI tracks inflation in levels → monitoring value exists (uncontroversial, already shown)
2. TF-IDF BENI → weak nowcast gains → sets a benchmark
3. BanglaBERT BENI → expected improvement → the test
4. Even a null nowcast result is publishable: "local-language news has monitoring value but limited nowcast value" is a useful finding for the field

This is the paper that moves BENI from "interesting correlation" to "practical policy tool." It answers the question: *If the Bangladesh Bank had BENI as a dashboard, would they make better inflation forecasts?*

---

## 4. Paper 3 Dependency Protocol

Paper 4 **requires** the frozen BENI index from Paper 3. The re-execution workflow:

### Step 1: Await Paper 3 Freeze
Paper 3 produces a frozen BanglaBERT-based BENI index (narrative_index_v2.csv).

### Step 2: Verify Index Consistency
- [ ] Check time coverage matches Paper 4 period (2014-09 to 2020-12)
- [ ] Verify index construction (economic share and mean probability)
- [ ] Compare TF-IDF vs BanglaBERT BENI: correlation, mean shift, volatility

### Step 3: Re-run Nowcasting Pipeline
```bash
python3 technical-reports/paper4_beni_nowcasting/scripts/run_nowcasting.py
```
- [ ] Same protocol (pseudo-real-time, h=0/1/3, 2018-01 to 2020-12 test window)
- [ ] Same models (M1–M4) — the only change is the BENI index
- [ ] Repeat asymmetry analysis with new index

### Step 4: Compare Results

| Benchmark | TF-IDF BENI (current) | BanglaBERT BENI (expected) |
|-----------|----------------------|---------------------------|
| h=0 ΔRMSE vs AR | +0.88% (worse) | Expected: -3% to -8% |
| h=1 ΔRMSE vs AR | +2.50% (worse) | Expected: -2% to -6% |
| h=3 ΔRMSE vs AR | -0.68% (small gain) | Expected: -5% to -12% |
| Level correlation | r = 0.54 | Expected: r = 0.60+ |

If BanglaBERT BENI improves nowcasts → paper is strong.
If BanglaBERT BENI does not improve nowcasts → paper is still publishable (null result with honest interpretation).

---

## 5. Paper Structure

### Title
> Nowcasting Inflation with the Bangla Economic Narrative Index: Local-Language News as a High-Frequency Economic Indicator

### Sections

**1. Introduction** (~1.5 pages)
- Bangladesh inflation forecasting is challenging: data arrives late (2-month lag), informal sector is large (~35% of economy), English-language news covers only business elite
- BENI provides a same-month signal in Bangla — the language 98% of the population reads
- Question: does this local-language signal improve inflation nowcasts?
- Preview of findings: [X]% RMSE improvement over AR benchmark at h=3; level correlation confirms monitoring value

**2. Related Work** (~1 page)
- **Inflation nowcasting**: Stock & Watson (1999), Giannone et al. (2008)
- **News-based nowcasting**: Thorsrud (2016, 2018) — topic-based nowcasting for Norway
- **Developing economy nowcasting**: limited — most work is US/EU
- **Local-language advantage**: theoretical case (Gorodnichenko et al. 2023), no empirical evidence for South Asia

**3. Data** (~1.5 pages)
- **BENI index**: monthly narrative index from Paper 3 (2014-2020, 79 months) — BanglaBERT-based after freeze
- **CPI inflation**: monthly, Bangladesh Bureau of Statistics (via IMF SDMX)
  - Headline CPI (primary target)
  - Food CPI and core CPI (if available) — secondary targets
- **English-language benchmark**: Google Trends for "Bangladesh inflation" (if collected)
- **Control variables**: AR terms, BDT/USD FX, oil prices

**4. Methods** (~2 pages)
- **4.1 Baseline**: ARIMA(p,d,q) with automatic order selection (AIC)
- **4.2 Pseudo-real-time evaluation**: recursive expanding window
  - Train: 2014-06 to 2017-12, test: 2018-01 to 2020-12
  - h = 0 (nowcast), h = 1 (1-month ahead), h = 3 (quarter-ahead)
- **4.3 Mixed Data Sampling (MIDAS)**: monthly BENI + quarterly GDP controls (if GDP data available)
- **4.4 Asymmetry analysis**: separate RMSE by inflation regime
- **4.5 Narrative domain decomposition**: which topic drives the forecast improvement?
- **4.6 Inference**: Diebold-Mariano tests with small-sample correction; bootstrap confidence intervals

**5. Results** (~2.5 pages)
- **5.1 BENI vs AR benchmark** (RMSE, MAE, direction accuracy for h=0,1,3)
- **5.2 BENI vs English-language benchmark** (if Google Trends available)
- **5.3 Nowcast vs official release comparison** (figure)
- **5.4 Asymmetric predictive power** (acceleration vs deceleration)
- **5.5 Domain importance** (which narrative topics matter most)

**6. Robustness** (~1 page)
- Alternative BENI specifications: economic_share vs mean_prob
- Alternative model: random forest for nonlinear effects
- Subperiod stability: pre-COVID vs COVID period
- Granger causality tests: does BENI Granger-cause CPI?
- Placebo test: does BENI predict non-economic variables?
- Diebold-Mariano tests with small-sample correction

**7. Discussion** (~1 page)
- Why local-language news matters: captures street-level price anxiety
- Policy implications: monitoring dashboard vs nowcasting model
- Limitations: short sample (36 test months), single country
- Generalizability: template for other South Asian economies

**8. Policy Brief** (~0.5 page)
- Practical dashboard design for central bank monitoring
- Data refresh cadence (weekly score updates)
- Integration with existing nowcasting models

**9. Conclusion** (~0.5 page)

---

## 6. Experimental Design

### Core Models

| Model | Description | Current TF-IDF ΔRMSE vs AR |
|-------|-------------|----------------------------|
| M1: ARIMA | Baseline autoregressive | — |
| M2: ARIMA + BENI aggregate | Add narrative index | h=0: +0.88%, h=3: -0.68% |
| M3: ARIMA + BENI + FX | Add exchange rate control | h=0: larger RMSE, h=3: mixed |
| M4: Random forest (nonlinear) | BENI + FX + AR terms | Does not beat linear AR |

**M2 with BanglaBERT BENI (expected):** -3% to -12% ΔRMSE depending on horizon.

### Nowcast Horizons

| Horizon | Definition | Practical Use |
|---------|------------|---------------|
| h=0 | Same month | Central bank real-time monitoring |
| h=1 | One month ahead | Policy preparation |
| h=3 | Quarter ahead | MPC meeting input |

### Pseudo-Real-Time Protocol
```
For each month t in test period (2018-01 to 2020-12):
  1. Estimate model using data up to month t-1
  2. Produce nowcast for month t (h=0), month t+1 (h=1), month t+3 (h=3)
  3. Record forecast error when actual CPI is released
  4. Update model with new data
This mimics exactly what a central bank would do.
```

### Asymmetry Hypothesis
- BENI should detect **inflation accelerations** better than decelerations
- Rationale: news amplifies price increases (consumer pain stories) but under-reports price stability
- Test: separate RMSE for months where ΔCPI > 0.5% vs ΔCPI < -0.2%

---

## 7. Manuscript Status

| Section | Status | Notes |
|---------|--------|-------|
| 1. Introduction | ✅ Drafted | 1.5 pages — provisional results, policy framing |
| 2. Related Work | ✅ Drafted | 1 page |
| 3. Data | ✅ Drafted | 1.5 pages — will update BENI source after Paper 3 freeze |
| 4. Methods | ✅ Drafted | 2 pages — will add DM tests + MIDAS |
| 5. Results | ✅ Drafted (placeholder) | Uses TF-IDF numbers — swap after freeze |
| 6. Robustness | ❌ Not drafted | Add post-freeze |
| 7. Discussion | ⚠️ Partial | Needs update with final results |
| 8. Policy Brief | ❌ Not drafted | Add post-freeze |
| 9. Conclusion | ✅ Drafted | 0.5 page |

---

## 8. Timeline

```
Paper 3 Freeze (~late July 2026)
    │
    ▼
Pre-Freeze Work (Can Start Now):
    ├── Diebold-Mariano test implementation
    ├── Bootstrap CI implementation
    ├── Google Trends data download (pytrends)
    ├── Quarterly GDP download + MIDAS prep
    └── Food/core CPI data check

Week 1 (Aug 3-7):   Post-freeze re-execution
    ├── Point to Paper 3 BanglaBERT BENI → re-run all models
    ├── Verify results: compare TF-IDF vs BanglaBERT
    ├── Run DM tests + bootstrap CIs
    └── Generate new figures + tables

Week 2 (Aug 10-14):  Additional analyses
    ├── English benchmark comparison (if data ready)
    ├── Food/core CPI nowcasts (if available)
    ├── Narrative domain decomposition
    ├── Granger causality + placebo tests
    └── Draft robustness section

Week 3 (Aug 17-21):  Writing
    ├── Update results section with final numbers
    ├── Draft policy brief (dashboard design)
    └── Revise discussion with final conclusions

Week 4 (Aug 24-28):  Polishing
    ├── Proofread entire manuscript
    ├── Generate publication-quality figures
    ├── Format for target venue
    └── Internal review

Week 5-6 (Aug 31-Sep 11): Submission
    ├── Final proofread + supplementary materials
    ├── arXiv submission
    └── Journal submission
```

**Key insight**: Pre-freeze work is independent of Paper 3. Use the wait time productively — implement DM tests, download Google Trends, prepare MIDAS code.

---

## 9. Target Venues

| Venue | Type | Fit |
|-------|------|-----|
| **International Journal of Forecasting** | Forecasting | Excellent fit for nowcasting methodology |
| **Journal of Development Economics** | Development | Good if framed as developing-economy contribution |
| **Economic Modelling** | Applied | Good for policy-oriented nowcasting models |
| **World Development** | Development | Strong if policy implications are central |

**Recommended first target**: International Journal of Forecasting (best methodological fit for nowcasting)

---

## 10. Required Resources

| Resource | Amount | Status |
|----------|--------|--------|
| BENI index (from Paper 3) | 79 months | ✅ Available (TF-IDF) |
| CPI inflation data | Monthly, 2014-2020 | ✅ Already downloaded |
| Google Trends data | Weekly "Bangladesh inflation" | ⚠️ Need to download (pre-freeze task) |
| MIDAS regression code | ~2 days to implement | ❌ Need to write (pre-freeze task) |
| Diebold-Mariano test code | ~1/2 day | ❌ Need to write (pre-freeze task) |
| Bootstrap CI code | ~1/2 day | ❌ Need to write (pre-freeze task) |
| Quarterly GDP series | Quarterly | ⚠️ Need to download (pre-freeze task) |

---

## 11. Risks (Updated)

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| BanglaBERT BENI does not improve nowcasts | High | Medium | Prototype already shows this possibility. Paper is still publishable — "local-language news has monitoring value but limited nowcast value" is a useful null result |
| Paper 3 delayed → no updated BENI | Medium | Low | Use TF-IDF BENI; clearly state limitation; paper becomes "framework paper" |
| Short sample (36 test months) limits power | Medium | High | Bootstrap CIs + DM tests with small-sample correction |
| Google Trends / GDP data unavailable | Low | Medium | Drop M4/M5; AR+BENI comparison is sufficient for core contribution |

---

## 12. Connection to Papers 3, 5, 6

```
Paper 3 ──frozen BENI index──▶ Paper 4 ──nowcast results──▶ Paper 5
  (pipeline)                       (application)                (synthesis — BENI as case study)

Paper 6 ──LLM narrative extraction──▶ (independent — could cite Paper 3 methods)
```

Paper 4 is the **application paper**. It doesn't depend on Paper 6 and Paper 6 doesn't depend on it. But both Papers 3 and 4 feed into Paper 5 as case studies of the research agenda.
