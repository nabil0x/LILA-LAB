# Paper 6 — LLMs as Measurement Devices

> **Title**: LLMs as Measurement Devices: Extracting Structured Economic Narratives from Low-Resource Language News
>
> **Status**: 💡 Proposed — zero implementation yet
>
> **Timeline**: January–March 2027 (10 weeks)

---

## Current State

This paper is in the **planning phase**. The only file is `PLAN.md`, which contains:

- Core research question and motivation
- Extraction schema (12 fields: topic, sentiment, frame, entities, causal claims)
- Experimental design (zero-shot vs few-shot, multi-LLM comparison)
- Validation strategy (self-consistency, cross-model, human review, macro correlation)
- Cost-quality frontier estimation
- Timeline and resource budget

---

## Dependencies

| Dependency | Source | Status |
|------------|--------|--------|
| Potrika corpus (664k articles) | `beni/Bangla_News_Database/` + `data-paper/data/` | ✅ Available |
| LLM annotation schema (12-field) | `beni/annotation/ANNOTATION_SCHEMA.md` | ✅ Available |
| 300-article LLM-annotated reference set | `beni/annotation/` | ✅ Available |
| Macro data (FX, CPI, reserves) | `beni/data/raw/macro/` | ✅ Available |
| BENI index (baseline for comparison) | `beni/index/outputs/` | ✅ Available (TF-IDF) |
| Claude API credits | External | ⚠️ Budget needed (~$200-500) |
| GPT-4o API credits | External | ⚠️ Budget needed (~$200-500) |

---

## Relationship to Other Papers

```
Paper 3 ──LLM infrastructure + classification pipeline──┐
                                                         ├──▶ Paper 6
Paper 3 ──300 LLM-annotated articles (validation seed)──┘
         (Paper 3 only uses binary label; Paper 6 uses all 12 fields)

Paper 6 output ──structured narrative dimensions──▶ could feed into
    │                                                Paper 4's nowcasting (richer predictors)
    └──▶ Paper 5's LLM Revolution section (case study)
```

- **Depends on**: Paper 3 (corpus, annotation infra, macro data)
- **Independent of**: Papers 4, 5
- **Feeds into**: Paper 5 as a frontier methodology case study

---

## For Research Agents

- This paper extends Paper 3's binary classification to **full structured narrative extraction**.
- The LLM becomes the measurement instrument itself, not just a labeler.
- When Paper 3 is on arXiv, reuse its `annotate_batch.py` pipeline with the extended extraction schema.
- Start with a 1,000-article benchmark across multiple LLMs before scaling to the full corpus.
