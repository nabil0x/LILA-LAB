# LILA Lab — Distribution Strategy & Funnel

> This document is part of the LILA Lab Communications Center (`communications/`). For the full multi-channel strategy including social media, community, and brand guidelines, see [`COMMUNICATIONS.md`](COMMUNICATIONS.md).

**Goal**: Turn a 56 GB monolithic research repo into a strategic multi-platform distribution system that creates a **citation funnel** — discover → engage → cite.

---

## The Full Funnel Architecture

```
                          ╔══════════════════════════════════════╗
                          ║       AWARENESS (Top of Funnel)      ║
                          ║  Social media + community channels   ║
                          ║  drive discovery of research output  ║
                          ╚══════════════╦═══════════════════════╝
                                         ║
                          ╔══════════════╩═══════════════════════╗
                          ║  SOCIAL MEDIA & COMMUNITY            ║
                          ║  X (@LILA_Lab) | LinkedIn | YouTube  ║
                          ║  Facebook | Discord | Substack       ║
                          ║  ──→ Full strategy in                ║
                          ║     communications/SOCIAL_MEDIA_     ║
                          ║     STRATEGY.md                       ║
                          ╚══════════════╦═══════════════════════╝
                                         ║
                                         ▼
                      ┌──────────────────────────────────────┐
                      │         DISCOVERY (Research-Facing)   │
                      │  "I need to measure economic news     │
                      │   in a low-resource language"         │
                      └──────────────┬───────────────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ▼                        ▼                        ▼
    ┌──────────────┐       ┌──────────────────┐     ┌────────────────┐
    │  Hugging Face │       │      OSF         │     │   Mendeley     │
    │  (NLP people) │◄─────►│  (Open Science)  │◄───►│  (Data people) │
    │  models/      │       │  project hub     │     │  raw corpus    │
    │  datasets/    │       │  preprints       │     │  DOI           │
    │  spaces demo  │       │  protocols       │     └────────────────┘
    └──────┬───────┘       └────────┬─────────┘
           │                        │
           └──────────┬─────────────┘
                      ▼
            ┌──────────────────┐
            │  ENGAGEMENT       │
            │  (Middle of Funnel)│
            │  "I want to use   │
            │   this data/code" │
            └────────┬─────────┘
                     │
            ┌────────▼─────────┐
            │     Zenodo        │
            │  DOI for: datasets│
            │  code releases,   │
            │  paper preprints  │
            └────────┬─────────┘
                     │
            ┌────────▼─────────┐
            │     GitHub        │
            │  code of record   │
            │  source of truth  │
            │  communications/  │
            │  collaboration    │
            └────────┬─────────┘
                     │
                      ▼
            ┌──────────────────┐
            │  CITATION         │
            │ (Bottom of Funnel)│
            │ Technical Reports │
            │ 1→6 cited         │
            │ DOI on everything │
            └──────────────────┘
```

> **New: Social & community layer** — The original funnel started at research platforms. The full funnel now starts with social media driving awareness → directing to research platforms → engagement → citation.

---

## Relation to the Communications Hub

This document focuses on **research platform distribution** (OSF, Zenodo, Hugging Face, Mendeley, arXiv, GitHub). For the broader multi-channel strategy including social media, community, brand, and content calendar, see:

| Document | Purpose |
|----------|---------|
| [`COMMUNICATIONS.md`](COMMUNICATIONS.md) | Hub entry point |
| [`communications/CHANNELS.md`](communications/CHANNELS.md) | Complete 15+ channel inventory |
| [`communications/SOCIAL_MEDIA_STRATEGY.md`](communications/SOCIAL_MEDIA_STRATEGY.md) | X, LinkedIn, YouTube plans |
| [`communications/COMMUNITY.md`](communications/COMMUNITY.md) | Discord, contributor coordination |
| [`communications/BRAND_GUIDELINES.md`](communications/BRAND_GUIDELINES.md) | LILA+XENI naming and identity |

---

## Platform Roles & Responsibilities

### 1. OSF (Open Science Framework) — Project Hub
**Role**: The front door. One OSF project page that links to everything else.

**What goes here**:
- **Project overview** — research program description, 6-paper arc, dependency DAG
- **Preprints** — PDF + TeX for ALL papers (Paper 1 through 6, plus BENI data paper)
- **Supplementary materials** — all figures, annotation protocols, dataset cards
- **Links to** — GitHub repo, Zenodo DOIs, Hugging Face models, Mendeley Data

**Structure**:
```
LILA Lab (OSF Project)
├── Components:
│   ├── Paper 1: Statistical Economics (preprint)
│   ├── Paper 2: Systematic Review (preprint)
│   ├── Paper 3: BENI Pipeline (preprint)
│   ├── Paper 4: BENI Nowcasting (preprint)
│   ├── Paper 5: Text as Data Survey (preprint)
│   ├── Paper 6: LLM Narrative Extraction (preprint)
│   └── BENI v1.0 Data Paper (preprint + data supplement)
├── Files:
│   ├── figures/ (all publication figures)
│   ├── protocols/ (annotation schema, guide, adjudication protocol)
│   ├── dataset_cards/ (DATASET_CARD.md, FILE_SCHEMA.md)
│   └── README.md
└── Links:
    ├── GitHub: https://github.com/nabil0x/LILA-LAB
    ├── Zenodo: 10.5281/zenodo.20585401
    ├── HF: hf.co/nabil0x/beni-banglabert
    └── Mendeley: 10.17632/v362rp78dc.4
```

### 2. Hugging Face — NLP Community Hub
**Role**: Where NLP researchers discover the work. Models + dataset + demo space.

**What goes here**:
- **Models**: Fine-tuned BanglaBERT models (best-per-k from active learning experiments)
- **Dataset**: BENI narrative index (as HF Dataset)
- **Space**: Gradio demo for classifying Bangla news as Economic/Not Economic
- **Links to**: GitHub, OSF, Zenodo DOIs

**Structure**:
```
huggingface.co/nabilox/
├── beni-banglabert/              # Model card
│   ├── README.md (model card)
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer files
├── beni-narrative-index/          # Dataset card
│   ├── README.md (dataset card)
│   └── data files
└── beni-classifier-demo/          # Gradio Space
    ├── app.py
    ├── requirements.txt
    └── README.md
```

### 3. Zenodo — DOI for Everything
**Role**: Get DOIs on datasets, code, and preprints. GitHub integration auto-archives releases.

**What goes here**:
- **Dataset release v1.0**: All index CSVs, gold-standard JSONL, annotations, systematic review database
- **Code releases**: Each GitHub release triggers Zenodo DOI
- **Links to**: GitHub, OSF, Hugging Face

**Zenodo record structure**:
```
BENI v1.0: Economic Narrative Measurement Dataset for Bangla News
├── data/ (CSVs, JSONLs, Parquet)
│   ├── narrative_index_full.csv
│   ├── beni_v1_reference_labels_frozen.jsonl
│   ├── llm_assisted_300_annotations.jsonl
│   ├── papers_database.csv
│   └── more...
├── scripts/ (Python pipeline)
│   ├── train.py, correlate.py, build_index.py, etc.
│   └── requirements.txt
├── models/ (TF-IDF joblib files)
│   ├── economic_tfidf_logreg.joblib
│   └── topic_tfidf_logreg.joblib
└── documentation/
    ├── DATASET_CARD.md
    ├── FILE_SCHEMA.md
    └── CITATION.cff
```

### 4. Mendeley Data — Raw Corpus
**Role**: The Potrika corpus is already on Mendeley Data (DOI: 10.17632/v362rp78dc.4). BENI can add the Bangla_News_Database JSONLs as a supplementary release.

**What goes here**:
- Potrika corpus (already on Mendeley — cite existing DOI)
- Optional: Bangla_News_Database (9 JSONL files, 16 GB) as BENI v2 raw corpus

### 5. GitHub — Code of Record
**Role**: Source of truth for all code, issue tracking, collaboration.

**Structure** (suggested reorganization):
```
LILA-LAB/
├── .github/                          # GitHub-specific config
│   ├── workflows/                    # CI/CD (future: test on push)
│   └── FUNDING.yml
├── code/                             # All reproducible code
│   ├── beni_pipeline/               # BENI core (was beni/experiment/beni_pilot/)
│   ├── annotation/                   # LLM annotation infra (copied from beni/annotation/)
│   ├── index/                        # Index construction (was beni/index/)
│   ├── database/                     # DB pipeline (was beni/database/)
│   ├── replications/                 # Systematic review replications
│   └── requirements.txt
├── data/                             # Small curated datasets only
│   ├── index/                        # Narrative index CSVs (core)
│   ├── annotations/                  # Gold-standard labels (core)
│   └── macro/                        # Macroeconomic indicators
│   (DO NOT commit: Potrika CSVs, Bangla_News_Database, model checkpoints)
├── models/                           # Model references (not weights)
│   └── README.md                     # Links to Hugging Face for weights
├── technical-reports/                           # Paper source files + plans
│   ├── paper1_statistical_economics/
│   ├── paper2_systematic_review/
│   ├── paper3_beni_pipeline/
│   ├── paper4_beni_nowcasting/
│   ├── paper5_text_as_data_survey/
│   └── paper6_llm_narrative_extraction/
├── releases/                     # Distribution manifests (THIS plan)
│   ├── OSF_UPLOAD_MANIFEST.md
│   ├── HUGGINGFACE_MODEL_CARD.md
│   ├── ZENODO_UPLOAD_MANIFEST.md
│   └── DATASET_CARD.md
├── README.md
├── CITATION.cff
└── LICENSE
```

---

## Citation Funnel Flow

### How a Researcher Discovers the Work

**Path A (NLP researcher)**:
```
Hugging Face (discovers BENI model)
  → Reads model card → cites Paper 3
  → Follows link to GitHub → runs code
  → Follows link to OSF → reads preprints
  → Finds Zenodo DOI → cites BENI dataset
```

**Path B (Economist)**:
```
OSF (discovers the research program)
  → Reads Paper 4 (nowcasting) abstract
  → Downloads preprint PDF
  → Follows link to GitHub → runs nowcasting
  → Finds Mendeley DOI → cites Potrika corpus
```

**Path C (Social scientist)**:
```
OSF (discovers Paper 5 survey)
  → Reads the 110-year taxonomy
  → Discovers BENI as case study
  → Follows link to Paper 3/4/6
  → Cites Paper 5 as "default entry point"
```

### How Citations Flow

```
Paper 5 (survey) ← cited by anyone writing "related work"
   │
   ├── cites Paper 2 (systematic review) ← the ENI review
   │
   ├── cites Paper 3 (BENI pipeline) ← the measurement tool
   │
   ├── cites Paper 4 (nowcasting) ← the application
   │
   └── cites Paper 6 (LLM extraction) ← the frontier method

BENI v1.0 Data Paper ← cited by Papers 3, 4, 6 as data source
Potrika Corpus (Mendeley) ← cited by BENI Data Paper
```

---

## Upload Checklist

### OSF (Estimated: 1-2 hours)
- [ ] Create OSF project: "Bangla Economic Narrative Indices (BENI)"
- [ ] Add components for each paper + data paper
- [ ] Upload preprints (PDF + TeX) to each component
- [ ] Upload figures to project-level "Figures" folder
- [ ] Upload protocols (annotation schema, guide, adjudication protocol)
- [ ] Upload DATASET_CARD.md
- [ ] Add links to GitHub, Zenodo, Hugging Face, Mendeley in project description
- [ ] Set license: CC BY 4.0
- [ ] Mint OSF DOI

### Hugging Face (Estimated: 2-3 hours)
**Models:**
- [ ] Create namespace: `nabil0x` on Hugging Face
- [ ] Upload best-performing BanglaBERT at each k-label (recommend top 5 models)
  - Model card must include: training details, label-count k, accuracy, F1
  - License: MIT (code), CC BY 4.0 (model weights)

**Dataset:**
- [ ] Create dataset: `beni-narrative-index`
  - Dataset card must cite: Potrika (Mendeley DOI), BENI Data Paper (OSF DOI)
  - Include: narrative_index_full.csv, reference_labels_frozen.jsonl

**Space:**
- [ ] Create Gradio Space: `beni-classifier-demo`
  - Load TF-IDF model from joblib
  - Input: Bangla text → Output: Economic/Not Economic + confidence
  - Link GitHub repo

### Zenodo (Estimated: 1-2 hours)
**Pre-existing**: `10.5281/zenodo.20585401` is already in CITATION.cff
- [ ] Verify this DOI is active (reserve if not)
- [ ] Upload BENI v1.0 data package:
  - Index CSVs, annotation JSONLs, systematic review database
  - Python scripts (63 core scripts)
  - TF-IDF joblib models
  - Documentation files
- [ ] Link to GitHub repo (for auto-archiving on release)
- [ ] Set creators: Nabil, Ann Naser (Jahangirnagar University)
- [ ] Set license: CC BY 4.0

### GitHub (Estimated: 2-3 hours)
- [ ] Reorganize repo structure as outlined above
- [ ] Add `.gitignore` for: `*.safetensors`, `*.joblib`, `*.sqlite`, `*.parquet`, `*.zip`, `*.tar.gz`, `Bangla_News_Database/`, `bnlp-resources/`, whole raw data directories
- [ ] Create `releases/` directory with manifests
- [ ] Update root `README.md` with badges: Zenodo DOI, OSF project, Hugging Face, Mendeley
- [ ] Update `CITATION.cff` with all DOIs
- [ ] Create `RELEASE.md` with versioning strategy

---

## Quick Reference: What to Upload Where

| Asset | OSF | HF | Zenodo | Mendeley | GitHub |
|-------|:---:|:--:|:------:|:--------:|:------:|
| Paper PDFs (all) | ✅ | | | | |
| Paper TeX (all) | ✅ | | | | ✅ |
| Figures | ✅ | | | | ✅ |
| Annotation protocols | ✅ | | | | ✅ |
| BENI narrative index CSVs | | ✅ | ✅ | | ✅ (small) |
| Gold-standard reference labels | | | ✅ | | |
| Systematic review DB | | | ✅ | | |
| Annotation exports (JSONL) | | | ✅ | | |
| Fine-tuned BanglaBERT models | | ✅ | | | |
| TF-IDF joblib models | | ✅ | ✅ | | |
| Python pipeline scripts | | | ✅ | | ✅ |
| Potrika corpus CSVs | | | | ✅ | |
| Bangla_News_Database JSONLs | | | | (future) | |
| Macro data (CPI, FX, reserves) | | | ✅ | | ✅ |
| Dataset card / file schema | ✅ | ✅ | ✅ | | ✅ |
| CITATION.cff | ✅ | ✅ | ✅ | | ✅ |
| README | ✅ | ✅ | ✅ | | ✅ |
| Code License (MIT) | ✅ | ✅ | ✅ | | ✅ |
| Data License (CC BY 4.0) | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## DOI Strategy

| Object | DOI | Status |
|--------|-----|--------|
| **BENI v1.0 dataset** | `10.5281/zenodo.20585401` | Pre-reserved in CITATION.cff — verify on Zenodo |
| **Potrika corpus** | `10.17632/v362rp78dc.4` | ✅ Already published (Mendeley Data) |
| **Paper 2 (arXiv)** | arXiv ID (to be assigned) | Submitted June 2026 |
| **Paper 3 (arXiv)** | arXiv ID (to be assigned) | Planned July 2026 |
| **Paper 4 (arXiv)** | arXiv ID (to be assigned) | Planned Sep 2026 |
| **Paper 5 (arXiv)** | arXiv ID (to be assigned) | Planned Dec 2026 |
| **Paper 6 (arXiv)** | arXiv ID (to be assigned) | Planned Mar 2027 |
| **BENI Data Paper (OSF)** | OSF DOI | To be minted on upload |
| **GitHub releases** | Zenodo DOIs | Auto-generated via Zenodo-GitHub integration |

---

## Key Principles

1. **OSF is the hub** — every other platform links TO it, and it links TO every other platform
2. **Don't duplicate large files** — raw corpus only on Mendeley; models only on HF; datasets on Zenodo
3. **Every platform gets a CITATION.cff** — researchers can cite from wherever they discover
4. **Badges in GitHub README** — Zenodo "DOI", OSF "View on OSF", HF "Model on HF", Mendeley "Dataset"
5. **Version everything** — BENI v1.0, v1.1, etc. Use semantic versioning for dataset releases
6. **The funnel works because everything connects** — no orphan platforms
