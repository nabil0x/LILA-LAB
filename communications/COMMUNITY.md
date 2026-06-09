# LILA Lab — Community & Contributor Coordination

> How contributors coordinate, ask questions, and collaborate — across Discord, email, and the repo itself.

---

## Philosophy

LILA Lab is a **research collective**, not a typical open-source project. Contributors are co-authors, not drive-by pull requesters. The community infrastructure reflects this:

- **Low barrier to entry** — native speakers contribute annotations, not code
- **High recognition** — every contribution is recorded in `OWNERS.csv` and acknowledged in papers
- **Asynchronous by default** — most coordination happens in GitHub issues + Discord channels
- **Synchronous when needed** — monthly lab calls for active contributors

---

## Channels

### Discord (`discord.gg/TrrdKbky`)

The primary real-time coordination space. 

| Channel | Purpose |
|---------|---------|
| `#welcome` | Newcomer onboarding, rules, link to `COLLABORATION.md` |
| `#announcements` | New papers, dataset releases, contributor milestones (read-only) |
| `#general` | Q&A, discussion, ideas — open to all |
| `#linguistic-data` | Coordinate annotation tasks, ask language-specific questions |
| `#pipelines` | Technical discussion — BENI, AENI, pipeline development |
| `#extensions` | Discussion of proposed and in-progress extension papers |
| `#paper-writing` | Drafting, review requests, citation questions |
| `#monthly-lab-call` | Agenda and notes for monthly video calls |

**Discord Guidelines:**
1. Be respectful. This is an academic community.
2. Keep language-specific questions in their relevant threads.
3. Before asking a technical question, check if it's answered in the repo docs first.
4. Share your contributions openly — we celebrate progress, not just completion.
5. No spam, no self-promotion of unrelated projects.

### GitHub Issues

For structured, persistent coordination:

| Issue Type | When to Use | Label |
|-----------|-------------|-------|
| Bug report | Pipeline code doesn't work as expected | `bug` |
| Extension proposal | Proposing a new language/domain pipeline | `extension` |
| Data request | Need access to a dataset or source | `data` |
| Question | How do I...? | `question` |
| Contribution | I want to contribute X language data | `contribution` |

### Email (`lila.lab0x@gmail.com`)

For direct inquiries that don't belong in public channels:
- Collaboration proposals from institutions
- Media inquiries
- Sensitive data sharing arrangements

### Monthly Lab Call

For active contributors working on papers and extensions.

| Detail | Value |
|--------|-------|
| **Frequency** | First Friday of each month |
| **Duration** | 60 minutes |
| **Format** | 30 min updates → 30 min open discussion |
| **Platform** | Google Meet / Zoom (link posted in Discord `#monthly-lab-call`) |
| **Agenda** | Posted 1 week in advance as GitHub Discussion |

---

## Contributor Onboarding Flow

```
New person arrives (Discord / GitHub / Email)
    │
    ├── 1. Read COLLABORATION.md — 8 contribution models
    ├── 2. Read LINGUISTIC_CONTRIBUTION_GUIDE.md (if linguist)
    ├── 3. Browse technical-reports/extensions/INDEX.md — active extensions
    ├── 4. Introduce yourself in Discord #welcome
    ├── 5. Choose contribution model
    ├── 6. Record intent in OWNERS.csv
    └── 7. Start contributing — we help along the way
```

---

## Recognition & Credit

| Contribution Type | Recognition |
|-------------------|-------------|
| Linguistic data submission | Listed in `OWNERS.csv` + acknowledged in relevant papers |
| Annotation work | Listed in `OWNERS.csv` + co-authorship if 500+ annotations |
| Extension pipeline (new language) | First-author on extension paper + entry in INDEX.md |
| Methodological improvement | Co-authorship on technical report |
| Replication study | First-author replication report in extensions/ |
| Code contribution | Listed in CONTRIBUTORS.md + release notes |
| Community support (Discord) | Listed in `OWNERS.csv` as Community Contributor |

---

## Code of Conduct

All LILA Lab spaces (Discord, GitHub, email, calls) follow this simple code:

1. **Respect boundaries.** Not everyone is on the same schedule, time zone, or expertise level.
2. **Assume good faith.** Most disagreements are about method, not values.
3. **Credit others.** If someone helped you, acknowledge them.
4. **No hierarchy of contributions.** The annotator who labels 100 articles is as valued as the researcher who built the pipeline.
5. **Harassment of any kind is not tolerated.**

Report violations to lila.lab0x@gmail.com. Reports are handled confidentially.
