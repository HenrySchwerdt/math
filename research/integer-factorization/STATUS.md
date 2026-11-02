# Integer factorization — status

Open aspirational goal: uniform deterministic classical complete prime
factorization for all N ≥ 2, including multiplicities, in worst-case O(n log n)
bit operations, n = ⌈log₂ N⌉. See `HYP-111ffd30-5c77-4977-a4f4-9428f9ae40e1` and its report.

No mathematical result, bound improvement, implementation or experiment exists.
Bootstrap only prepared the shared research infrastructure.

## Next-session handoff

Read docs/HANDOFF.md and run `python scripts/research.py audit integer-factorization`.
First unfinished task: `TSK-8f7279d1-072e-4b0a-b03d-576460acab89`. Create a RUN and acquire its remote claim.
Then inspect the HYP report and task success criteria; define the bit/memory
model and retrieve primary baseline sources. No provider conversation is needed.
Blockers: no agreed computational model or sourced baseline yet. Failed research
approaches: none attempted. No workers or long experiments authorized yet.
