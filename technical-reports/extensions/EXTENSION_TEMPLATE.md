# Extension Proposal Template

Use this template to propose a new language or domain extension to the XENI pipeline framework. Extensions that result in a validated pipeline and manuscript are eligible for first-author publication under the LILA Lab collaboration model.

Submit your completed proposal as a Pull Request to `technical-reports/extensions/` or discuss it on Discord before formalizing.

---

## Extension Proposal

### Language/Domain

*Specify the target language (for language extensions) or domain (for domain extensions). Include the ISO 639-3 language code if applicable, and the approximate number of speakers.*

### Motivation

*Why does this language or domain matter for narrative measurement? Describe the research gap, policy relevance, or scientific question this extension addresses. If a language extension, include current NLP resource availability (annotated corpora, pretrained models, etc.).*

### Data Sources

*List the planned data sources: news publishers, RSS feeds, web archives, social media, or other text repositories. Estimate the target corpus size and time coverage. Specify if data collection will use existing infrastructure (e.g., Potrika-style scraping) or requires new tooling.*

### Methodology

*Outline the planned approach:*
- *Annotation schema (domain-specific categories and definitions)*
- *LLM annotation protocol (models, prompting strategy, adjudication)*
- *Classifier training (model architecture, train/test split, evaluation metrics)*
- *Index construction (aggregation method, temporal smoothing, normalization)*
- *Validation strategy (macroeconomic or domain-specific benchmarks)*

### Team

| Role | Name | Affiliation | Expertise |
|------|------|-------------|-----------|
| Lead researcher | | | |
| Linguistic expert | | | |
| NLP engineer | | | |
| Domain expert | | | |

*Add rows as needed. At minimum, a lead researcher and a native speaker annotator are required for language extensions.*

### Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data collection | | |
| Annotation | | |
| Model training | | |
| Index construction | | |
| Validation | | |
| Manuscript writing | | |
| Submission | | |

### Expected Output

- *A functional XENI pipeline for the target language or domain*
- *A validated narrative index with quantitative accuracy and correlation metrics*
- *A manuscript suitable for journal submission*
- *Replication package (code, data references, documentation)*

---

## Submission Instructions

1. Copy this template and fill in all sections with substantive content.
2. Save as `technical-reports/extensions/[language-or-domain]-proposal.md`.
3. Add a row to `technical-reports/extensions/INDEX.md` reflecting your proposal.
4. Open a Pull Request with both changes.
5. The maintainers will review within two weeks and may request clarifications or suggest collaborators.

For help developing your proposal, join the [LILA Lab Discord](https://discord.gg/TrrdKbky) and post in the #extensions channel.
