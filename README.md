# LILA Lab

**Language Intelligence for Low-resource Applications**

Your language. Your stories. Amplified by AI.

> 84% of NLP research is in English. 56% is US-focused. **0% is Bangla. 0% is Assamese. 0% is Sylheti. 0% is Chittagonian.**
>
> We are building the infrastructure that lets every language participate in the LLM revolution — starting with South Asia.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](./LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![Discord](https://img.shields.io/badge/discord-join-7289DA?logo=discord)](https://discord.gg/TrrdKbky)

---

## Table of Contents

- [What Is LILA Lab?](#what-is-lila-lab)
- [The XENI Pipeline Framework](#the-xeni-pipeline-framework)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [For Researchers](#for-researchers)
  - [For Linguistic Contributors](#for-linguistic-contributors)
  - [For Developers](#for-developers)
- [Repository Overview](#repository-overview)
- [Project Status & Results](#project-status--results)
- [How to Contribute](#how-to-contribute)
- [How to Cite](#how-to-cite)
- [Community & Contact](#community--contact)
- [License](#license)

---

## What Is LILA Lab?

LILA Lab is a research collective building **open-source NLP pipelines** that let any low-resource language participate in the LLM revolution. We don't just talk about multilingual AI — we build the infrastructure for it.

Our first pipeline, **BENI** (Bangla Exploration & Native-language Intelligence), is proven and production-tested:

```
Raw Bangla news articles (664,000+)
    → LLM annotation (Claude, GPT-4o ensemble)
    → Multi-model classification (TF-IDF, BanglaBERT)
    → BENI Economic Index (monthly narrative index)
    → Macroeconomic validation (CPI, FX, reserves)
    → Published papers + open-source code
```

**Proven in Bangla (265M speakers). Ready for your language and domain.**

---

## The XENI Pipeline Framework

**XENI** stands for **[Language initial] + Exploration & Native-language Intelligence**. Each language gets its own pipeline that collects native-language news, classifies narratives across domains, and produces validated monthly indices.

Every XENI pipeline follows the same structure:

```
[x]eni/
├── annotation/          # LLM annotation pipeline (domain-agnostic)
│   ├── schemas/         # Per-domain annotation schemas
│   ├── llm_annotate.py  # Multi-LLM annotation (Claude, GPT-4o, ...)
│   └── adjudicate.py    # Resolve annotation disagreements
├── indices/             # Index construction — one subdirectory per domain
│   ├── eco/             # Economic narrative index
│   │   ├── build_index.py
│   │   └── validate.py  # Validate against CPI, FX, etc.
│   └── health/          # (planned)
├── experiment/          # Model training & evaluation
├── database/            # Data storage
└── data/                # Pipeline-specific data
```

| Element | Convention | Example |
|---------|-----------|---------|
| **Pipeline** | XENI (language initial + ENI) | BENI, AENI, NENI |
| **Index** | XENI [Domain] Index | BENI Economic Index |

A single pipeline can produce many domain indices. BENI's first index happens to be economic — the same instrument can measure health, climate, or education narratives.

**Active pipelines:**

| Pipeline | Language | Speakers | Status |
|----------|----------|----------|--------|
| **BENI** | Bangla (বাংলা) | 265M | ✅ Active |
| **AENI** | Assamese (অসমীয়া) | 15M | 🔜 Seeking contributors |
| **NENI** | Nepali (नेपाली) | 25M | 🔜 Seeking contributors |
| **SENI** | Sylheti (চিটাঙ্গ) | 11M | 🔜 Planned |
| **CENI** | Chittagonian (চাঁটগাঁইয়া) | 16M | 🔜 Planned |

**Don't see your language?** [Start a new pipeline.](#how-to-contribute)

---

## Prerequisites

- **Python 3.10+** — the entire pipeline ecosystem targets 3.10+
- **Git** — for cloning and contributing
- **pip** — Python package manager
- **Optional:** A Discord account if you want to [join the community](https://discord.gg/TrrdKbky)

For LLM annotation (Claude, GPT-4o), you'll need API keys from [Anthropic](https://console.anthropic.com/) and/or [OpenAI](https://platform.openai.com/). The pipeline gracefully degrades — you can still run classification and index construction without them.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/LilaLABx/LILA-LAB.git
cd LILA-LAB
```

### 2. Install core dependencies

```bash
pip install -e ".[core]"
```

This installs the shared pipeline library (`pandas`, `scikit-learn`, `numpy`, etc.) defined in [`pyproject.toml`](pyproject.toml).

### 3. (Optional) Install LLM annotation extras

```bash
pip install -e ".[llm]"      # For running LLM annotation (Claude, GPT)
pip install -e ".[dev]"      # For development (ruff, pytest)
pip install -e ".[all]"      # Everything above
```

### 4. (Optional) Install BENI pilot experiment dependencies

```bash
cd pipelines/beni/experiment/beni_pilot
pip install -r requirements.txt
cd ../../..
```

This adds `torch`, `transformers`, `streamlit`, and other experiment-specific packages.

---

## Quick Start

### For Researchers

Run the BENI pilot baseline — from clone to narrative index in a few commands:

```bash
# 1. Install dependencies (see Installation section above)

# 2. Train the baseline TF-IDF classifier
cd pipelines/beni/experiment/beni_pilot
python3 train.py --task economic --model-type tfidf --data-source potrika-timeseries

# 3. Build the 79-month BENI Economic Index
python3 build_index.py

# 4. Correlate with macroeconomic indicators (CPI, FX, reserves)
python3 correlate.py
```

**What you'll get:** A monthly narrative index (2014–2020), model artifacts, and correlation reports. See [`pipelines/beni/experiment/beni_pilot/README.md`](pipelines/beni/experiment/beni_pilot/README.md) for full documentation.

**Need the Potrika dataset?** Download it from [Mendeley Data](https://data.mendeley.com/datasets/v362rp78dc/4) (3.3 GB, CC BY 4.0) and place it in `pipelines/beni/data/raw/potrika/`.

### For Linguistic Contributors

Want to bring the XENI pipeline to your language?

```bash
# 1. Read the contribution guide
cat LINGUISTIC_CONTRIBUTION_GUIDE.md

# 2. Check which languages are most needed
cat technical-reports/extensions/INDEX.md

# 3. Register as a contributor
# Use /register in Discord or email lila.lab0x@gmail.com
```

**No coding required.** We need native speakers for annotation, schema design, and language expertise.

### For Developers

```bash
# 1. Set up the Discord bot
cd infrastructure/discord-bot/
cp .env.example .env
# Edit .env with your bot token
pip install -r requirements.txt
python bot.py

# 2. Work on the website
cd infrastructure/website/
# Files: dashboard.html, dashboard-styles.css, dashboard.js
# Open dashboard.html in a browser to preview
```

---

## Repository Overview

```
lila-lab/
├── pipelines/                  # XENI Pipeline Collection
│   ├── beni/                   # Bangla (active — proven pipeline)
│   ├── aeni/                   # Assamese (planned)
│   ├── neni/                   # Nepali (planned)
│   ├── seni/                   # Sylheti (planned)
│   ├── ceni/                   # Chittagonian (planned)
│   ├── template/               # Pipeline template (start here for new languages)
│   └── shared/                 # Language-agnostic utilities (LLM, stats, config)
│
├── technical-reports/          # Research Papers (6-paper series)
│   ├── paper1_.../
│   ├── paper2_.../
│   ├── paper3_.../
│   ├── paper4_.../
│   ├── paper5_.../
│   ├── paper6_.../
│   ├── contributions/          # Contributor records
│   └── extensions/             # Extension proposals
│
├── dataset/                    # Datasets
├── communications/             # Brand, social media, community strategy
├── infrastructure/             # Discord bot, website, scripts
└── docs/                       # Documentation
```

**Key entry points:**
- [`pipelines/README.md`](pipelines/README.md) — full pipeline framework documentation
- [`pipelines/beni/README.md`](pipelines/beni/README.md) — BENI deep dive
- [`pipelines/beni/experiment/beni_pilot/README.md`](pipelines/beni/experiment/beni_pilot/README.md) — pilot experiment commands & results
- [`COLLABORATION.md`](COLLABORATION.md) — full contribution framework
- [`LINGUISTIC_CONTRIBUTION_GUIDE.md`](LINGUISTIC_CONTRIBUTION_GUIDE.md) — guide for language contributors

---

## Project Status & Results

### BENI Benchmark

| Metric | Result |
|--------|--------|
| Classification accuracy | 91.7% (TF-IDF) |
| Monthly index built | 79 months (2014–2020) |
| Level correlation with CPI | r = −0.75 (p < 0.001) |
| Level correlation with FX | r = −0.72 (p < 0.001) |
| Papers published | 2 submitted, 4 in pipeline |

### Paper Series

| Paper | Title | Status |
|-------|-------|--------|
| 1 | Statistical Economics of Narrative | ✅ Complete |
| 2 | Economic Narrative Indices: Systematic Review | ✅ Submitted |
| 3 | Building BENI Pipeline | 🔄 Active (July 2026) |
| 4 | Nowcasting Inflation with BENI | 📋 Planned (Aug 2026) |
| 5 | Text as Data in Social Science | 📋 Planned (Oct 2026) |
| 6 | LLMs as Measurement Devices | 💡 Proposed (Jan 2027) |

**Full details:** [`technical-reports/README.md`](technical-reports/README.md)

---

## How to Contribute

| Model | What You Do | What You Get |
|-------|-------------|--------------|
| 🌍 **Language Extension** | Apply the pipeline to YOUR language | First-author paper |
| 🔬 **Cross-Domain Extension** | Apply to health, climate, education | First-author paper |
| ⚙️ **Methodological** | Improve classifier, reduce cost | Co-authorship |
| ✅ **Replication** | Independently verify results | Replication report |
| 🗣️ **Citizen Annotation** | Label articles in your language | Acknowledgment |
| 📊 **Policy Brief** | Analyze narratives for policy | Co-authorship |
| 🛠️ **Infrastructure** | Build dashboards, APIs, tools | Tool paper co-authorship |
| 📖 **Education** | Create tutorials, course modules | Educational paper |

**→ Full framework:** [`COLLABORATION.md`](COLLABORATION.md)

---

## How to Cite

If you use LILA Lab pipelines or data in your research:

```bibtex
@software{lila_lab,
  author = {Nabil, Ann Naser and others},
  title = {LILA Lab: Language Intelligence for Low-resource Applications},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/LilaLABx/LILA-LAB}
}
```

For individual papers in the series, see [`technical-reports/README.md`](technical-reports/README.md) for specific citations.

---

## Community & Contact

- **Discord:** [discord.gg/TrrdKbky](https://discord.gg/TrrdKbky) — Ask questions, find collaborators, get help
- **Email:** [lila.lab0x@gmail.com](mailto:lila.lab0x@gmail.com) — Formal inquiries and partnerships
- **GitHub Issues:** [Open an issue](https://github.com/LilaLABx/LILA-LAB/issues) — Bug reports, feature requests, language proposals
- **X (Twitter):** [@LILA_Lab](https://x.com/LILA_Lab)
- **Website:** [lilalab.pro.bd](https://lilalab.pro.bd/)

**Maintainer:** Ann Naser Nabil — Department of Economics, Jahangirnagar University ([ORCID](https://orcid.org/0009-0006-3561-045X))

---

## License

- **Code:** MIT License — Use, modify, distribute freely
- **Data:** CC BY 4.0 — Attribute the source
- **Papers:** © Ann Naser Nabil
- **Contributions:** Attributed to contributor, shared under CC BY 4.0

---

**Your language is underserved by current AI. Let's change that — together.**
