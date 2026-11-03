# Start with either provider

For the current ECDLP mission, read docs/CLAUDE_START.md first. The older
factorization bootstrap example below remains available for that separate project.

Requires Python 3.11+, Git, Elan/Lean 4 (see LEAN.md), and the selected authenticated CLI. From repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/research.py check
.venv/bin/python scripts/research.py audit integer-factorization
lake build
```

Start `codex` (project config selects Sol) or `claude` (project settings select
Opus), then send the same task prompt:

> Read AGENTS.md and docs/HANDOFF.md. Resume research/integer-factorization from
> its repository state. Do the first unfinished TSK only after recording a RUN
> and acquiring its remote claim. Follow its scope and success criteria. Do not
> start parallel workers until a bounded budget is authorized. Finish with ledger
> evidence and an actionable cross-provider handoff.

If Claude has no credentials, run `claude auth login` first and resolve any
user-level diagnostics described in PROVIDERS.md.

Confirm the actual selected model and agent loading in the CLI. Project settings
may require workspace trust; managed/user settings or environment overrides can
change effective models. Stop on mismatch; never silently downgrade. See
PROVIDERS.md for version requirements and validation limits.

## A second project

`python scripts/research.py init example-project` creates the same generic
layout and status/backlog starters. Then create a TSK and a HYP using `new`, fill
in scope/definitions/success criteria and update STATUS/BACKLOG. Replace example
content with the new project's question. All common tooling and role adapters
remain unchanged. No factoring assumptions live in shared infrastructure.

```sh
python scripts/research.py new example-project TSK
python scripts/research.py new example-project HYP
python scripts/research.py new example-project RUN
```

Templates and required metadata are in research/_templates and docs/SCHEMA.md.
