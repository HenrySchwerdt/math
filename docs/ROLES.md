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

## Scientific laboratory roles

Shared role files and native adapters now also define discovery,
algebraic-geometry, group-theory, number-theory, complexity-theory,
algorithm-engineering, counterexample, independent-reviewer and formalization.
All routine roles use Luna/Sonnet; independent-reviewer uses Sol/Opus.
Adapters contain references, not duplicated scientific policy. Actual live
spawning/independence remains to be demonstrated in the first vertical slice.

## Frontier exploration

`frontier-explorer` (Luna/Sonnet) is a standing role for deliberately unconventional but testable
ideas outside the directions already investigated. It must name the barrier assumption each idea
escapes, run the cheapest decisive test for its best ideas, and report negative results with equal
weight. Its outputs enter the normal falsification and review pipeline like any other hypothesis.

Scientific write-ups follow docs/PAPERS.md (draft by a worker, blind adversarial and independent manuscript review, PI integration; no external submission without human approval).

## Algorithm invention (primary since the round-11 strategic correction)

`algorithm-inventor` (Luna/Sonnet) produces concrete candidate algorithms with mechanism, prototype,
correctness argument, explicit complexity model, a measured scaling comparison against Pollard rho,
and — if unsuccessful — the exact obstacle. It is the lab's primary role; lower-bound work is only
pursued when it unblocks a concrete candidate.

Orchestrators follow docs/WORKFLOW.md for packages, pull requests and merges.
