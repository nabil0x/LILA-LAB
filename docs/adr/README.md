# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the LILA Lab project. ADRs document important architectural, design, and organizational decisions, including the context that motivated each decision, the option chosen, and the consequences of that choice.

## Why ADRs?

- **Transparency**: Every significant decision is documented with its rationale.
- **Onboarding**: New contributors can understand why the project is structured the way it is.
- **Institutional memory**: Decisions are preserved in version control alongside the code they affect.
- **Accountability**: Each ADR records who made the decision and when.

## ADR Format

We use the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records) lightweight format. Each ADR includes:

- **Title**: A unique identifier and descriptive name
- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: The forces at play and why the decision was needed
- **Decision**: The chosen approach
- **Consequences**: What becomes easier or harder as a result

See [template.md](template.md) for the canonical format.

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | XENI Pipeline Naming Convention | Accepted | 2025-01-15 |

## Proposing a New ADR

1. Copy [template.md](template.md) and fill in all sections.
2. Number sequentially (ADR-002, ADR-003, ...).
3. Submit a Pull Request with the proposed ADR.
4. ADRs are discussed and accepted by maintainer consensus.

## Status Definitions

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not yet accepted |
| Accepted | Formally adopted and in effect |
| Deprecated | Still valid but no longer recommended for new work |
| Superseded | Replaced by a newer ADR |
