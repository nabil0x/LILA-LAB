# Paper 6 — LLMs as Measurement Devices: Extracting Structured Economic Narratives from Low-Resource Language News

**Status**: 💡 Proposed — Not yet started
**Timeline**: January–March 2027 (10 weeks, after Papers 3-5)
**Depends on**: Paper 3 (uses the same Potrika corpus + annotated reference set), but can proceed independently after Paper 3 is on arXiv. Does **not** depend on Papers 4 or 5.
**Current state**: Zero implementation. This is a new paper concept that extends Paper 3's LLM usage from binary classification to structured narrative extraction.

---

## 1. Motivation

Paper 3 uses LLMs for **binary economic relevance classification** (is this article Economic or Not Economic?). The LLM annotator labels 300 articles with a structured schema (relevance, confidence, topic, sentiment, narrative force), but the paper only uses the binary "Economic/Not Economic" label for the classification pipeline.

Paper 6 asks: **what if we use the LLM's full structured output as the measurement instrument itself?**

Instead of:
```
Raw text → Binary classifier → Economic relevance score → BENI index
```

We do:
```
Raw text → LLM structured extraction → Multi-dimensional narrative measurement
  ├── Economic topic (12 categories)
  ├── Sentiment (negative/neutral/positive)
  ├── Narrative frame (crisis, burden, reform, stability, ...)
  ├── Entity extraction (institutions, policies, sectors)
  └── Causal claims (X causes Y)
```

This moves from "how much economic news?" to **"what economic narratives are being told?"** — a much richer measurement space.

### Why This Paper Now

1. **LLMs can do structured extraction at scale** — cost per article is ~$0.01-0.05. 10,000 articles = $100-500.
2. **Paper 3's LLM infrastructure already exists** — annotation schema, prompt templates, batch processing.
3. **The BENI index provides ground truth** for validating whether extracted narratives correlate with economic outcomes — same macro indicators (FX, CPI, reserves).
4. **No prior work does this for Bangla** — or for any low-resource language's economic news.

---

## 2. Core Research Question

> Can large language models (LLMs) be used as reliable measurement devices for extracting structured economic narratives from low-resource language news, and do the extracted narratives provide richer economic signal than simple classification-based indices?

### Sub-questions
1. How reliably do LLMs extract structured narrative fields (topic, sentiment, frame, entities) from Bangla economic news?
2. Do LLM-extracted narrative dimensions correlate with macroeconomic indicators, and which dimensions carry the most signal?
3. Does multi-dimensional narrative measurement outperform the unidimensional BENI (economic share) for nowcasting?
4. What is the cost-quality tradeoff for LLM-based narrative extraction in a low-resource language setting?

---

## 3. Contribution

| Layer | Contribution | Cited By |
|-------|-------------|----------|
| **T1: LLM-as-measurement benchmark** | First structured economic narrative extraction in Bangla — across topics, sentiment, frames, entities | Development economists, NLP researchers |
| **T2: Comparison** | Multi-dimensional narrative measurement vs unidimensional BENI — which predicts macro outcomes better? | Text-as-data methodologists |
| **T3: Cost-quality frontier** | Price-performance of structured extraction (zero-shot vs few-shot vs fine-tuned) for low-resource language | Practitioners building LLM measurement pipelines |

### How Paper 6 Is Different From Paper 3

| Dimension | Paper 3 | Paper 6 |
|-----------|---------|---------|
| **LLM task** | Binary classification (Economic/Not Economic) + label-cost curve | Structured narrative extraction (topic, sentiment, frame, entities, causal claims) |
| **Output** | Single binary label per article | Multi-dimensional structured record per article |
| **Downstream use** | Aggregate into monthly BENI index (economic share) | Construct sub-indices: inflation_sentiment, crisis_frame_count, entity_mentions |
| **Validation** | Correlation with macro (FX, CPI) — level + differenced | Same macro indicators, but test which narrative dimensions predict best |
| **LLM role** | Silver standard for classification model training | **Direct measurement instrument** — the LLM output IS the data |

---

## 4. Paper Structure

### Title (working)
> LLMs as Measurement Devices: Extracting Structured Economic Narratives from Bangla News

### Sections

**1. Introduction** (~1.5 pages)
- Economic narrative measurement has relied on classification-based indices (EPU, BENI) → single dimension
- LLMs can extract richer structure: topics, sentiment, frames, entities, claims
- This paper: use LLMs as direct measurement instruments for Bangla economic news
- Preview: which narrative dimensions correlate with macro outcomes; cost curves for extraction

**2. Related Work** (~1 page)
- **LLMs as annotators**: Gilardi et al. (2023), Tornberg (2023), Hemmingsen et al. (2024)
- **Narrative economics**: Shiller (2017, 2019), narrative frames, epidemic models of narrative spread
- **Structured extraction**: Few-shot NER, event extraction, relation extraction in low-resource languages
- **Positioning**: No prior work does full structured narrative extraction for Bangla economic news

**3. Data** (~1 page)
- **Potrika corpus**: 664k Bangla news articles, 2014-2020 (same as Paper 3)
  - Use 300-article LLM-annotated set from Paper 3 as validation seed
  - Expand to 1,000-2,000 articles for extraction benchmark
  - Full corpus scoring for index construction (if budget permits)
- **Macroeconomic indicators**: BDT/USD FX, CPI, reserves (same as Papers 3-4)
- **Paper 3 BENI index**: used as baseline for comparison

**4. Methods** (~2.5 pages)
- **4.1 Extraction schema**: structured output per article
  - Economic topic (12 categories, from Paper 3 schema)
  - Sentiment toward topic (negative/neutral/positive)
  - Narrative frame (crisis, burden, reform, stability, uncertainty, resilience, blame, neutral)
  - Key entities mentioned (government, Bangladesh Bank, specific ministries, sectors)
  - Causal claims extraction (X leads to Y — e.g., "price hike causes suffering")
  - Confidence score per extraction field
- **4.2 LLM extraction protocol**
  - Zero-shot: prompt with schema definition only
  - Few-shot: add 3-5 exemplar extractions
  - Multi-model: compare Claude Sonnet 4, GPT-4o, Llama 3 (if available for Bangla)
- **4.3 Validation strategy**
  - **Self-consistency**: re-extract random subset, measure agreement per field
  - **Cross-model agreement**: compare outputs across LLMs for same articles
  - **Human review**: random sample reviewed by author for field-level accuracy
  - **Macro validation**: correlate extracted dimensions with FX, CPI, reserves

**5. Results** (~2.5 pages)
- **5.1 Extraction reliability** (table: self-consistency, cross-model agreement, human review accuracy by field)
- **5.2 Narrative dimension correlations with macro indicators**
  - Which topics, frames, sentiments correlate most strongly with CPI/FX?
  - Does "crisis" frame predict inflation better than "stability" frame?
- **5.3 Multi-dimensional vs unidimensional BENI comparison**
  - Does topic-specific sentiment (e.g., inflation sentiment sub-index) outperform the aggregate BENI index?
  - Test: regress CPI on various narrative sub-indices — compare $R^2$
- **5.4 Cost-quality frontier** (table: articles/$ for each LLM, field-level accuracy cost)

**6. Discussion** (~1 page)
- Which narrative dimensions carry genuine economic signal vs measurement noise
- When LLM-as-measurement is appropriate vs when traditional classification suffices
- Limitations: LLM cost, prompt sensitivity, schema design choices
- Implications for low-resource language narrative measurement

**7. Conclusion** (~0.5 page)

---

## 5. Experimental Design

### Extraction Schema (12 fields)

| Field | Type | Values | Expected Reliability |
|-------|------|--------|---------------------|
| Economic relevance | Binary | Economic / Not Economic | High (from Paper 3 — 96% self-consistency) |
| Confidence | Ordinal | 1 / 2 / 3 | High |
| Economic topic | Categorical (12) | inflation, FX, trade, fiscal, etc. | Medium (topic boundary issues) |
| Sentiment | 3-class | negative / neutral / positive | Medium-High |
| Narrative frame | Categorical (8) | crisis, burden, reform, stability, etc. | Low-Medium (subjective) |
| Key entities | List | e.g., "Bangladesh Bank", "Ministry of Finance" | Medium |
| Causal claims | List of triples | [cause → effect → topic] | Low (hardest task) |

### LLM Extraction Protocol

| Variant | Cost/article | Expected Quality | N for Index |
|---------|-------------|------------------|-------------|
| Zero-shot Claude | ~$0.02 | Medium | Up to 50,000 ($1,000) |
| Few-shot Claude | ~$0.025 | High | Up to 10,000 ($250) |
| Zero-shot GPT-4o | ~$0.03 | Medium | Up to 10,000 ($300) |
| Few-shot GPT-4o | ~$0.035 | High | Up to 5,000 ($175) |

**Recommended approach**: Start with 1,000-article multi-LLM benchmark. Score the full 120k calibration set with the best-performing LLM protocol.

### Validation

| Method | N | What It Tests |
|--------|---|---------------|
| Self-consistency (re-extract) | 100 articles | Field-level stability |
| Cross-model agreement | 200 articles | Schema robustness across LLMs |
| Human review | 100 articles | Ground-truth accuracy (author review) |
| Macro correlation | Full index | Predictive validity |

### Narrative Sub-Indices

Aggregate monthly:
- **Topic share**: % of articles on each economic topic → 12 topic indices
- **Sentiment balance**: (positive - negative) / total → sentiment index per topic
- **Frame prevalence**: % using each narrative frame → crisis index, reform index, etc.
- **Entity mention count**: volume of mentions for Bangladesh Bank, specific policies

---

## 6. Relationship to Other Papers

```
Paper 3 ──LLM infrastructure + classification pipeline──┐
                                                         ├──▶ Paper 6
Paper 3 ──300 LLM-annotated articles (validation seed)──┘
         (but Paper 3 only uses binary label)

Paper 6 output ──structured narrative dimensions──▶ could feed into
    │                                                Paper 4's nowcasting
    │                                                (as richer predictors)
    └──▶ Paper 5's LLM Revolution section (case study)

Key distinction:
  Paper 3: "Here's how to build an index with LLM help → classification"
  Paper 6: "Here's how to use LLMs as the measurement instrument → extraction"
```

Paper 6 can proceed independently from Papers 4-5, but ideally Paper 3 is on arXiv first (so Paper 6 can cite the annotation schema, corpus, and macro data pipeline).

---

## 7. Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| **W1** | Design extraction schema + prompt templates | Draft schema + 4 prompt variants |
| **W2** | Run extraction benchmark (1,000 articles, 3 LLMs) | Raw extraction data |
| **W3** | Validate: self-consistency + cross-model + human review | Reliability metrics per field |
| **W4** | Aggregate monthly narrative sub-indices | Topic, sentiment, frame, entity indices |
| **W5** | Macro validation: correlate sub-indices with CPI, FX | Correlation table |
| **W6** | Compare vs BENI: which predicts better? | Nowcasting comparison |
| **W7-8** | Write paper | Draft sections 1-7 |
| **W9** | Generate figures: narrative dimension radar, correlation heatmap, cost frontier | All figures |
| **W10** | Polish, proofread, format, submit | Full paper |

**Total estimated cost**: $500-1,000 in LLM API calls (for 5,000-10,000 article extractions).

---

## 8. Target Venues

| Venue | Type | Fit | IF |
|-------|------|-----|-----|
| **PLOS ONE** | Interdisciplinary | Good — methodology + application | ~3.7 |
| **Behavior Research Methods** | Methods | Excellent — measurement focus | ~6.5 |
| **Journal of Computational Social Science** | Computational | Good — LLM + social science | ~2.5 |
| **Computational Linguistics** | NLP | Good if method dominates | ~3.0 |
| **arXiv preprint** | Preprint | Immediate citation + timestamp | — |

**Recommended**: arXiv preprint first, then **Behavior Research Methods** (strong fit for "LLMs as measurement devices" framing).

---

## 9. Required Resources

| Resource | Amount | Status |
|----------|--------|--------|
| Potrika corpus | 664k articles | ✅ Available from Paper 3 |
| Paper 3 LLM annotation schema | 12-field schema | ✅ Available |
| Paper 3 300 annotated articles | Validation seed | ✅ Available |
| Claude API credits | ~$200-500 | ⚠️ Need to allocate budget |
| GPT-4o API credits | ~$200-500 | ⚠️ Need to allocate budget |
| Llama 3 (local inference) | GPU for a few hours | ⚠️ May not work well for Bangla structured extraction |
| Macro data (FX, CPI) | Monthly, 2014-2020 | ✅ Available from Papers 3-4 |
| Human review time | 100 articles × 5 minutes = ~8 hours | ✅ Author |

---

## 10. Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM structured extraction is unreliable in Bangla (low self-consistency) | High | Medium | Report all reliability metrics transparently. If low, paper becomes "what LLMs can and cannot extract in Bangla" — still publishable |
| Narrative sub-indices do not correlate with macro outcomes | Medium | Medium | The comparison with BENI is still informative — "classification index captures all the signal" is a finding |
| LLM API costs exceed budget | Medium | Low | Start with 1,000-article benchmark. Scale to 5,000+ only if signal is promising |
| Paper 3 not on arXiv before Paper 6 starts | Low | Low | Can cite Paper 3's methods section directly; both papers are by same author |

---

## 11. First Steps (Weeks 1-2)

### Week 1: Schema + Prompts
1. Review Paper 3's annotation schema (12-topic, 8-frame, sentiment, confidence)
2. Design extraction prompt: structured JSON output with field-level instructions
3. Design 4 prompt variants:
   - Zero-shot (schema only)
   - Few-shot (schema + 3 exemplar extractions)
   - Chain-of-thought (schema + reasoning steps → extraction)
   - Structured (schema with field-level constraints, regex-like format enforcement)
4. Select 1,000 articles for extraction benchmark (stratified by: economic/not-economic, newspaper, year)

### Week 2: Run Extraction
1. Set up batch processing pipeline (reuse Paper 3's `annotate_batch.py` or deploy new)
2. Run Claude Sonnet 4 extraction on 1,000 articles with all 4 prompt variants
3. Run GPT-4o on 500 articles with best prompt variant
4. Store all outputs with article ID, LLM, prompt variant, timestamp
5. Extract self-consistency subset (100 articles, re-run with same variant)
