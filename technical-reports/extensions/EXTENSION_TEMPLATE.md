# Extension Template — [Language/Domain] Narrative Index

> Use this template to propose and structure a research extension to the BENI program.
> Replace all bracketed text with your content.

---

## 1. Overview

| Field | Value |
|-------|-------|
| **Extension title** | [e.g., Building an Assamese Economic Narrative Index] |
| **Type** | Language Extension / Cross-Domain / Methodological |
| **Lead contributor(s)** | [Your name(s)] |
| **Affiliation** | [Your institution] |
| **Target language** | [e.g., Assamese (অসমীয়া)] |
| **ISO 639-3 code** | [e.g., asm] |
| **Estimated speakers** | [e.g., 15,000,000] |
| **Primary region** | [e.g., Assam, India] |
| **Date proposed** | [YYYY-MM-DD] |

---

## 2. Research Question

> What is the central question this extension answers?

Example: *Does an Assamese-language economic narrative index correlate with Assam's macroeconomic indicators, and how does the narrative structure differ from Bangla?*

---

## 3. Innovation Statement

> What is novel about this extension? (1–2 sentences)

Example: *This is the first economic narrative index for any language of Northeast India. It will reveal whether economic narratives in Assamese follow different topical patterns than Bangla — testing whether narrative economics generalizes across closely related but culturally distinct languages.*

---

## 4. Data Plan

| Requirement | Your Plan |
|-------------|-----------|
| Source corpus | [e.g., Assamese newspapers — Axomiya Pratidin, Niyomiya Barta] |
| Target size | [e.g., 10,000 articles] |
| Date range | [e.g., 2014–2020] |
| Collection method | [e.g., Web scraping, existing corpus, archive] |
| Annotation plan | [e.g., Lead contributor annotates 1,000 articles, LLM annotates remainder] |
| Macro data sources | [e.g., Assam CPI, INR exchange rate, state GDP] |

---

## 5. Methodology

> How will you adapt the BENI pipeline?

- [ ] **No modification needed** — BENI pipeline works as-is for this language
- [ ] **Minor modification** — adjust stopwords, tokenizer, or annotation schema
- [ ] **Major modification** — describe changes

Describe your methodology:

```
[Your approach. Reference specific scripts in beni/ that you will use or modify.]
```

---

## 6. Expected Contributions

| Layer | Contribution |
|-------|-------------|
| **T1: Benchmark** | First [language] economic NLP benchmark |
| **T2: Evidence** | Cross-language comparison with Bangla — do narratives work the same way? |
| **T3: Infrastructure** | [Language] corpus + annotations added to the shared resource pool |

---

## 7. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data collection | [X weeks] | Corpus of [N] articles |
| Annotation | [X weeks] | [N] annotated articles |
| Pipeline adaptation | [X weeks] | Working [language] index |
| Analysis | [X weeks] | Results + validation |
| Writing | [X weeks] | Manuscript draft |

---

## 8. Collaboration Model

- [ ] **Git merge** — I will fork, develop, and submit a PR to this repository
- [ ] **Git submodule** — I maintain my own repo; request to be linked as submodule
- [ ] **Paper submission** — I will collaborate on a paper for external publication

---

## 9. Status

| Item | Status |
|------|--------|
| Proposal submitted | [ ] |
| Data collection started | [ ] |
| Pipeline run | [ ] |
| Results validated | [ ] |
| Manuscript written | [ ] |
| Submitted for publication | [ ] |

---

## 10. Contributors

| Name | Role | ORCID / Contact |
|------|------|-----------------|
| [You] | Lead | [your email/ORCID] |
| [Co-contributor] | [Role] | [contact] |

---

*After filling this template, create your extension directory and start developing:*

```bash
mkdir -p technical-reports/extensions/[your_extension_name]/{data,scripts,manuscript,results}
cp technical-reports/extensions/EXTENSION_TEMPLATE.md technical-reports/extensions/[your_extension_name]/README.md
echo "Your Name,Extension Author,technical-reports/extensions/[your_extension_name],in_progress,2026-06-10," >> technical-reports/contributions/OWNERS.csv
```
