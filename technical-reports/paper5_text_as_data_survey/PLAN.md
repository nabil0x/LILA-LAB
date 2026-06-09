# Paper 5 — Text as Data in Social Science: A Systematic Review of the Evolution of Language-Based Methods from Content Analysis to Large Language Models (1916–2026)

**Status**: 🔄 Active expansion — Seed prototype complete (28 canonical papers), manuscript drafted (157 lines), Crossref search returned 301 candidates, screening infrastructure operational
**Timeline**: October–December 2026 (8-10 weeks)
**Depends on**: Papers 2, 3, 4 at least on arXiv (for citation and case study inclusion within the review)
**Current state**: The manuscript structure and taxonomy are prototyped and drafted. The key remaining work is **expansion** — screening 301 Crossref candidates, adding formal database searches (WoS, Scopus, JSTOR), coding 200-400 papers, building the citation network, and replacing prototype figures with full-review versions.

---

## 1. What Already Exists

### Already Done (Seed Prototype)

**Data & Infrastructure:**
- ✅ `data/seed_literature_database.csv` — 28 curated canonical papers across 7 eras and 6 disciplines
- ✅ `data/crossref_candidate_papers.csv` — 301 unscreened papers from Crossref search
- ✅ `data/crossref_screening_queue.csv` — Ranked screening queue (prioritized by relevance score)
- ✅ `data/search_log.md` — Search protocol documentation
- ✅ `data/coding_schema.md` — Coding schema for full review (fields: discipline, year, method, task, language, sample size, validation type, geographic focus, data source, citation count)

**Scripts:**
- ✅ `scripts/search_crossref_candidates.py` — Crossref API search and candidate retrieval
- ✅ `scripts/screen_crossref_candidates.py` — ML-augmented screening with relevance ranking
- ✅ `scripts/build_review_assets.py` — Generates all figures and tables from the literature database
- ✅ `scripts/download_candidate_pdfs.py` — Batch PDF download for screening
- ✅ `scripts/download_open_access_pdfs.py` — Open-access PDF retrieval

**Manuscript (157 lines, `manuscript/paper5_text_as_data_survey.tex`):**
- ✅ Complete paper structure with all 9 sections
- ✅ Era table, timeline figure, method adoption figure
- ✅ Taxonomy section with method-task table
- ✅ Discipline coverage table
- ✅ Language gap figure (seed data)
- ✅ Validation standards figure (seed data)
- ✅ LLM capability matrix figure
- ✅ Research agenda section with BENI case study
- ✅ $\LaTeX$ compiles to PDF

**Figures (seed versions):**
- ✅ `results/figures/timeline_seed.png` — 110-year timeline
- ✅ `results/figures/method_adoption_seed.png` — Cumulative method adoption
- ✅ `results/figures/language_gap_seed.png` — Language coverage
- ✅ `results/figures/validation_by_discipline.png` — Validation standards
- ✅ `results/figures/llm_capability_matrix.png` — LLM vs social science needs

**Tables ($\LaTeX$-ready):**
- ✅ `results/tables/era_counts.tex`
- ✅ `results/tables/method_task_taxonomy.tex`
- ✅ `results/tables/discipline_counts.tex`

### What Remains

**Critical path (blocks submission):**
1. **Screen 301 Crossref candidates** → Include/Exclude (~40-60 expected to pass)
2. **Run formal database searches** (WoS, Scopus, JSTOR, arXiv, SSRN) → add to screening pool
3. **Read and code** 200-400 papers with metadata extraction
4. **Citation network analysis** (cross-disciplinary)
5. **Replace seed figures** with full-review versions
6. **Finalize manuscript** with full-review numbers, add PRISMA diagram
7. **Proofread, format, submit**

---

## 2. Core Research Question

> How has language been transformed into measurable data across social science disciplines over 110 years, and what does the evolution from manual content analysis to large language models reveal about the trajectory, gaps, and future of text-as-data research?

### Guiding Questions
1. How have the **theoretical foundations** of text-as-data evolved across disciplines?
2. Which **social science disciplines** adopted text analysis first, and why?
3. How did **research objectives** change across eras (description → measurement → prediction → causal inference)?
4. How did **methodological sophistication** evolve (manual → dictionary → ML → transformers → LLMs)?
5. What **validation standards** emerged, and how rigorous are they across disciplines?
6. What opportunities do **LLMs and generative AI** create for future social science research?

---

## 3. Contribution

| Layer | Contribution | Cited By |
|-------|-------------|----------|
| **T1: Historical synthesis** | First unified timeline (1916–2026) of text-as-data across 5+ social science disciplines | Any paper needing a "related work" citation |
| **T2: Taxonomy** | Novel classification system: methods × tasks × disciplines × validation standards | Methodology papers |
| **T3: Gap analysis** | Systematic documentation of gaps: geographic, linguistic, validation, and disciplinary isolation | Grant proposals, PhD theses |
| **T4: Research agenda** | Concrete agenda for LLM-era social science text analysis | NLP + social science researchers |

**Citation prediction**: This paper becomes the "default entry point" citation for anyone working at the intersection of NLP and social science. If done well, it accumulates 100+ citations within 3-4 years.

### Why This Paper Now

The field is at an inflection point:
- **2018–2022**: Transformer revolution — but most social scientists still use dictionary methods
- **2022–2026**: LLM explosion — GPT-4, Claude, open-source models, agents
- **2026+**: Social scientists need a roadmap. The old reviews (Grimmer & Stewart 2013, Gentzkow et al. 2019) are pre-LLM.

This paper fills the gap between the pre-LLM reviews and the current moment.

---

## 4. Paper Structure

### Title
> Text as Data in Social Science: A Systematic Review of the Evolution of Language-Based Methods from Content Analysis to Large Language Models (1916–2026)

### Sections

**1. Introduction** (~2 pages)
- Text-as-data is transforming social science — but the transformation is uneven
- Three gaps motivate the review:
  1. **Disciplinary fragmentation**: economics, poli-sci, sociology, communication, psych, and NLP rarely cite each other
  2. **Historical amnesia**: LLM-era researchers often reinvent methods from 1950s content analysis
  3. **Geographic/linguistic bias**: 84% of research is English, 56% is US-focused
- This review provides a unified historical framework, a taxonomy, and a research agenda

**2. Historical Eras** (~8 pages — the core of the paper)

| Era | Period | Key Innovation | Representative Works |
|-----|--------|----------------|---------------------|
| **Era 1: Content Analysis** | 1916–1950 | Propaganda analysis, manual coding | Lasswell (1927, 1948), Berelson (1952) |
| **Era 2: Quantitative Content Analysis** | 1950–1980 | Systematic coding schemes, inter-coder reliability | Holsti (1969), Krippendorff (1980) |
| **Era 3: Computer-Assisted Text Analysis** | 1980–2000 | Keyword-in-context, concordances, early NLP | Stone et al. (1966), General Inquirer |
| **Era 4: Dictionary Methods** | 2000–2010 | Sentiment dictionaries, LIWC, General Inquirer | Tetlock (2007), Baker et al. (2016) EPU |
| **Era 5: Topic Models & ML** | 2010–2018 | LDA, structural topic models, SVM, Naive Bayes | Blei (2012), Roberts et al. (2014) |
| **Era 6: Transformers & Embeddings** | 2018–2022 | BERT, RoBERTa, sentence embeddings | Devlin et al. (2019) |
| **Era 7: Large Language Models** | 2022–2026 | GPT-4, Claude, Llama, prompting, agents | Brown et al. (2020), recent works |

Each era section covers:
- **What was technically new?**
- **Which disciplines adopted it and why?**
- **What research questions could now be asked?**
- **What validation standards existed?**
- **What were the limitations?

**3. A Unified Taxonomy of Text-as-Data Methods** (~3 pages)
- **3.1 By task**: classification → measurement → prediction → discovery → causal inference
- **3.2 By method**: dictionary → supervised ML → unsupervised ML → embeddings → LLMs
- **3.3 By data type**: short text (tweets) → medium (news) → long (documents) → corpora
- **3.4 By validation**: manual annotation → gold standard → inter-annotator agreement → external validation
- **3.5 Contributions**: a classification system researchers can use to position their own work

**4. Disciplinary Adoption Patterns** (~3 pages)
- **4.1 Political Science**: early adopter (Lasswell), content analysis of speeches, ideology scaling
- **4.2 Communication Studies**: framing analysis, media effects, agenda-setting
- **4.3 Economics**: late adopter (2000s), now fastest growing: narrative economics, nowcasting
- **4.4 Sociology**: discourse analysis, cultural sociology, identity
- **4.5 Psychology**: LIWC, sentiment, personality from text
- **4.6 Computational Social Science**: the convergence (2015–present)
- **4.7 Who cites whom?** Citation network analysis across disciplines (novel contribution)

**5. Geographic and Linguistic Gaps** (~2 pages)
- Meta-analysis of language coverage across all reviewed papers
- Map: text-as-data research density by country/language
- Deep dives: English dominance (84%), gap regions (Africa, South Asia, Latin America)
- Implications: whose narratives are we measuring? Whose are we missing?

**6. Validation Standards Across Fields** (~2 pages)
- Systematic comparison of validation practices:
  - Economics: out-of-sample testing common, but weak baselines
  - Political science: hand-validated dictionaries, but small samples
  - NLP: leaderboard culture, but artificial tasks
- What "good validation" looks like: a cross-disciplinary minimal standard
- Publication bias documentation

**7. The LLM Revolution: Opportunities and Pitfalls** (~3 pages)
- **7.1 What changed?** From fine-tuning to prompting, from labels to instructions
- **7.2 What LLMs enable for social science**:
  - Zero-shot classification at scale (dictionary-level cost, human-level quality?)
  - Narrative understanding beyond bag-of-words
  - Synthetic data for pilot studies
  - Agent-based simulation of belief dynamics
- **7.3 What LLMs still cannot do**:
  - Reliable measurement (hallucination, bias, inconsistency)
  - Causal claims from text alone
  - Replicability (model updates change results)
  - Low-resource language coverage
- **7.4 A research agenda for LLM-era text-as-data**
- **7.5 The BENI case study** (Paper 6 — LLM narrative extraction) fits here

**8. A Research Agenda for 2026–2036** (~2 pages)
- **8.1 Methodological priorities**: validation standards, replicability, bias documentation
- **8.2 Substantive priorities**: geographic expansion, multilingual indices, real-time monitoring
- **8.3 Infrastructure priorities**: open-source pipelines, annotation tools, benchmark datasets
- **8.4 Institutional priorities**: cross-disciplinary training, journal standards, replication mandates
- **8.5 The BENI case study**: Papers 3-4 (pipeline + nowcasting) as exemplars of the research agenda

**9. Conclusion** (~1 page)

---

## 5. Methodology for the Review

### Search Strategy
| Source | Coverage | Status | Query |
|--------|----------|--------|-------|
| Crossref | All years | ✅ 301 candidates retrieved | Broad text-as-data query |
| Web of Science | All years | ⚠️ Need access | "text as data" OR "content analysis" AND social science |
| Scopus | All years | ⚠️ Need access | Same + forward/backward citation tracking |
| arXiv | 2018–2026 | ⚠️ Need to run | NLP + social science cross-listed papers |
| SSRN | 2000–2026 | ⚠️ Need to run | Working papers in economics + computational social science |
| JSTOR | 1916–2000 | ⚠️ Need access | Historical content analysis literature |

### Screening Workflow
```
301 Crossref candidates (unscreened)
    │
    ├── Step 1: Screen title + abstract → Include/Exclude
    │       (Target: ~40-60 included from Crossref)
    │
    ├── Step 2: Expand with WoS/Scopus/JSTOR/arXiv/SSRN searches
    │       (Target: +200-340 additional candidates)
    │
    ├── Step 3: Deduplicate across sources
    │
    ├── Step 4: Screen remaining candidates → final pool of 200-400
    │
    └── Step 5: Read and code all included papers
```

### Inclusion Criteria
- **Empirical**: must analyze text data (not just propose methods)
- **Social science**: economics, political science, sociology, communication, psychology, computational social science
- **Time period**: 1916–2026
- **Language**: Any (code language coverage as metadata)

### Exclusion Criteria
- Pure computer science/NLP benchmarks without social science application
- Method papers with no empirical demonstration
- Non-English papers without English abstract (unless accessible for coding)

### Data Extraction
For each paper (target: 200-400 papers):
- Fields: discipline, year, method, task, language, sample size, validation type, geographic focus, data source, citation count

### Analysis
- **Era analysis**: temporal trends in method adoption
- **Discipline analysis**: comparative adoption rates
- **Citation network**: cross-disciplinary citation patterns
- **Gap analysis**: geographic, linguistic, methodological blind spots
- **Validation meta-analysis**: what standards are actually used (not just recommended)

---

## 6. Key Figures

| Figure | Description | Status |
|--------|-------------|--------|
| F1 | 110-year timeline of text-as-data methods | ✅ Seed version — expand with full review |
| F2 | Citation network across disciplines | ❌ Not yet built |
| F3 | Geographical density map of text-as-data research | ❌ Not yet built |
| F4 | Method adoption curves by discipline (7 eras × 6 disciplines) | ✅ Seed version — expand |
| F5 | Validation standard comparison across fields | ✅ Seed version — expand |
| F6 | LLM capabilities vs social science needs | ✅ Seed version — refine |
| F7 | Proposed research agenda visual | ❌ Not yet built |
| F8 | PRISMA flow diagram | ❌ Not yet built |

---

## 7. Timeline

```
Papers 2, 3, 4 should be on arXiv before Paper 5 submits (to cite as case studies).
Paper 4 submits Sep 2026 → Paper 5 can start serious expansion in Oct 2026.
```

| Week | Phase | Tasks | Deliverable |
|------|-------|-------|-------------|
| **W1** | Screening | Screen 301 Crossref candidates (title + abstract). Aim: 50-60 includes. Update screening queue CSV. | Screened candidate pool |
| **W2** | Expansion | Run WoS, Scopus, JSTOR, arXiv, SSRN searches. Import and deduplicate. Add to screening pool. | Master candidate database |
| **W3-4** | Reading | Read and code papers. Target: 50-60 technical-reports/week. Prioritize by era and discipline coverage. | Coded dataset (150+ papers) |
| **W5-6** | Reading | Continue reading and coding. Target: 50-60 technical-reports/week. | Coded dataset (250+ papers) |
| **W7** | Analysis | Citation network analysis. Geographic mapping. Validation meta-analysis. Update all figures. | Final figures + statistics |
| **W8** | Writing | Update manuscript sections 1-5 with full-review numbers. Replace seed figures. Add PRISMA diagram. | Updated draft |
| **W9** | Writing | Update sections 6-9. Refine LLM agenda with Paper 6 insights (if available). Proofread. | Near-final draft |
| **W10** | Submission | Format for target. Generate arXiv package. Write abstract. Submit. | Full paper |

**Total reading volume**: 200-400 papers × 15-30 min ≈ 50-200 hours. The bottleneck is reading time. Mitigation: batch reading by era (read all Era 4 papers in one sitting for consistency).

---

## 8. Target Venues

| Venue | Type | Fit | Notes |
|-------|------|-----|-------|
| **Nature Human Behaviour** | Interdisciplinary | Very strong fit, high impact | Long-shot but worth trying |
| **Journal of the Royal Statistical Society (Series A)** | Review | Strong statistics + social science fit | Good alternative |
| **Plos ONE** | Interdisciplinary OA | Reliable path | High acceptance for technically sound work |
| **arXiv preprint** | Preprint | Immediate citation | Post first, journal later |

**Recommended strategy**: arXiv preprint → Nature Human Behaviour (if rejected → PLOS ONE).

---

## 9. Connection to the Research Program

```
Paper 2: ENI Systematic Review (2007-2025, 66 papers)
   ↓ narrow, domain-specific → feeds Era 4-6 economics section

Paper 3: BENI Pipeline → feeds the "LLM-assisted measurement" case study
Paper 4: BENI Nowcasting → feeds the "developing-economy nowcasting" case study
Paper 6: LLM Narrative Extraction → feeds the "LLM as measurement device" section

All four → Paper 5: 110-year cross-disciplinary synthesis
```

Paper 5 is the capstone. It subsumes Paper 2 as one discipline section, and uses Papers 3-4-6 as case studies of the research agenda in action.

**Dependency constraint**: Papers 2, 3, 4, and ideally 6 should be on arXiv before Paper 5 submission. This avoids self-citation concerns and allows Paper 5 to cite them as established contributions.

---

## 10. Required Resources

| Resource | Amount | Status |
|----------|--------|--------|
| Literature database (WoS, Scopus, JSTOR) | Institutional access | ⚠️ Verify access (Jahangirnagar University) |
| Reading time | 200-400 papers × 15-30 min = 50-200 hours | Heavy — dedicated reading blocks needed |
| Citation network tool | Connected Papers / CitNetExplorer | ✅ Free |
| Geographic mapping tool | Python (plotly/geopandas) | ✅ Available |
| PDF access for full-text screening | 200-400 PDFs | ⚠️ Partially available via open access + crossref |

---

## 11. Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scope too large (110 years, 6 disciplines, 300+ papers) | High | High | Strict inclusion criteria; batch reading by era |
| Pre-2000 literature hard to access | Medium | Medium | JSTOR has most; era 1-2 coverage is manageable (<50 papers total) |
| LLM literature moving too fast (2024-2026) | High | High | Set a firm cutoff date (e.g., June 2026). Note LLM section is a snapshot. |
| WoS/Scopus access unavailable | Medium | Low | Crossref + arXiv + Google Scholar + manual citation chasing can reach 200+ papers |
| Writing a review after empirical papers feels like "going back" | Medium | Low | Frame as capstone synthesis — it's what makes the research program a coherent narrative |
| Reviewer: "Why another review?" | Medium | Medium | Emphasize: (1) first to cover 110-year span, (2) first cross-disciplinary taxonomy, (3) first to position LLMs within historical context |
