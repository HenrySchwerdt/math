# Platform handoff

Bootstrap commit `bef6840627e790a5a96e8332e50227474c6365cc` is on origin/main. Upgrade branch:
`codex/ecdlp-research-laboratory`. Start Claude with docs/CLAUDE_START.md.
The primary project is now ECDLP; preserve integer-factorization unchanged.

Bootstrap tests and Lean smoke check passed; independent exact-commit re-review
failed due provider usage limit and remains pending. The full laboratory mission
is not yet implemented. The current task is `TSK-9f6a9ba1-1a55-4111-b9be-ec9af0e4a5a4`.

## Public research notebook

Live: https://henryschwerdt.github.io/math/ — VitePress, matching Mini's docs
framework/style, with local search and generated research/task/result/evidence
pages. Website task TSK-3b0320e8-17b1-447f-80e5-d9f0f2770613 is complete.
Python command: `.venv/bin/python scripts/research.py site`. Updates on main
automatically publish via `.github/workflows/pages.yml`. Read docs/WEBSITE.md.
Independent website Python/integration reviews accepted candidate d116b7c.
Earlier quota-blocked bootstrap runs remain historical records. The full ECDLP
laboratory implementation remains open; website delivery is infrastructure only.

Task board and CLI integration complete: LAB-3. Project-scoped keys are persisted
in TASKS.json. `research.py task` records status/outcome/reason/history; `exec`
records command steps; main commits automatically regenerate the public site.
The homepage now uses task status columns and factual copy. 25 tests, independent
Python/Vue reviews and production deployment passed. No research proof claimed.
