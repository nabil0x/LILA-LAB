# Frequently Asked Questions

> New to LILA Lab? Start here. This covers everything from installation to contributing to citing our work.

---

## How do I install the pipeline?

Clone the repository and install the core dependencies:

```bash
git clone https://github.com/LilaLABx/LILA-LAB.git
cd LILA-LAB
pip install -e ".[core]"
```

You need **Python 3.10 or later**. It is strongly recommended to use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[core]"
```

Optional extras:
- `pip install -e ".[llm]"` for LLM annotation (Claude, GPT)
- `pip install -e ".[dev]"` for development (ruff, pytest)
- `pip install -e ".[all]"` for everything

If you are running the BENI pilot experiment, install its additional dependencies separately:

```bash
cd pipelines/beni/experiment/beni_pilot
pip install -r requirements.txt
```

See the [README](README.md#installation) for full installation instructions.

---

## How do I get API keys for LLM annotation?

The BENI pipeline uses an ensemble of Claude (Anthropic) and GPT-4o (OpenAI). You need API keys from both services to run LLM annotation:

- **Anthropic (Claude):** Sign up at [console.anthropic.com](https://console.anthropic.com/). You get some free credits on signup, then pay per token.
- **OpenAI (GPT-4o):** Sign up at [platform.openai.com](https://platform.openai.com/). Add a payment method and generate an API key.

Set them as environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-proj-..."
```

Or create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
```

The pipeline degrades gracefully. You can still run classification and index construction without API keys. See [`pipelines/beni/annotation/llm_annotate.py`](pipelines/beni/annotation/llm_annotate.py).

---

## What Python version do I need?

Python 3.10 or later. The project targets 3.10+ across all pipelines. Older versions are not supported.

---

## Where do I download the Potrika dataset?

The Potrika Bangla news corpus is hosted on Mendeley Data:

- **DOI:** [10.17632/v362rp78dc.4](https://data.mendeley.com/datasets/v362rp78dc/4)
- **Size:** 3.3 GB (39 CSV files)
- **License:** CC BY 4.0 (attribution required)
- **Period:** 2014 to 2020
- **Sources:** Jugantor, Ittefaq, Kaler Kontho, Inqilab, Jaijaidin, Somoyer Alo

After downloading, place the files in `pipelines/beni/data/raw/potrika/`. The pipeline expects them there.

---

## Can I contribute without coding?

Yes. Linguistic contributors are essential to the project and do not need to write code.

You can contribute by:
- **Submitting text data** in your native language (plain text or CSV)
- **Annotating articles** as "Economic" or "Not Economic" using your cultural and linguistic knowledge
- **Designing annotation schemas** that capture how economic narratives work in your language
- **Validating LLM outputs** by reviewing and correcting labels produced by the automated pipeline
- **Documenting dialectal variants**, idioms, and culturally specific expressions

All contributions are recorded in [`technical-reports/contributions/OWNERS.csv`](technical-reports/contributions/OWNERS.csv) and lead to co-authorship or acknowledgement in publications.

See the [Linguistic Contribution Guide](LINGUISTIC_CONTRIBUTION_GUIDE.md) and the [Collaboration Framework](COLLABORATION.md) for details.

---

## How do I set up the Discord bot?

The Discord bot lives in `infrastructure/discord-bot/`. To set it up:

```bash
cd infrastructure/discord-bot/
cp .env.example .env
```

Edit `.env` with your bot token (get one from the [Discord Developer Portal](https://discord.com/developers/applications)):

```
DISCORD_BOT_TOKEN=your_token_here
```

Then install and run:

```bash
pip install -r requirements.txt
python bot.py
```

The bot handles community registration, contributor tracking, and project notifications. See the [README](README.md#for-developers) for more.

---

## How do I train a model for my language?

The XENI pipeline is designed to be language-agnostic. To train a model for a new language:

1. **Copy the template:** `cp -r pipelines/template/ pipelines/[your-lang]/`
2. **Collect data:** Gather at least 1,000 news articles in your language
3. **Define a schema:** Adapt [`pipelines/beni/annotation/ANNOTATION_SCHEMA.md`](pipelines/beni/annotation/ANNOTATION_SCHEMA.md) for your domain
4. **Annotate:** Use the LLM annotation scripts or Label Studio for human annotation
5. **Train:** Run `train.py --model-type tfidf --data-source your-data`
6. **Build your index:** Run `build_index.py`
7. **Validate:** Compare against real-world indicators

The [`pipelines/template/`](pipelines/template/) directory has everything you need to start. See the [Linguistic Contribution Guide](LINGUISTIC_CONTRIBUTION_GUIDE.md) for data submission instructions.

---

## How do I cite LILA Lab?

To cite the overall project:

```bibtex
@software{lila_lab,
  author = {Nabil, Ann Naser and others},
  title = {LILA Lab: Language Intelligence for Low-resource Applications},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/LilaLABx/LILA-LAB}
}
```

For individual papers in the 6-paper series, see [`technical-reports/README.md`](technical-reports/README.md) for specific citations. To cite the Potrika dataset:

```bibtex
@dataset{potrika_bangla_news,
  author = {Hasan, Md. Arid},
  title = {Potrika: Bangla News Corpus},
  doi = {10.17632/v362rp78dc.4},
  publisher = {Mendeley Data},
  year = {2023}
}
```

For the LILA-BENI dataset:

```bibtex
@dataset{lila_beni_v1,
  author = {Nabil, Ann Naser},
  title = {LILA-BENI v1.0: A Harmonised Bangla News Dataset for Economic Narrative Measurement},
  doi = {10.5281/zenodo.20585401},
  year = {2026}
}
```

---

## Where are the research papers?

LILA Lab is producing a 6-paper technical report series, all available in [`technical-reports/`](technical-reports/):

| Paper | Title | Status |
|-------|-------|--------|
| 1 | Statistical Economics of Narrative | Complete |
| 2 | Economic Narrative Indices: Systematic Review | Submitted |
| 3 | Building BENI Pipeline | Active (July 2026) |
| 4 | Nowcasting Inflation with BENI | Planned (Aug 2026) |
| 5 | Text as Data in Social Science | Planned (Oct 2026) |
| 6 | LLMs as Measurement Devices | Proposed (Jan 2027) |

Papers 1-2 are complete or submitted. Papers 3-4 are in active development. Papers 5-6 are planned.

---

## Who maintains this project?

**Ann Naser Nabil**, Department of Economics, Jahangirnagar University, maintains the project. Contact via:

- **Email:** [lila.lab0x@gmail.com](mailto:lila.lab0x@gmail.com)
- **ORCID:** [0009-0006-3561-045X](https://orcid.org/0009-0006-3561-045X)
- **Discord:** [discord.gg/TrrdKbky](https://discord.gg/TrrdKbky)
- **X (Twitter):** [@LILA_Lab](https://x.com/LILA_Lab)

The project is a research collective, not a company. Contributions come from researchers, linguistic experts, and developers worldwide.

---

## What is a XENI pipeline?

XENI stands for **[Language initial] + Exploration & Native-language Intelligence**. It is the naming convention for every language-specific NLP pipeline in LILA Lab. For example:

- **BENI** = Bangla XENI
- **AENI** = Assamese XENI
- **NENI** = Nepali XENI

Each XENI pipeline collects native-language news, annotates articles using an LLM ensemble, trains a classifier, constructs a monthly narrative index, and validates the index against real-world indicators. The full framework is documented in [`pipelines/README.md`](pipelines/README.md).

---

## How do I start a new pipeline for my language?

See the [Collaboration Framework](COLLABORATION.md) for the full process. In short:

1. **Check priorities:** Assamese (AENI), Nepali (NENI), Sylheti (SENI), and Chittagonian (CENI) are most needed
2. **Copy the template:** `cp -r pipelines/template/ pipelines/[your-lang]/`
3. **Collect at least 1,000 articles** in your language
4. **Register your intent:** Add a row to `technical-reports/contributions/OWNERS.csv`
5. **Open an issue** or email lila.lab0x@gmail.com to coordinate

We provide templates, code, mentorship, and co-authorship opportunities.

---

## What's the difference between a pipeline and an index?

A **pipeline** (the XENI) is the full instrument: the code, data, and models for a language. An **index** is a specific output of that pipeline, measuring narratives in one domain.

BENI (the Bangla pipeline) produces one index today (the BENI Economic Index), but can produce many more: a BENI Health Index, a BENI Climate Index, and so on. Each domain just needs its own annotation schema.

---

## Do I need a GPU to run the pipeline?

For the TF-IDF baseline and index construction, no. A standard laptop is sufficient. The TF-IDF model trains in minutes on CPU.

For BanglaBERT fine-tuning, a GPU is recommended. The full 70,000-article, 3-epoch training run is scheduled for Kaggle (T4 or P100 GPU, roughly 2-3 hours). The code supports fp16 mixed precision and can run on 6 GB GPUs with batch size 4.

---

## How is the narrative index calculated?

The index is built in two steps. First, the trained classifier predicts an "economic probability" for each article in the corpus. Second, articles are grouped by month, and the index is the proportion of articles with probability above 0.5. The result is a monthly time series showing the share of economic news in the language's media.

The BENI Economic Index contains 79 monthly observations from June 2014 to December 2020, with a mean economic news share of 38.9%. See [`pipelines/beni/experiment/beni_pilot/README.md`](pipelines/beni/experiment/beni_pilot/README.md).

---

## How are LLM annotations adjudicated?

Each article is annotated independently by multiple LLMs (Claude and GPT-4o). When the models disagree, adjudication uses majority voting. If there is a tie, the higher-confidence label wins. The adjudicated labels become the ground truth for classifier training.

The ensemble approach improves label reliability and provides natural confidence estimates. See [`pipelines/beni/annotation/adjudicate.py`](pipelines/beni/annotation/adjudicate.py) and the [annotation schema](pipelines/beni/annotation/ANNOTATION_SCHEMA.md).

---

## What are the key results so far?

- **Classification accuracy:** 91.7% (TF-IDF + logistic regression)
- **Narrative index:** 79 months, mean economic share 38.9%
- **Level correlation with CPI:** r = -0.75 (p < 0.001)
- **Level correlation with BDT/USD FX:** r = -0.72 (p < 0.001)
- **Level correlation with reserves:** r = -0.77 (p < 0.05)
- **Papers:** 2 complete, 4 in the pipeline

Month-to-month (detrended) correlations are near zero, suggesting the TF-IDF index captures long-run structural shifts but not short-term noise. The BanglaBERT upgrade may improve short-run signal.

---

## What license applies to the code and data?

- **Code:** MIT License. Use, modify, and distribute freely.
- **Data:** CC BY 4.0. Attribute the source.
- **Papers:** Copyright Ann Naser Nabil.
- **Contributions:** Attributed to the contributor, shared under CC BY 4.0.

Linguistic contributors retain ownership of their language data and choose the license.

---

## How can I stay updated on the project?

- **Discord:** [discord.gg/TrrdKbky](https://discord.gg/TrrdKbky) for community discussions
- **X (Twitter):** [@LILA_Lab](https://x.com/LILA_Lab) for announcements
- **GitHub:** Watch and star the [repository](https://github.com/LilaLABx/LILA-LAB)
- **Website:** [lilalab.pro.bd](https://lilalab.pro.bd/) for the dashboard and visualizations

---

## I found a bug or have a feature request. Where do I report it?

Open a GitHub Issue at [github.com/LilaLABx/LILA-LAB/issues](https://github.com/LilaLABx/LILA-LAB/issues). For sensitive matters, email lila.lab0x@gmail.com directly.
