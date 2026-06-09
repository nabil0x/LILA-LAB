# Paper 3 — Building Local-Language Economic Narrative Indices: A Replicable Pipeline from Raw News to Validated Index

**Status**: 🔄 Active — Manuscript drafted, index frozen, finishing sprint in progress
**Timeline**: June–July 2026 (was planned 4 weeks; manuscript ~90% complete)
**Current state**: BENI v1 database harmonized (1.4M articles), TF-IDF baseline frozen at 88.17% acc, LLM silver standard validated, manuscript drafted with all 7 sections (`\input{drafts/*}`). Remaining: BanglaBERT fine-tuning on Kaggle, label-cost curve for T3, final results integration, figure polishing, arXiv submission.

---

## 1. What Has Changed Since the Original Plan

The paper has evolved from a "3-model comparison" (TF-IDF vs BanglaBERT-weak vs BanglaBERT-LLM) into a **frozen pipeline release** paper. Key shifts:

| Original Plan | Current Reality | Why |
|---------------|----------------|-----|
| 3-model comparison on 120k Potrika calibration set | Frozen BENI v1 database (1.4M articles, Potrika + BNAD), TF-IDF production baseline vetted on 186 clean LLM labels | The database harmonization effort (BNAD merge, dedup, frozen IDs) became its own contribution |
| BanglaBERT-LLM as the star model | LLM labels are the **validation silver standard**, not training data for a third model | 22 positive examples (7.4% base rate) kills fine-tuning — the label-cost curve reveals this |
| Active learning as cost curve | Active learning shows a **flat null result** (F1 never exceeds 0.10 at any budget) | The base-rate problem means TF-IDF cannot learn the minority class from ≤300 examples |
| "Classification improvement → correlation improvement" hypothesis | Level correlations strong ($r = -0.75$ with CPI), first-differenced correlations insignificant | The null result is itself publishable |

The paper's contribution is now clearer:

| Layer | Original Plan | Actual Contribution |
|-------|---------------|-------------------|
| **T1** | Benchmark (3 models) | Frozen BENI v1 database + replicable pipeline template + 88.17% TF-IDF baseline |
| **T2** | Replicable LLM-assisted pipeline | Same — the frozen release IS the template |
| **T3** | Label-cost curve | **Flat curve is the finding** — base-rate problem shows LLM-assisted classification needs either (a) more labels, (b) stronger models, or (c) designed sampling beyond simple uncertainty |

---

## 2. What Is Done

### Code & Data Infrastructure
- ✅ BENI v1 database: 1,467,705 harmonised articles (Potrika + BNAD), deduplicated, dated, with frozen release versioning
- ✅ LLM silver standard: 299 articles annotated with Claude Sonnet 4, 186 clean labels after excluding 114 ambiguous rows
- ✅ Self-consistency evaluation: 96% agreement, $\kappa = 0.48$ (prevalence effect)
- ✅ TF-IDF + Logistic Regression: trained, validated at 88.17% acc, 0.823 F1 on Economic class
- ✅ Active learning simulation: 5-fold stratified CV, 25 trials per budget, flat curve documented
- ✅ Macro correlations: level ($r = -0.75$ CPI, $r = -0.72$ FX) and first-differenced ($r \approx 0.10$, n.s.)
- ✅ BENI v1 monthly index: article-weighted and source-balanced specifications, frozen

### Manuscript
- ✅ `drafts/introduction.tex` — Gap, motivation, preview
- ✅ `drafts/related_work.tex` — Positioned within text-as-data + low-resource NLP
- ✅ `drafts/methods.tex` — Pipeline architecture, data, 3 models (with BanglaBERT retained as legacy), active learning protocol, index construction, validation
- ✅ `drafts/results.tex` — Model comparison table, active learning curve (flat), macro correlations (null diffs)
- ✅ `drafts/discussion.tex` — Why levels work and diffs don't, base-rate ceiling, template framing
- ✅ `drafts/template.tex` — Step-by-step replicable pipeline guide
- ✅ `drafts/conclusion.tex` — Summary
- ✅ `main.tex` — Compiles all drafts, abstract finalized
- ✅ `references.bib` — Bibliography populated

---

## 3. What Remains (Finishing Sprint)

### Sprint A: Kaggle BanglaBERT (Priority: Highest — Blocks nothing if skipped, but strengthens the paper)

The current manuscript relegates BanglaBERT to "legacy prototype evidence." The original plan promised a BanglaBERT comparison. Decision needed:

| Option | Risk | Effort |
|--------|------|--------|
| **A1**: Run BanglaBERT on Kaggle T4 (~3 hrs), add to model comparison table | May not improve over TF-IDF (weak labels are noisy) | 4 hrs (setup + queue + collect) |
| **A2**: Keep BanglaBERT as legacy appendix — the paper is about the pipeline, not the model race | Reviewers may ask why the most obvious deep learning baseline is absent | 0 hrs |

**Recommended**: Run A1 as a robustness check. If BanglaBERT matches or beats TF-IDF, add it to Table 1. If it doesn't (possible given noisy weak labels), report it honestly and note the weak-label ceiling. This costs 4 hours and insulates against the reviewer question "why no BERT baseline?"

### Sprint B: Label-Cost Curve Finalization (Priority: High — T3 is the claimed novelty)

Current state: Active learning simulation shows a flat curve using TF-IDF. This is a **genuinely informative null result** — it shows that with ≤300 LLM labels and a 7.4% base rate, even the best weak-label classifier cannot learn the minority class.

What to add for completeness:
- [ ] **Uncertainty sampling curve**: Plot performance as a function of which articles are selected (random vs uncertainty vs diversity)
- [ ] **BanglaBERT active learning**: If Sprint A runs, try the same active learning protocol with BanglaBERT embeddings as the classifier (to test whether a stronger model changes the curve shape)
- [ ] **Cost table**: Convert annotation budget to USD (API costs + GPU hours) at each budget point
- [ ] **Recommendation threshold**: State clearly: "At k=300 LLM labels with a 7.4% base rate, linear classifiers cannot learn the minority class. Minimum viable budget is k ≥ 1,000 or a designed sampling strategy."

### Sprint C: Results Integration (Priority: High — Must be clean before submission)

- [ ] Integrate Sprint A results into `drafts/results.tex` if BanglaBERT runs
- [ ] Update correlation analysis if the frozen BENI v1 index changes after BanglaBERT integration
- [ ] Generate final figures (active learning curve, correlation scatter, timeline/diagram of pipeline)
- [ ] Run `main.tex` to PDF and verify all cross-references, tables, figures
- [ ] Spell-check and proofread all sections

### Sprint D: Submission Preparation (Priority: High — Submission target)

- [ ] Choose target venue. **Recommended**: arXiv preprint first (immediate citation + timestamp), then PLOS ONE (interdisciplinary, open access, high acceptance rate for methodology papers)
- [ ] Format for target venue (PLOS ONE: double-spaced, specific heading style, ORCID)
- [ ] Write abstract (exists — refine)
- [ ] Generate supplementary materials: full annotation prompt, economic keyword list, BENI v1 database schema
- [ ] Add data availability statement + code repository link
- [ ] Add author contributions / competing interests if required
- [ ] Create arXiv submission package (PDF + source files)

---

## 4. Updated Manuscript Map

| Section | Status | Notes |
|---------|--------|-------|
| 1. Introduction | ✅ Drafted | 1.5 pages — gap, motivation |
| 2. Related Work | ✅ Drafted | 1 page — text-as-data, low-resource, LLMs |
| 3. Data | ✅ Drafted | 1.5 pages — BENI v1, LLM labels, macro |
| 4. Methods | ✅ Drafted | 2 pages — pipeline, 3 models, active learning |
| 5. Results | ✅ Drafted (needs update) | 2 pages — add BanglaBERT if Sprint A, finalize cost curve |
| 6. Discussion | ✅ Drafted | 1 page — level vs diff, base rate, limitations |
| 7. Template | ✅ Drafted | 1 page — replicable guide |
| 8. Conclusion | ✅ Drafted | 0.5 page |
| Abstract | ✅ Drafted | Refined |
| Figures | ⚠️ Needs final pass | Active learning curve, correlation plot, pipeline diagram |
| References | ✅ Drafted | Populated |

---

## 5. Timeline (Finishing Sprint)

| Day | Tasks |
|-----|-------|
| **Day 1** | Set up Kaggle notebook with BENI v1 data + BanglaBERT. Queue training. |
| **Day 2** | Collect BanglaBERT results. Generate uncertainty sampling curves. Update results.tex. |
| **Day 3** | Run label-cost curve with BanglaBERT (if runtime). Write cost table. Generate all final figures. |
| **Day 4** | Proofread, format for PLOS ONE, generate arXiv package. |

**Total remaining effort**: 3–4 days (not weeks). The paper is 90% complete.

---

## 6. Target Venue Strategy

| Step | Venue | Timeline |
|------|-------|----------|
| **1. Preprint** | arXiv (cs.CL, econ.EM, stat.AP) | Immediate after finishing sprint |
| **2. Journal** | PLOS ONE | Submit September 2026 (after Paper 4 prototype is done) |

PLOS ONE fits because:
- Interdisciplinary (NLP + economics + development)
- High acceptance rate (~50%) for technically sound work
- Open access (fits the "replicable template" ethos)
- No novelty requirement — the pipeline + template contribution stands alone

---

## 7. Risks (Updated)

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| BanglaBERT doesn't improve over TF-IDF | Low | Medium (noisy weak labels) | Report honestly — "weak-label ceiling" is the finding |
| Reviewer: "Why no human gold standard?" | Low | Medium | LLM labels are transparently documented as silver standard; self-consistency reported; limitation acknowledged |
| Paper scope feels narrow (just one pipeline) | Medium | Low | Broaden framing: template for low-resource languages, not just Bangla |
| Active learning curve is a null result | Low | High | Null result is informative for the field — "you need >300 labels for rare-event classification" |
