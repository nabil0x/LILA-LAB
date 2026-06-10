# LILA Lab Roadmap

> Lab-wide development roadmap. Dates are targets, not guarantees. Items marked "seeking contributors" are open for collaboration.

---

## Q3 2026 (Jul-Sep)

### Paper Series

| Item | Status | Notes |
|------|--------|-------|
| **Paper 3: Building BENI Pipeline** | Active | Write up the full pipeline architecture, annotation methodology, classifier comparison, and index construction. Covers LLM annotation, active learning, and the TF-IDF baseline. |
| **Paper 4: Nowcasting Inflation with BENI** | Planned | Use the BENI Economic Index to nowcast CPI inflation. Compare against AR benchmarks and survey-based forecasts. Requires the full BanglaBERT index to be built first. |

### BENI Pipeline

| Item | Status | Notes |
|------|--------|-------|
| BanglaBERT full training on Kaggle | Pending | Run the full 70,000-article, 3-epoch BanglaBERT fine-tuning on a T4/P100 GPU. Currently wired but untrained. Estimated 2-3 hours on Kaggle. |
| Rebuild narrative index with BanglaBERT | Depends on above | Replace TF-IDF predictions with BanglaBERT predictions. Compare detrended correlations. |
| 300-article locked reference set | Planned | Manually annotate 300 articles for economic relevance, topic, and sentiment. Lock as the gold-standard evaluation set. |
| Active learning optimization | Planned | Use the reference set to run active learning loops, reducing the number of LLM annotations needed. |
| Paper 3 experiment notebooks | Active | Finalize all experiment notebooks and reproducible outputs for the Paper 3 manuscript. |

### Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| Website dashboard v1 | Planned | Deploy an interactive Streamlit dashboard showing the BENI index, macro correlations, and model performance metrics. |
| Publication bias correction | Planned | Implement trim-and-fill analysis on the 8 replications from the systematic review. Estimate true effect size. |

### Community

| Item | Status | Notes |
|------|--------|-------|
| AENI contributor recruitment | Seeking contributors | Reach out to Assamese-language researchers and linguists. Document Assamese news source landscape. |
| Discord bot deployment | In progress | Deploy the community bot for registration, contributor tracking, and notifications. |

---

## Q4 2026 (Oct-Dec)

### Paper Series

| Item | Status | Notes |
|------|--------|-------|
| **Paper 5: Text as Data in Social Science** | Planned | A systematic review of language-based methods from content analysis to LLMs (1916-2026). Covers the full methodological history. |
| **Paper 3 final submission** | Target | Submit the BENI pipeline paper to a journal or conference. |
| **Paper 4 final submission** | Target | Submit the nowcasting paper. Requires successful BanglaBERT results. |

### New Pipelines

| Item | Status | Notes |
|------|--------|-------|
| **AENI pipeline bootstrap** | Seeking contributors | Build the first Assamese news corpus (minimum 1,000 articles). Adapt the BENI annotation schema for Assamese economic narratives. Run the LLM annotation pipeline. |
| AENI baseline classifier | Seeking contributors | Train initial TF-IDF model on Assamese data. Establish baseline accuracy. |
| Pipeline template documentation | Planned | Improve the pipeline template with step-by-step instructions, example data, and a getting-started guide. |

### Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| Website dashboard v2 | Planned | Add interactive time-series exploration, model comparison views, and downloadable index CSVs. |
| Reproducibility dashboard | Planned | Unified interface comparing all 8 replications plus BENI across accuracy, RMSE improvement, interpretability, and speed. |
| REST API for BENI index | Proposed | Expose the narrative index programmatically for external researchers and policy users. |

### Community

| Item | Status | Notes |
|------|--------|-------|
| Policy brief pilot | Planned | Write the first policy brief: "What Bangla news narratives tell us about inflation expectations." Target: Bangladesh Bank researchers and Ministry of Finance. |
| NENI and SENI exploration | Seeking contributors | Identify news sources and linguistic experts for Nepali and Sylheti pipelines. |

---

## H1 2027 (Jan-Jun)

### Paper Series

| Item | Status | Notes |
|------|--------|-------|
| **Paper 6: LLMs as Measurement Devices** | Proposed | Framework paper on using LLMs for structured narrative extraction in low-resource languages. Methodological and theoretical. |
| **Paper 5 final submission** | Target | Submit the Text as Data survey. |
| Cross-language comparison paper | Proposed | Compare narrative indices across Bangla, Assamese, and Nepali. Requires AENI and NENI pipelines to be operational. |

### New Pipelines

| Item | Status | Notes |
|------|--------|-------|
| **NENI pipeline launch** | Seeking contributors | Nepali news corpus, annotation schema, LLM annotation, and baseline classifier. |
| **SENI pipeline launch** | Seeking contributors | Sylheti pipeline bootstrap. |
| **CENI pipeline launch** | Seeking contributors | Chittagonian pipeline bootstrap. |

### Cross-Domain Indices

| Item | Status | Notes |
|------|--------|-------|
| BENI Health Index prototype | Proposed | Adapt the annotation schema for health discourse. Collect health-related news from the existing Potrika corpus. |
| BENI Climate Index prototype | Proposed | Same approach, targeting climate and environmental narratives. |
| Cross-domain methodology paper | Proposed | Document how the pipeline generalizes across domains. Include validation strategies for non-economic indices. |

### Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| Website dashboard v3 | Planned | Add cross-pipeline comparison views, health/climate index tabs, and real-time news feed. |
| Mobile-friendly dashboard | Proposed | Responsive design for policy users on mobile devices. |
| Automated weekly narrative reports | Proposed | Generate and distribute weekly summaries of narrative trends. |

### Community

| Item | Status | Notes |
|------|--------|-------|
| University course module | Proposed | Create Jupyter notebook tutorials based on the BENI pipeline for NLP and economics courses. |
| Contributor workshop series | Proposed | Online workshops for linguistic contributors: data collection, annotation, and validation. |
| Open data release v2.0 | Planned | Release expanded Potrika-derived datasets with LLM annotations and classifier predictions. |

---

## Ongoing

### Pipeline Maintenance

- Maintain and improve the TF-IDF baseline and BanglaBERT integration
- Update macroeconomic indicator data (CPI, FX, reserves) as new data becomes available
- Fix bugs and respond to GitHub Issues
- Review and merge community contributions

### Dataset Expansions

- Extend the Potrika-derived annotation set with additional articles
- Curate and release annotated datasets in batches
- Maintain the locked reference set as the gold standard for evaluation
- Acquire and process news data for new time windows beyond 2020

### Community Growth

- Maintain Discord community and recruit contributors
- Process linguistic data submissions (text corpora, annotations, dialectal documentation)
- Update contributor records in `technical-reports/contributions/OWNERS.csv`
- Respond to collaboration inquiries and research proposals

### Infrastructure Reliability

- Monitor Discord bot uptime and functionality
- Keep the website dashboard operational
- Maintain reproducible experiment pipelines (seed control, deterministic preprocessing)
- Expand the replication suite from 8 to 15-20 replication studies

### Publication Pipeline

- Revise and resubmit papers as needed
- Respond to reviewer feedback on submitted manuscripts
- Prepare and submit policy briefs and extension reports
- Maintain citation metadata in `CITATION.cff`

---

## How to Get Involved

| If you want to... | Start here |
|-------------------|-----------|
| Start a pipeline for your language | [`pipelines/template/`](pipelines/template/) + [`COLLABORATION.md`](COLLABORATION.md) |
| Contribute linguistic data | [`LINGUISTIC_CONTRIBUTION_GUIDE.md`](LINGUISTIC_CONTRIBUTION_GUIDE.md) |
| Improve the classifier | [`pipelines/beni/experiment/beni_pilot/`](pipelines/beni/experiment/beni_pilot/) |
| Build the website or tools | [`infrastructure/`](infrastructure/) |
| Write a policy brief | Open an issue or email lila.lab0x@gmail.com |
| Replicate or validate results | [`technical-reports/extensions/REPLICATION_TEMPLATE.md`](technical-reports/extensions/REPLICATION_TEMPLATE.md) |

See the full BENI pipeline roadmap at [`pipelines/beni/BENI_ROADMAP.md`](pipelines/beni/BENI_ROADMAP.md) for granular BENI-specific research milestones.
