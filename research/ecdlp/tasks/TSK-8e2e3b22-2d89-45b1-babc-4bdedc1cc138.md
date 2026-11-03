# TSK-8e2e3b22-2d89-45b1-babc-4bdedc1cc138 — Round 11 / ECDLP-39: algebraic decision-tree barrier (branching) and batched SLP review

Status: completed; proof status: not-applicable; outcome: verified.

## Question, selection rationale and inputs
Algebraic decision-tree barrier (conjecture): any algebraic decision tree over F_p with equality branching (tests f(u) = 0 on intermediate values), single input u = x(Q), depth D and leaf programs of length L (with division defined on their leaf sets), that outputs k at u = x(kP) for 1 <= k <= N, 2N < r, satisfies L + c·D >= log2 N − O(1) for an absolute constant c; obstacle: leaves partition the nodes arbitrarily, and partial-agreement bounds need additive structure (progressions) in each leaf set (Behrend-type sets may avoid it).

DEC allocation: strongest open math; plus mandatory review of PRF-58cf340e and the division-SLP PRF.

Assumptions:
- none

References:
- HYP-0c93c4e2-19f2-4fd9-aedd-7dd2b45a163f
- HYP-6aef8c30-2942-4079-8d0a-fc2ae8b6c200
- HYP-92a9b4d9-827b-45fc-b881-1e7cf3b3443b
- HYP-2de84d42-f26b-45c1-ae82-7ffb4a404b61

Sources:
- none

## Claims and verification
- none

Evidence:
- research/ecdlp/events/EVT-179ff07a-7d03-4d31-b49b-1d413f1f44a8.evidence
- research/ecdlp/events/EVT-f0e4be6b-08bb-40cb-bf4e-8e72a00b6f6c.evidence

## Outcome, limitations and next action
Next action: ECDLP-40 review and formalization

Notes: Created by PI RUN-62dbda7c.

_Generated from the JSON record by `research.py render-md`; the JSON is authoritative._
