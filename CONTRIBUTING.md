# Contributing to LILA Lab

Thank you for contributing to this project. Every contribution — whether screening papers, running replications, extracting data, or writing — moves us toward a shared goal: measurement infrastructure for data-scarce economies.

---

## Quick Start

1. **Pick a paper** → `technical-reports/` has per-paper CONTRIBUTING guides with open tasks
2. **Log your contribution** → Add a row to `technical-reports/contributions/OWNERS.csv` with your name and what you're working on
3. **Record decisions** → Use the CSV templates in `technical-reports/contributions/` to log each paper you screen or extract
4. **Submit** → Commit your changes with a descriptive message

---

## Contribution Types

| Type | Description | Tracked In |
|------|-------------|------------|
| **Linguistic data** | Submit native-language text, annotations, dialect expertise | `technical-reports/contributions/linguistic_data/` + `OWNERS.csv` |
| **Screening** | Include/exclude decisions for candidate papers | `technical-reports/contributions/paper{screening_log.csv}` |
| **Data extraction** | Coding metadata from included papers | `technical-reports/contributions/paper_extraction_log.csv` |
| **Replication** | Running or validating replication code | `technical-reports/contributions/OWNERS.csv` |
| **Writing** | Drafting or editing manuscript sections | `technical-reports/contributions/OWNERS.csv` |
| **Code** | Writing/modifying analysis scripts | `technical-reports/contributions/OWNERS.csv` |
| **Review** | Commenting on drafts or results | `technical-reports/contributions/OWNERS.csv` |

---

## Ownership & Credit

Every contribution is recorded in `technical-reports/contributions/OWNERS.csv`:

| Field | What to enter |
|-------|---------------|
| `name` | Your name (as you want it in acknowledgements) |
| `role` | Screener / Extractor / Replicator / Writer / Reviewer |
| `paper` | Which paper (e.g., `paper2`, `paper5`) |
| `task` | Specific task (e.g., "screen 301 Crossref candidates", "extract era 4-6 papers") |
| `status` | `in_progress` / `completed` / `verified` |
| `date_started` | ISO date |
| `date_completed` | ISO date |

This log is the source of truth for authorship and acknowledgement decisions.

---

## Principles

- **Transparency**: All decisions (include/exclude, coding choices) are recorded in CSV files with contributor initials
- **Reviewability**: Every screening decision and extraction can be traced back to the contributor
- **Low ceremony**: A CSV row is sufficient — no forms, no accounts
- **Git-native**: All contribution records live in the repo, versioned alongside the work
- **Extensible**: New paper → add its log templates to `technical-reports/contributions/`

---

## Further Reading

| Guide | What it covers |
|-------|---------------|
| `COLLABORATION.md` | **START HERE** — 8 research contribution models that lead to co-authorship |
| `LINGUISTIC_CONTRIBUTION_GUIDE.md` | How linguistic experts can contribute native-language data |
| `SUBREPOS.md` | How to link your independent repository as a git submodule |
| `technical-reports/extensions/INDEX.md` | Registry of active research extensions |
| `technical-reports/extensions/EXTENSION_TEMPLATE.md` | Template for proposing a language/domain + publishing a paper |
| `technical-reports/extensions/REPLICATION_TEMPLATE.md` | Template for independently validating our results |
| `technical-reports/CONTRIBUTING.md` | Standard workflows for all papers |
| `technical-reports/paper2_systematic_review/CONTRIBUTING.md` | Paper 2 specific tasks |
| `technical-reports/paper5_text_as_data_survey/CONTRIBUTING.md` | Paper 5 specific tasks |
| `technical-reports/contributions/OWNERS.csv` | Who owns what |
