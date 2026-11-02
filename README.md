# Auditable mathematical research

A small provider-independent foundation for mathematical projects. Codex and
Claude Code share task definitions, evidence, reviews and Git-versioned state.
The first project is `research/integer-factorization`; no mathematical findings
or performance claims have been established during bootstrap.

Start with [the bootstrap guide](docs/BOOTSTRAP.md). Read the
[methodology](docs/METHODOLOGY.md), [handoff protocol](docs/HANDOFF.md),
[provider verification](docs/PROVIDERS.md) and [metadata contract](docs/SCHEMA.md).
Use `scripts/research.py audit PROJECT` for chronology and `--hypothesis ID` for
a linked-artifact view. See [concurrency](docs/CONCURRENCY.md) before starting work.

Validation: `.venv/bin/python scripts/research.py check` and
`.venv/bin/python -m unittest discover -s tests -v`. No research agents, database,
large orchestration service are needed for bootstrap.

Lean 4 is the formal proof environment; see [Lean setup and proof policy](docs/LEAN.md).
