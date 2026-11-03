# REV-6c73a098-6bec-4241-9b91-b7ee5bfa4fcf — Complexity review: Frontier E remarks E0 (generic model) and E3 (decision-tree size)

Status: completed; proof status: reviewed; outcome: verified.

## Question, selection rationale and inputs
Are remarks E0 and E3 of RUN-7112aed9 (recorded in HYP-6da71353) correct, and what do they imply for HYP-dbe79a50?

Unreviewed derivations bearing on the barrier map interpretation.

Assumptions:
- none

References:
- HYP-6da71353-1963-4cfd-824e-0ae14e063417
- HYP-dbe79a50-030e-41b9-944b-271f2bd37042
- RUN-98e2c896-a011-4429-af16-57d090ea908b

Sources:
- none

## Claims and verification
- E0 accept with corrections: in Shoup's model (not Maurer's) bit/order access on labels is free and useless; the Omega(sqrt r) bound is a family/random-encoding average, excludes field-structure algorithms, sigma-dependent advice and quantum; x-only encoding needs the Z_r/+-1 variant. The "distinguisher" corollary is a theorem only in tautological form (A plus a verifier); a Legendre test distinguishes x(kP) from a random injection into F_p (1.000 vs 0.463, p=10007) without k-information, so the injection must be into X={x(kP)} and "informative" formalised. As a mechanism characterisation it is a heuristic.
- E3 accept with corrections: DecisionTree.lean uses equality branching only, constants are charged arithmetic nodes (Op.const), so E3 does not attack Theorem DT. With order comparisons a binary-search tree has 0 arithmetic nodes (toy N=300: depth 9, 300 leaves), so in that model only size/depth matter; no size-depth lower bound is proved; S T^2 ~ r is an analogy only.

Evidence:
- research/ecdlp/runs/RUN-98e2c896-a011-4429-af16-57d090ea908b.md
- research/ecdlp/experiments/round13-review-e0e3/e3_e0_toy.py

## Review
Decision: revise; run RUN-98e2c896-a011-4429-af16-57d090ea908b; target commit 5c97df0.

Both remarks correct in a narrower form; E0 corollary tautological as stated; E3 does not apply to the formal (equality-only, charged constants) model.

Counterexamples:
- Legendre symbol of x^3+ax+b separates curve x-coordinates from a random injection into F_p with no information about k (toy p=10007: 1.000 vs 0.463).

Complexity: Model-level analysis; no algorithmic claim.

Limitations: Literature from memory; toy illustration on one curve; DT with free constants not checked.

## Outcome, limitations and next action
Next action: Barrier map: state Theorem DT as a barrier for equality-branching trees with charged constants; order comparisons make arithmetic length vacuous (size/depth only); Shoup bound is family-level and E0 corollary is a restatement of non-genericity.

Notes: Reviewer model self-reported Claude Sonnet 5.5 (configured), not runtime-verified. All literature (Shoup 1997, Maurer 2005, Corrigan-Gibbs-Kogan 2018, Coretti-Dodis-Guo 2018, Dent 2002, Fischlin 2000, Koblitz-Menezes 2007, Jager-Schwenk) cited from memory, not retrieved. PI reproduced e3_e0_toy.py bit-identically via exec.

_Generated from the JSON record by `research.py render-md`; the JSON is authoritative._
