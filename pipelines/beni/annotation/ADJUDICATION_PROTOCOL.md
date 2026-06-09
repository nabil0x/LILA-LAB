# BENI LLM Label Validation Protocol

**Purpose**: Validate LLM-generated labels and produce a locked LLM reference label set for the 300-article BENI validation batch.

This project does not require two human annotators. The publishable framing is therefore **LLM reference labels**, not a human gold standard. The protocol below documents how label quality is checked transparently.

---

## 1. Validation Strategy

Use three complementary checks:

| Check | Purpose | Output |
|---|---|---|
| LLM self-consistency | Measures whether repeated LLM labeling gives the same answer | Agreement rate / kappa-like agreement |
| Model disagreement | Finds articles where LLM, TF-IDF, and BanglaBERT disagree | Review queue |
| Confidence and ambiguity flags | Identifies cases that should not be treated as clean labels | Uncertain/ambiguous subset |

The main paper should report these checks instead of inter-annotator agreement.

---

## 2. Label Locking Rules

Each article receives one final reference label using this priority order:

| Scenario | Final rule |
|---|---|
| LLM confidence is high and model predictions agree | Lock the LLM label |
| LLM confidence is high but models disagree | Lock the LLM label and flag `model_disagreement=true` |
| LLM confidence is low | Flag `uncertain=true`; include in sensitivity analysis |
| Repeated LLM passes disagree | Use majority vote if available; otherwise flag `ambiguous=true` |
| Article is genuinely mixed | Keep the best label but include a note explaining the ambiguity |

Do not force every article to be clean. Ambiguous cases are useful evidence about the limits of the schema.

---

## 3. Agreement Metrics

Report agreement between systems rather than between human annotators:

| Metric | Comparison |
|---|---|
| Observed agreement | LLM vs TF-IDF, LLM vs BanglaBERT, TF-IDF vs BanglaBERT |
| Cohen's kappa | Pairwise system agreement, with class imbalance caveat |
| Precision/recall/F1 | Model performance when LLM labels are treated as the reference |
| Disagreement count | Number of cases requiring uncertainty review |

Kappa can look low when the economic class is rare, even with high observed agreement. Always report base rates.

---

## 4. Review Queue

Prioritize articles for review when any condition holds:

1. LLM confidence is low.
2. LLM label differs from both TF-IDF and BanglaBERT.
3. TF-IDF and BanglaBERT agree against the LLM.
4. The article has short text, missing text, or mixed political/economic framing.
5. The article is classified as Economic but the topic/sentiment/frame is uncertain.

The review queue is a quality-control artifact. It does not imply a full human annotation requirement.

---

## 5. Deliverables

After validation, produce:

1. `exports/llm_assisted_300_annotations.jsonl` — locked 300-article LLM reference labels.
2. `exports/llm_assisted_300_summary.json` — label counts, method name, and output paths.
3. `exports/analysis_report.txt` — LLM/model agreement and disagreement summary.
4. `exports/model_comparison.txt` — TF-IDF, BanglaBERT, and LLM comparison.
5. `exports/beni_v0_1_review_queue.csv` — low-confidence or disagreement cases.

---

## 6. Publication Language

Use:

- "LLM-labeled reference set"
- "LLM-assisted annotation"
- "self-consistency and model-disagreement validation"
- "uncertainty review"

Avoid:

- "human gold standard"
- "inter-annotator agreement" unless human labels are later added
- "adjudicated gold labels" unless an independent adjudication step is actually performed

Suggested methods sentence:

> We construct a 300-article LLM-labeled reference set using a fixed economic relevance schema, then validate label quality through confidence scores, repeated-label consistency, and disagreement analysis against TF-IDF and BanglaBERT baselines.
