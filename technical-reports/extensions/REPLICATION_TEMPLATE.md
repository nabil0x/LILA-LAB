# Replication Report Template

> Independently reproduce and validate results from the BENI research program.

---

## 1. Overview

| Field | Value |
|-------|-------|
| **Replication of** | [e.g., Paper 2: Systematic Review — 8 replication scripts] |
| **Replicator(s)** | [Your name(s)] |
| **Affiliation** | [Your institution] |
| **Date** | [YYYY-MM-DD] |
| **Environment** | [OS, Python version, key package versions] |

---

## 2. Replication Summary

| Result Claimed | Result Obtained | Match? | Notes |
|----------------|-----------------|--------|-------|
| [e.g., BERT RMSE improvement: +31.50%] | [Your value] | ✅/⚠️/❌ | [Any discrepancies] |
| [e.g., Tetlock replication: +7.52%] | [Your value] | ✅/⚠️/❌ | | |
| [e.g., Level correlation CPI: r=-0.75] | [Your value] | ✅/⚠️/❌ | | |

---

## 3. Verification Details

### Environment
```bash
# Your environment
python3 --version
pip3 freeze | grep -E "numpy|scikit-learn|torch|transformers|pandas"
```

### Execution
```bash
# Steps taken
cd technical-reports/paper2_systematic_review/replications/
python3 run_all_phases.py
# OR your modified approach
```

### Modifications (if any)
[Describe any changes you made to get the code to run]

---

## 4. Discrepancies Found

| Result | Expected | Got | Possible Cause |
|--------|----------|-----|----------------|
| | | | |

---

## 5. Verdict

- [ ] **Full replication**: All results match within rounding tolerance
- [ ] **Partial replication**: [N]/[M] results match; discrepancies documented
- [ ] **Failed replication**: Results could not be reproduced; causes documented

---

## 6. Innovation (Optional)

Did your replication reveal any insight beyond the original results?
[e.g., "During replication, I noticed that the TF-IDF model is highly sensitive to Bangla stopword selection. I tested 3 stopword lists and found performance varies by ±2%. This is a methodological insight the original paper did not explore."]

---

## 7. Files Added

| File | Description |
|------|-------------|
| `technical-reports/extensions/[your_replication]/replication_report.md` | This report |
| `technical-reports/extensions/[your_replication]/results/` | Your output files |
| `technical-reports/extensions/[your_replication]/scripts/` | Modified or additional scripts |

---

*Submit your replication report:*

```bash
mkdir -p technical-reports/extensions/[your_replication]/{results,scripts}
cp technical-reports/extensions/REPLICATION_TEMPLATE.md technical-reports/extensions/[your_replication]/README.md
echo "Your Name,Replicator,technical-reports/extensions/[your_replication],completed,2026-06-10,2026-06-15" >> technical-reports/contributions/OWNERS.csv
```
