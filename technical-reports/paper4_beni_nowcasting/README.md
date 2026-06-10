# Paper 4: Nowcasting Inflation with BENI

**Full Title:** Nowcasting Inflation in Bangladesh Using the BENI Narrative Index

**Status:** Planned (Target: August 2026)

---

## Abstract

*This section will be populated as the manuscript develops.*

The paper will evaluate whether the BENI Economic Index — a monthly measure of economic narrative sentiment derived from Bangla-language news — contains predictive content for inflation (CPI) beyond what is captured by traditional econometric models. Using a nowcasting framework, we will assess marginal predictive gains across multiple forecast horizons and discuss the implications for monetary policy in data-scarce environments.

---

## Dependencies

This paper depends on outputs from the following components:

- **BENI Economic Index** — monthly narrative index values (2014–2020) from `pipelines/beni/indices/eco/`
- **Paper 3 — Building BENI Pipeline** — methodology and validation benchmarks that justify the index as a credible input
- **Bangladesh macroeconomic data** — CPI, exchange rate, remittance, and interest rate series (public sources: Bangladesh Bank, BBS)
- **Nowcasting model infrastructure** — the shared time-series library to be placed in `pipelines/shared/`

---

## Contributing

This paper is in the planning stage. Contributions are welcome in the following areas:

- **Nowcasting methodology** — expertise in nowcasting models (MIDAS, bridge equations, dynamic factor models)
- **Macroeconomic data** — assistance sourcing and cleaning Bangladesh macroeconomic time series
- **Literature review** — survey of nowcasting applications in South Asian economies
- **Writing** — drafting or editing manuscript sections

To contribute:

1. Discuss your interest on Discord or via email.
2. Add a row to [`technical-reports/contributions/OWNERS.csv`](../contributions/OWNERS.csv) recording your contribution.
3. Submit a Pull Request with your proposed approach or preliminary results.

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md) for general contribution guidelines and [`COLLABORATION.md`](../../COLLABORATION.md) for authorship and credit policies.
