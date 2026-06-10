# ADR-001: XENI Pipeline Naming Convention

**Status:** Accepted

**Date:** 2025-01-15

## Context

As the LILA Lab project expands beyond the initial Bangla pipeline, a consistent naming convention is needed for multi-language pipeline instances. Without a standard convention, each new language pipeline risks introducing ad-hoc names that obscure the relationship between pipelines and make the framework harder to navigate for contributors and users.

The naming convention must satisfy several requirements:

- **Identifiability**: The name should make the target language immediately recognizable.
- **Extensibility**: The pattern must accommodate an arbitrary number of languages without breaking down.
- **Brand cohesion**: All pipelines should be visually and verbally identifiable as part of the same framework.
- **Discoverability**: The naming should make it easy to find pipeline code and reference it in documentation.

Several alternatives were considered: numeric indices (P1, P2, ...), geographic groupings (South Asian NLP), and purely descriptive names. Each had shortcomings: numeric indices require a lookup table, geographic groupings exclude future non-South-Asian languages, and descriptive names are too verbose for code and CLI use.

## Decision

We adopt the **XENI** naming convention:

**XENI = [Language initial] + "ENI" (Exploration & Native-language Intelligence)**

Where [Language initial] is the first letter of the language name in English, uppercase.

### Examples

| Pipeline | Language | Breakdown |
|----------|----------|-----------|
| **BENI** | Bangla (Bengali) | **B** + ENI |
| **AENI** | Assamese | **A** + ENI |
| **NENI** | Nepali | **N** + ENI |
| **SENI** | Sylheti | **S** + ENI |
| **CENI** | Chittagonian | **C** + ENI |
| **HENI** | Hindi | **H** + ENI |

### Derived nomenclature

| Element | Convention | Example |
|---------|-----------|---------|
| Pipeline directory | `pipelines/[x]eni/` | `pipelines/beni/` |
| Narrative index | XENI [Domain] Index | BENI Economic Index |
| Annotation pipeline | `pipelines/[x]eni/annotation/` | `pipelines/beni/annotation/` |

## Consequences

### Positive

- **Highly extensible**: Any new language requires only the single-letter initial. Adding Urdu (UENI), Burmese (MENI), or Thai (TENI) is trivial.
- **Self-documenting**: The name encodes both the framework (ENI) and the language (initial letter).
- **Short and CLI-friendly**: Four-character pipeline names are easy to type, tab-complete, and use in scripts.
- **Brand cohesion**: All pipelines share the "ENI" suffix, creating a recognizable family.

### Negative

- **Initial collision**: Languages sharing the same initial (e.g., Bengali and Bangla — both B) require disambiguation. We resolve this by using "BENI" for Bangla (the endonym's English form) and noting in documentation that "BENI" refers to the Bangla language pipeline. If a second B-initial language is added (e.g., Bhojpuri), we would use the full ISO 639-3 code or a two-letter abbreviation on a case-by-case basis.
- **English-centric**: The convention assumes the English name of the language. Languages whose English names differ significantly from endonyms (e.g., Burmese vs. Myanmar) use the English form for consistency.
- **Non-obvious for newcomers**: Users unfamiliar with the convention may not immediately recognize that BENI stands for Bangla + ENI. This is mitigated by the README and the ADR itself being prominently linked from the project root.
