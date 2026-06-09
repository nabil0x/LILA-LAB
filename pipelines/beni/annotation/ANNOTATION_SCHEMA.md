# BENI Annotation Schema

## Current (LLM reference labels — binary)

| Field | Type | Values |
|---|---|---|
| `economic_relevance` | binary | Economic / Not Economic |
| `confidence` | ordinal | 1 (guessing) / 2 (fairly sure) / 3 (certain) |
| `difficulty` | flag | Clear-cut / Borderline (conditional on Economic) |

## Planned (Phase 2 — multiclass expansion)

When ready, expand to the full schema defined in `.omo/plans/beni-definition-and-implementation.md`:

### Fields to add

| Field | Type | Values |
|---|---|---|
| `economic_topic` | multiclass (8) | `inflation`, `exchange_rate`, `reserves`, `banking`, `fiscal_policy`, `trade`, `employment`, `growth_investment`, `other` |
| `narrative_force` | multiclass (7) | `crisis`, `burden`, `blame`, `reform`, `stability`, `uncertainty`, `resilience`, `neutral` |
| `valuation_target` | multiclass (7) | `government`, `central_bank`, `banks`, `businesses`, `market_actors`, `global_economy`, `households`, `unnamed_system` |
| `sentiment` | ordinal | negative / neutral / positive |

### Quality target

- **LLM self-consistency / agreement target**: ≥ 0.8 on repeated or multi-model labels for economic relevance
- **Uncertainty review**: inspect low-confidence labels and cases where LLM, TF-IDF, and BanglaBERT disagree
- **Macro F1 targets**: economic_relevance ≥ 0.80, topic ≥ 0.75, narrative_force ≥ 0.60

### Expansion approach

1. Update `beni/annotation/label_config.xml` with new `Choices` blocks
2. Re-export tasks with `export_for_labelstudio.py --n 500 --econ-ratio 0.35`
3. Generate LLM labels with the same schema
4. Optionally review uncertain cases in LabelStudio UI (Settings → Import)

Reference: `beni/experiment/beni_pilot/narrative.py` for the canonical Bangla lexicons driving each label.
