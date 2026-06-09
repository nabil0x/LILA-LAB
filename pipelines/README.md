# LILA Lab Pipelines

## XENI Pipeline Collection

Each language gets its own **XENI** pipeline — [Language initial] + **E**xploration & **N**ative-language **I**ntelligence.

### Active Pipelines

| Pipeline | Language | Status | Accuracy | Index |
|----------|----------|--------|----------|-------|
| **BENI** | Bangla (বাংলা) | ✅ Active | 91.7% | 79 months (2014–2020) |
| **AENI** | Assamese (অসমীয়া) | 🔜 Planned | — | — |
| **NENI** | Nepali (नेपाली) | 🔜 Planned | — | — |
| **SENI** | Sylheti (চিটাঙ্গ) | 🔜 Planned | — | — |
| **CENI** | Chittagonian (চাঁটগাঁইয়া) | 🔜 Planned | — | — |

### Pipeline Structure

Each pipeline follows this structure:

```
[x]eni/
├── README.md              # Pipeline-specific documentation
├── annotation/            # LLM annotation pipeline
├── index/                 # Index construction
├── experiment/            # Model training & evaluation
├── data/                  # Pipeline-specific data
└── figures/               # Paper figures
```

### Shared Utilities

The `shared/` directory contains common code used across pipelines:

- `shared/annotation/` — Shared annotation tools
- `shared/classifiers/` — Shared classifier code
- `shared/utils/` — Common utilities

### Creating a New Pipeline

1. Copy the structure from `beni/`
2. Replace Bangla-specific code with your language
3. Update the annotation schema for your language
4. See `technical-reports/extensions/EXTENSION_TEMPLATE.md` for the full guide

### Language Priority

| Priority | Languages | Status |
|----------|-----------|--------|
| 🔴 High | Assamese, Nepali, Sylheti, Chittagonian | Seeking contributors |
| 🟡 Medium | Maithili, Odia, Meitei | Open to proposals |
| 🟢 Low | Other South Asian languages | Welcome anytime |

**Your language is underserved by current AI. Let's change that.**
