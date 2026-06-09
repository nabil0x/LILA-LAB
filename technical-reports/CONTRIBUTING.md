# Contributing to Research Papers

This guide covers the standard workflows for contributing to any paper in this project. Each paper also has its own CONTRIBUTING.md with specific open tasks.

---

## 1. Screening Workflow (Papers 2 & 5)

Used when evaluating candidate papers for inclusion/exclusion in a systematic review.

### What you need
- A list of candidate papers (CSV with `title`, `authors`, `year`, `doi`, `abstract`)
- The paper's inclusion/exclusion criteria (see per-paper CONTRIBUTING)

### Steps

1. **Open the screening queue**: `technical-reports/contributions/paper{screening_log.csv`
2. **Screen each paper** by title + abstract (typically 30–60 seconds per paper)
3. **Record your decision**:
   - `decision`: `include` / `exclude` / `uncertain`
   - `exclusion_reason`: `out_of_scope` / `wrong_method` / `wrong_language` / `no_empirical` / `duplicate` / `unavailable`
   - `screened_by`: Your name or initials
   - `date`: ISO date
4. **Flag uncertain papers** for second review — mark `decision=uncertain` and add a note
5. Commit your batch

### Standard CSV format

```csv
paper_id,title,authors,year,decision,exclusion_reason,screened_by,date,notes
```

---

## 2. Data Extraction Workflow

Used to extract structured metadata from papers that passed screening.

### What you need
- The full text or detailed abstract of each included paper
- The paper's coding schema (`data/coding_schema.md` or `data/coding_schema.md`)

### Steps

1. **Open the extraction log**: `technical-reports/contributions/paper_extraction_log.csv`
2. **For each paper**, fill in:
   - **Theme/domain**: Broad research area (e.g., "Financial Economics", "Political Communication")
   - **Method**: Dictionary / ML / Transformer / LLM / Mixed
   - **Task**: Classification / Measurement / Prediction / Causal inference
   - **Target language**: Language of the text data used
   - **Geographic focus**: Country or region
   - **Validation method**: Out-of-sample / Manual annotation / External validation
   - **Key findings**: 1–2 sentence summary
   - **Extracted by**: Your name or initials
3. Commit your batch

### Standard CSV format

```csv
paper_id,title,year,method,task,language,geography,validation,findings,extracted_by,date
```

---

## 3. Writing Workflow

### File naming
- Manuscript files are LaTeX (`.tex`) in each paper's `manuscript/` directory
- Draft variants are in `drafts/` with descriptive names

### Process
1. Check `technical-reports/contributions/OWNERS.csv` for which sections have assigned writers
2. Announce your intent: create a row in `OWNERS.csv` with `role=Writer` and `task="Draft Section X"`
3. Write in the relevant `.tex` file
4. Compile to verify no LaTeX errors
5. Commit

---

## 4. Code/Replication Workflow

### For replications (Paper 2)
1. Check `technical-reports/paper2_systematic_review/replications/` for existing scripts
2. Run `python3 run_all_phases.py` to verify current state
3. Add your replication or improvement
4. Log in `OWNERS.csv` with `role=Replicator`

### For analysis scripts (Papers 3-4-6)
1. Scripts live in `beni/annotation/`, `beni/experiment/`, `beni/index/`, or per-paper `scripts/`
2. Document any changes in the script header
3. Log in `OWNERS.csv`

---

## Task-Specific Conventions

| Convention | Standard |
|------------|----------|
| **Date format** | ISO 8601: `2026-06-10` |
| **Contributor identifier** | Full name or consistent initials |
| **Uncertain papers** | Mark `decision=uncertain` — do not guess |
| **Batch size** | Screen 20–50 papers per session for consistency |
| **Extraction depth** | Whole paper coding = 5–15 min. Triage coding = 2–5 min. |
