# Technical Reports — LILA Lab Paper Series

This directory contains the complete 6-paper research series produced by LILA Lab. The series documents the design, construction, validation, and application of the XENI pipeline framework for generating narrative indices from low-resource language news corpora. Each paper builds on the preceding ones, forming a coherent arc from foundational methodology to downstream applications.

---

## Paper Series Overview

| Paper | Title | Status | Target |
|-------|-------|--------|--------|
| 1 | Statistical Economics of Narrative | Complete | Published |
| 2 | Economic Narrative Indices: Systematic Review | Submitted | Journal |
| 3 | Building BENI Pipeline | Active (Jul 2026) | Journal |
| 4 | Nowcasting Inflation with BENI | Planned (Aug 2026) | Journal |
| 5 | Text as Data in Social Science: A Survey | Planned (Oct 2026) | Survey |
| 6 | LLMs as Measurement Devices | Proposed (Jan 2027) | Journal |

### Paper 1 — Statistical Economics of Narrative
Foundational paper establishing the theoretical framework for measuring economic narratives in low-resource languages. Introduces the BENI pipeline architecture and validates the BENI Economic Index against macroeconomic indicators (CPI, FX, reserves). Establishes the correlation methodology that later papers extend and refine.

### Paper 2 — Economic Narrative Indices: Systematic Review
Systematic literature review of economic narrative index construction across all languages. Maps the methodological landscape — dictionary-based, supervised ML, and LLM-based approaches — and positions the XENI framework within the broader literature. Identifies gaps that the remaining papers address.

### Paper 3 — Building BENI Pipeline
Detailed methodological paper describing the end-to-end BENI pipeline: corpus assembly (664,000+ Bangla news articles), LLM annotation protocol (Claude + GPT-4o ensemble), classifier training (TF-IDF, BanglaBERT), and index construction. Serves as the implementation guide for extending the pipeline to new languages.

### Paper 4 — Nowcasting Inflation with BENI
Applied paper using the BENI Economic Index to nowcast inflation in Bangladesh. Evaluates the marginal predictive content of narrative data relative to traditional macroeconomic models. Demonstrates practical value for policy in data-scarce environments.

### Paper 5 — Text as Data in Social Science: A Survey
Synthesis survey covering the use of text-as-data methods across economics, political science, and sociology, with emphasis on applications in low-resource language settings. Draws on findings from Papers 1–4 to chart a research agenda for multilingual narrative measurement.

### Paper 6 — LLMs as Measurement Devices
Forward-looking paper examining the reliability, validity, and biases of LLM-based annotation for social science measurement. Proposes best practices and benchmarks for using LLMs as measurement instruments in low-resource contexts.

---

## How the Papers Relate to the BENI Pipeline

All six papers are unified by their connection to the BENI (Bangla Exploration & Native-language Intelligence) pipeline:

- **Papers 1–2** establish the theoretical and empirical foundation: can economic narratives be measured in a low-resource language, and where does this fit in the existing literature?
- **Paper 3** documents the engineering and methodology behind the pipeline itself — the "how" that researchers need to replicate or extend the work.
- **Paper 4** demonstrates a concrete application: using the narrative index to nowcast a real macroeconomic variable (inflation).
- **Paper 5** steps back to survey the broader field, situating the BENI approach within the full text-as-data landscape.
- **Paper 6** looks ahead to the methodological frontier — LLMs as measurement devices — which will shape the next generation of XENI pipelines.

---

## Directory Structure

```
technical-reports/
├── README.md                         # This file
├── extensions/                       # Language and domain extension proposals
│   ├── INDEX.md                      # Registry of active extensions
│   ├── EXTENSION_TEMPLATE.md         # Template for proposing a new extension
│   └── REPLICATION_TEMPLATE.md       # Template for replication reports
├── contributions/                    # Contribution tracking
│   └── OWNERS.csv                    # Who owns what
├── paper1_*/                         # Paper 1 materials (to be populated)
├── paper2_*/                         # Paper 2 materials (to be populated)
├── paper3_beni_method/               # Paper 3 materials
├── paper4_beni_nowcasting/           # Paper 4 materials
├── paper5_text_as_data_survey/       # Paper 5 materials
└── paper6_*/                         # Paper 6 materials (to be populated)
```

Paper directories with an asterisk will be created as the corresponding papers progress through their research lifecycle.

---

## Using These Reports

- **Researchers**: Each paper directory contains the manuscript, figures, data references, and replication code.
- **Contributors**: See [extensions/INDEX.md](extensions/INDEX.md) for active extension opportunities, and [contributions/OWNERS.csv](contributions/OWNERS.csv) to record your participation.
- **Reviewers**: Replication reports can be submitted using the [REPLICATION_TEMPLATE.md](extensions/REPLICATION_TEMPLATE.md).

---

## Citation

For the overall project:

```bibtex
@software{lila_lab,
  author = {Nabil, Ann Naser and others},
  title = {LILA Lab: Language Intelligence for Low-resource Applications},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/LilaLABx/LILA-LAB}
}
```

Individual paper citations will be added to each paper's README as they are published.
