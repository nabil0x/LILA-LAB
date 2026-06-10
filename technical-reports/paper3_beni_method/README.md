# Paper 3: Building BENI Pipeline

**Full Title:** Building the BENI Pipeline: A Reproducible Framework for Narrative Index Construction in Low-Resource Languages

**Status:** Active (Target: July 2026)

---

## Abstract

*This section will be populated as the manuscript develops.*

The paper will provide a comprehensive methodological account of the BENI (Bangla Exploration & Native-language Intelligence) pipeline, covering the complete workflow from raw news article collection through LLM annotation, classifier training, and monthly narrative index construction. It is designed to serve as both a research output and an implementation guide for researchers extending the pipeline to new languages or domains.

---

## Dependencies

This paper depends on outputs from the following components:

- **BENI pilot experiment** — model artifacts, index data, and evaluation results in `pipelines/beni/experiment/beni_pilot/`
- **BENI annotation pipeline** — LLM annotation schemas, adjudication protocols, and labeled data in `pipelines/beni/annotation/`
- **BENI Economic Index** — monthly index values and macroeconomic correlation results (CPI, FX, reserves)
- **Potrika dataset** — 664,000+ Bangla news articles (Mendeley Data, CC BY 4.0)
- **Shared pipeline library** — language-agnostic utilities in `pipelines/shared/`

---

## Contributing

This paper is an active project. Contributions are welcome in the following areas:

- **Methodology review** — feedback on pipeline design and validation strategy
- **Replication** — independent verification of classification and index construction results
- **Writing** — drafting or editing manuscript sections
- **Visualization** — figures, tables, and interactive index displays

To contribute:

1. Review the open tasks in this directory.
2. Add a row to [`technical-reports/contributions/OWNERS.csv`](../contributions/OWNERS.csv) recording your contribution.
3. Submit a Pull Request with your changes.

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md) for general contribution guidelines and [`COLLABORATION.md`](../../COLLABORATION.md) for authorship and credit policies.
