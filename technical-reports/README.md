# Research Program: NLP Infrastructure for Economic Measurement in Low-Resource Languages

**Author**: Ann Naser Nabil
**Affiliation**: Jahangirnagar University, Department of Economics

---

## Program Identity

> Building the measurement infrastructure — methods, indices, and benchmarks — that enable data-scarce economies to use local-language text as a real-time economic signal.

---

## Paper Sequence (6-Paper Arc)

```
FOUNDATION (Completed):
  Paper 1: Statistical Economics                           ← Empirical credibility
  Paper 2: NLP in Social Science (Systematic Review)       ← Interdisciplinary authority

CORE TRILOGY (2026):
  Paper 3: BENI Pipeline (Method)        ⇐ Finishing sprint  ← Infrastructure builder
  Paper 4: BENI Nowcasting (Application) ⇐ Awaiting Paper 3  ← Policy relevance
  Paper 5: Text as Data Survey (Capstone)                    ← Field leadership

EXTENSION (2027):
  Paper 6: LLMs as Measurement Devices                       ← Frontier methodology
```

---

## Six-Paper Architecture

### Paper 1 — The Foundation
**Title**: Statistical Economics
**Status**: ✅ Complete
**Role**: Empirical credibility for the research program.

### Paper 2 — The Review
**Title**: NLP in Social Science: A Systematic Review, Replication Study, and Bangla Extension
**Status**: ✅ Submitted to arXiv (June 2026)
**Role**: Establishes the gap — 84% English, 0% Bangla, 66 papers reviewed, 8 replications.
**Outputs**: Meta-analysis + replication suite + gap documentation.

### Paper 3 — The Instrument
**Title**: Building Local-Language Economic Narrative Indices: A Replicable Pipeline from Raw News to Validated Index
**Status**: 🔄 Finishing sprint — manuscript drafted, BENI v1 frozen, Kaggle BanglaBERT pending
**Timeline**: July 2026 submission
**What it does**: Provides a complete, reusable template for constructing economic narrative indices in any low-resource language.
**Identity**: "I build measurement infrastructure."
**Outputs**: Frozen BENI v1 index + LLM-labeled reference set + open-source pipeline + annotation cost/quality curve.

### Paper 4 — The Application
**Title**: Nowcasting Inflation with the Bangla Economic Narrative Index: Local-Language News as a High-Frequency Economic Indicator
**Status**: 📋 Awaiting Paper 3 freeze — prototype done, manuscript drafted, results use TF-IDF placeholder
**Timeline**: August–September 2026 (6 weeks)
**What it does**: Shows the instrument in action — evaluates whether BENI improves inflation nowcasts.
**Identity**: "I use my instruments to answer real economic questions."
**Outputs**: Nowcast evaluation + policy implications + dashboard design.

### Paper 5 — The Synthesis
**Title**: Text as Data in Social Science: A Systematic Review of the Evolution of Language-Based Methods from Content Analysis to Large Language Models (1916–2026)
**Status**: 🔄 Active expansion — seed prototype complete (28 papers), 301 Crossref candidates to screen, manuscript drafted
**Timeline**: October–December 2026 (10 weeks)
**Depends on**: Papers 2, 3, 4 on arXiv (for citation as case studies)
**What it does**: Positions the entire research program within the 110-year intellectual history of text-as-data.
**Identity**: "I lead the field's understanding of where we've been and where we're going."
**Outputs**: Unified taxonomy + gap analysis + LLM-era research agenda + BENI case study.

### Paper 6 — The Frontier
**Title**: LLMs as Measurement Devices: Extracting Structured Economic Narratives from Low-Resource Language News
**Status**: 💡 Proposed — zero implementation yet
**Timeline**: January–March 2027 (10 weeks)
**Depends on**: Paper 3 (uses same corpus + annotation infrastructure), independent of Papers 4-5
**What it does**: Extends Paper 3 from binary classification to full structured narrative extraction (topics, sentiment, frames, entities, causal claims) using LLMs as direct measurement instruments.
**Identity**: "I push the frontier of what LLMs can measure in low-resource languages."
**Outputs**: Multi-dimensional narrative indices + LLM extraction benchmark + cost-quality frontier.

---

## Citation Strategy

| Paper | Expected Citation Base | Citation Growth | Peak Year |
|-------|----------------------|-----------------|-----------|
| Paper 3 | NLP for development economics | Steady | Year 2-4 |
| Paper 4 | Nowcasting + Bangladesh policy | Moderate | Year 1-3 |
| Paper 5 | ANY text-as-data paper | High (100+) | Year 3-6 (long tail) |
| Paper 6 | LLM-as-measurement methodology | Growing | Year 2-5 |

Paper 5 is the "umbrella" that Papers 2-4 sit under. A researcher who cites Paper 5 for the historical overview will also cite Papers 3-4 for specific contributions. Paper 6 is a standalone frontier contribution that feeds into Paper 5's LLM section.

---

## Dependency Graph

```
     ┌─────────────────────────────────────────────────────────┐
     │                     Paper 5 (Capstone)                   │
     │   110-year text-as-data review + BENI/LLM case studies   │
     └────────┬──────────┬──────────────┬───────────────────────┘
              │          │              │
              ▼          ▼              ▼
     ┌──────────┐ ┌───────────┐ ┌────────────────┐
     │ Paper 2  │ │ Papers 3-4│ │   Paper 6      │
     │ (Review) │ │ (BENI)    │ │ (LLM extraction)│
     └──────────┘ └─────┬─────┘ └────────────────┘
                        │
                        ▼
                 ┌───────────┐
                 │ Paper 4   │
                 │(Nowcasting)│
                 └───────────┘

     Paper 1 (Stats Econ) — independent foundation

Key dependencies:
  Paper 4 → Paper 3 (needs frozen BENI index)
  Paper 5 → Papers 2, 3, 4 (needs them on arXiv for citation)
  Paper 6 → Paper 3 (uses corpus + LLM infra), independent of 4, 5
```

---

## Timeline Overview

```
2026 Jun     Jul     Aug     Sep     Oct     Nov     Dec     | 2027 Jan   Feb   Mar
├────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
Paper 2: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ [Jun arXiv]
Paper 3: ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ [Jul arXiv]
Paper 4: ░░░░░░░░░░████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ [Aug-Sep]
Paper 5: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████████████████░░░░░░░░░░░░░░ [Oct-Dec]
Paper 6: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████████████ [Jan-Mar]
```

---

## Key Distinctions

| Dimension | Paper 3 | Paper 4 | Paper 5 | Paper 6 |
|-----------|---------|---------|---------|---------|
| **Primary audience** | NLP researchers, methodologists | Economists, central bankers | Social scientists (all fields) | NLP + computational social science |
| **Contribution type** | Methodological pipeline | Empirical application | Historical synthesis + agenda | LLM measurement benchmark |
| **Novelty** | Replicable LLM-assisted template | First Bangla nowcast | 110-year cross-disciplinary review | First structured narrative extraction in Bangla via LLMs |
| **Data requirement** | Potrika + LLM annotation | BENI index + CPI | 300-400 published papers | Potrika + LLM API credits ($500-1,000) |
| **Risk if null result** | Low (pipeline still valuable) | Medium (no nowcast improvement) | N/A (synthesis cannot fail) | Medium (extraction may be unreliable) |
| **Effort** | Now: finishing sprint (3-4 days) | 6 weeks | 10 weeks | 10 weeks |
| **Citation half-life** | 5-7 years | 3-5 years | 10+ years | 5-7 years |
| **LLM dependency** | Medium (300 labels) | None | Low | High (core measurement instrument) |
