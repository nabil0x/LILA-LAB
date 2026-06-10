# Replication Report Template

Independent replication is a cornerstone of scientific credibility. This template provides a standard format for reporting replication results for any LILA Lab paper or extension. Replication reports are peer-reviewed by the maintainers and, if accepted, become part of the permanent repository record.

Submit your completed report as a Pull Request to `technical-reports/extensions/` or email it to [lila.lab0x@gmail.com](mailto:lila.lab0x@gmail.com).

---

## Replication Report

### Original Paper

- **Title:** 
- **Authors:** 
- **Repository version/commit:** 
- **DOI or URL:** 

### Replicator

- **Name:** 
- **Affiliation:** 
- **Contact:** 
- **Date:** 

### Methodology

*Describe the replication approach:*
- *Did you use the original code as-is, or did you re-implement from the paper description?*
- *Which parts of the analysis were replicated (full or partial)?*
- *What software and hardware environment was used (OS, Python version, package versions, GPU)?*

### Findings

*Summarize the replication results:*

| Metric | Original | Replicated | Difference |
|--------|----------|------------|------------|
| *e.g., Classification accuracy* | *91.7%* | *91.5%* | *−0.2 pp* |
| *e.g., CPI correlation* | *r = −0.75* | *r = −0.73* | *+0.02* |

*Include key figures or tables as appropriate. If results are substantially different, discuss possible causes.*

### Discrepancies

*Document any discrepancies between the original and replication results. For each discrepancy, note:*
- *What differs*
- *Likely cause (e.g., software version differences, random seed, data version, interpretation)*
- *Whether the discrepancy changes the substantive conclusions*

*If no discrepancies were found, state "No material discrepancies identified."*

### Conclusion

*State clearly whether the original findings are reproduced, partially reproduced, or not reproduced. Include a brief assessment of what this means for the paper's conclusions.*

- [ ] **Fully reproduced** — all key results match within expected tolerance
- [ ] **Partially reproduced** — some results match, others differ
- [ ] **Not reproduced** — material differences that affect conclusions

### Materials

- **Replication code repository:** 
- **Replication data location:** 
- **Instructions for running the replication:** 

---

## Submission Instructions

1. Complete this template with substantive detail.
2. Save as `technical-reports/extensions/replication-[paper-name]-[your-name].md`.
3. Open a Pull Request or email the completed report.
4. The maintainers will review and, if accepted, link the report from the original paper's README.

Accepted replication reports earn the replicator an authorship credit or formal acknowledgment, depending on the scope of work (see [COLLABORATION.md](../../COLLABORATION.md)).
