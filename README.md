# Mathematical research laboratory — Claude handoff

Start with [the Claude handoff](docs/CLAUDE_START.md) and the
[full implementation mission](docs/LAB_MISSION.md). The primary project is ECDLP;
integer-factorization is preserved separately. The full laboratory is pending;
this repository currently supplies the tested bootstrap and clear starting tasks.

A small provider-independent foundation for mathematical projects. Codex and
Claude Code share task definitions, evidence, reviews and Git-versioned state.
The earlier project is `research/integer-factorization`; no mathematical findings
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

## Public research notebook

The [GitHub Pages research website](https://henryschwerdt.github.io/math/) uses
VitePress, with Markdown documentation, local search, open tasks, results and
evidence. Generate it from the shared ledger with
`.venv/bin/python scripts/research.py site`. See [website instructions](docs/WEBSITE.md).
GitHub Actions publishes updates committed to main.

Task progress is connected directly to the CLI: `research.py new` assigns a key,
`research.py task` updates status and records its reason, and `research.py exec`
records commands. The public task board and history are regenerated automatically
on main; agents do not edit website pages to report progress.
