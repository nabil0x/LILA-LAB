# LILA Lab

## Language Intelligence for Low-resource Applications

### Your language. Your stories. Amplified by AI.

> 84% of NLP research is in English. 56% is US-focused. **0% is Bangla. 0% is Assamese. 0% is Sylheti. 0% is Chittagonian.**
>
> We are building the infrastructure that lets every language participate in the LLM revolution — starting with South Asia.

---

## Repository Structure

This repository is the **central hub** for LILA Lab — a research collective building NLP infrastructure for languages underserved by current AI.

```
lila-lab/
│
├── 📁 pipelines/                    # XENI Pipeline Collection
│   ├── beni/                        # Bangla (active)
│   ├── aeni/                        # Assamese (planned)
│   ├── neni/                        # Nepali (planned)
│   └── shared/                      # Shared utilities
│
├── 📁 technical-reports/                       # Research Papers (6-paper series)
│   ├── paper1_statistical_economics/
│   ├── paper2_systematic_review/
│   ├── paper3_beni_method/
│   ├── paper4_beni_nowcasting/
│   ├── paper5_text_as_data_survey/
│   ├── paper6_llm_narrative_extraction/
│   ├── contributions/               # Contributor records
│   └── extensions/                  # Extension proposals
│
├── 📁 dataset/                      # Datasets
│   ├── beni-v1/                     # BENI v1 dataset
│   ├── raw/                         # Upstream data
│   └── processed/                   # Processed datasets
│
├── 📁 communications/               # Multi-channel command center
│   ├── CHANNELS.md
│   ├── BRAND_GUIDELINES.md
│   ├── SOCIAL_MEDIA_STRATEGY.md
│   ├── COMMUNITY.md
│   ├── CONTENT_CALENDAR.md
│   └── templates/
│
├── 📁 infrastructure/               # Infrastructure & Tools
│   ├── discord-bot/                 # Discord bot
│   ├── website/                     # Website source
│   └── scripts/                     # Utility scripts
│
└── 📁 docs/                         # Documentation
    ├── pipelines/
    ├── research/
    └── assets/
```

---

## Quick Start

### For Linguistic Contributors

```bash
# 1. Read the guide
cat LINGUISTIC_CONTRIBUTION_GUIDE.md

# 2. Check what languages are most needed
ls technical-reports/extensions/INDEX.md

# 3. Register as a contributor
# Use /register command in Discord or email lila.lab0x@gmail.com
```

### For Researchers

```bash
# 1. Explore the BENI pipeline
cd pipelines/beni/

# 2. Run the baseline classifier
python3 experiment/beni_pilot/train.py --task economic --model-type tfidf

# 3. Build the narrative index
python3 experiment/beni_pilot/build_index.py --model-type tfidf
```

### For Developers

```bash
# 1. Set up the Discord bot
cd infrastructure/discord-bot/
cp .env.example .env
pip install -r requirements.txt
python bot.py

# 2. Contribute to the website
cd infrastructure/website/
# Edit index.html, styles.css
```

---

## What We Have Already Built

A complete, production-tested pipeline family. The first XENI pipeline — **BENI** — proves the framework works:

```
Raw Bangla news articles (664,000+)
    → LLM annotation (Claude, GPT-4o ensemble)
    → Multi-model classification (TF-IDF, BanglaBERT)
    → BENI Economic Index (monthly narrative index)
    → Macroeconomic validation (CPI, FX, reserves)
    → Published papers + open-source code
```

**BENI is the pipeline. The BENI Economic Index is its first validated output. The same instrument can now produce health, climate, education, and other domain indices.**

**Proven in Bangla (265M speakers). Ready for your language and domain.**

| Benchmark | Result |
|-----------|--------|
| Classification accuracy | 91.7% (TF-IDF) |
| Monthly index built | 79 months (2014–2020) |
| Level correlation with CPI | r = −0.75 (p < 0.001) |
| Level correlation with FX | r = −0.72 (p < 0.001) |
| Papers published | 2 submitted, 4 in pipeline |

---

## Eight Ways to Contribute

| Contribution Model | What You Do | What You Get |
|--------------------|-------------|--------------|
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

## Communications Center

This repository is the **command center** for LILA Lab's entire multi-channel presence.

| Channel Layer | Channels | Managed In |
|--------------|----------|-----------|
| 🐦 **Social** | X (`@LILA_Lab`), LinkedIn, YouTube, Facebook | [`communications/SOCIAL_MEDIA_STRATEGY.md`](communications/SOCIAL_MEDIA_STRATEGY.md) |
| 📄 **Research** | GitHub, OSF, Zenodo, Hugging Face, arXiv | [`communications/RESEARCH_PLATFORMS.md`](communications/RESEARCH_PLATFORMS.md) |
| 💬 **Community** | Discord, email, monthly lab calls | [`communications/COMMUNITY.md`](communications/COMMUNITY.md) |
| 🎨 **Brand** | LILA+XENI naming, voice, visual identity | [`communications/BRAND_GUIDELINES.md`](communications/BRAND_GUIDELINES.md) |
| 📅 **Calendar** | Scheduled posts, paper releases | [`communications/CONTENT_CALENDAR.md`](communications/CONTENT_CALENDAR.md) |

**→ Full hub:** [`COMMUNICATIONS.md`](COMMUNICATIONS.md)

---

## Research Papers

| Paper | Title | Status |
|-------|-------|--------|
| **1** | Statistical Economics of Narrative | ✅ Complete |
| **2** | Economic Narrative Indices: Systematic Review | ✅ Submitted |
| **3** | Building BENI Pipeline | 🔄 Active (July 2026) |
| **4** | Nowcasting Inflation with BENI | 📋 Planned (Aug 2026) |
| **5** | Text as Data in Social Science | 📋 Planned (Oct 2026) |
| **6** | LLMs as Measurement Devices | 💡 Proposed (Jan 2027) |

**→ Full details:** [`technical-reports/README.md`](technical-reports/README.md)

---

## Data Sources

| Dataset | Language | Size | License |
|---------|----------|------|---------|
| Potrika Bangla News | Bangla | 3.3 GB | CC BY 4.0 |
| BENI v1 | Bangla | — | CC BY 4.0 |

**YOUR LANGUAGE HERE** — submit via the linguistic contribution guide.

---

## Contact

**Maintainer:** Ann Naser Nabil — Department of Economics, Jahangirnagar University

- Email: lila.lab0x@gmail.com
- ORCID: [0009-0006-3561-045X](https://orcid.org/0009-0006-3561-045X)
- GitHub: [nabil0x](https://github.com/nabil0x)
- Discord: [discord.gg/TrrdKbky](https://discord.gg/TrrdKbky)

---

## License

- **Code**: MIT License
- **Data**: CC BY 4.0 (unless otherwise specified)
- **Papers**: © Ann Naser Nabil
- **Contributions**: Attributed to contributor, shared under CC BY 4.0
