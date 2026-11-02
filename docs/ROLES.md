# Equivalent roles

| Shared role | Codex | Claude Code |
| --- | --- | --- |
| principal-investigator, final-reviewer | gpt-6.1-sol | claude-opus-5-5 |
| research-worker, implementer, experimenter, adversarial-critic | gpt-6-luna | claude-sonnet-5-5 |

Each adapter reads the corresponding `docs/roles/<role>.md`. Those files and
METHODOLOGY.md, not provider-specific prompts, define success. Workers receive
the task ID, exact question, inputs, success criteria, owned files/worktree,
run ID and resource limit. Independent critics receive neutral claim/evidence
packets rather than the author's confidence assessment. PI/final reviewer
integrates only after a separate review. Bootstrap is infrastructure only.
