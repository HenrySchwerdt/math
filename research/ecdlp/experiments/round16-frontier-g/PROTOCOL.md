# PROTOCOL — Round 16 / frontier G: automated discovery of DLP procedures (RUN-ede8fc59-b94d-4073-8b8c-a58aa6368779)

Pre-registered before any evolutionary search was run. Toy curves only (prime order r, 2^10 <= r <= 2^16, prime field).
Files: `dsl.py` (VM, curves, hand baselines), `evolve.py` (search), `evaluate.py` (held-out test; written after
the search but its analysis is fixed here). The sha256 of this file is recorded in `PROTOCOL.sha256` before searching.

## Question
Does an automated search over programs in a small DLP instruction set find a procedure whose measured cost
scales as r^beta with beta < 1/2 on instances (sizes and curves) never used by the search? What does it rediscover?

## Instruction set (exactly as implemented in dsl.py)
4 point registers (start at the identity O), 2 integer counters (c0 = loop iteration, c1 user), a hash table of
at most 2*ceil(sqrt r) entries (memory bound), programs = init block (<=5 instr) + loop body (<=10 instr).
Ops: SETC (c*P or c*Q for c = m*ceil(r^(e/32)), cost = double-and-add count), ADD, DBL (cost 1 each), NEG, MOV, SETO
(cost 0), SETRAND (random aP+bQ, cost 3*bitlen r), STEP (add walk-table entry indexed by low nb bits of x; table built on
first use at cost 6*bitlen r + 2^nb; entry cost 1), INS/LOOK (hash table insert/lookup keyed on (x>>s)&(2^kb-1)),
SOLVE (on x-equality of two registers), INC/ZERO, conditionals IFLT/IFGE/IFMOD (counter vs r^(e/32)-scale constants),
IFEQX, IFLTX (equality / integer comparison of x), IFDP (low bits of x zero). Programs see only x-coordinates (infinity
has x=-1); points carry hidden coefficients (a,b) with point = aP+bQ, used only by LOOK/SOLVE to derive candidate k
from a relation a1+b1 k = +-(a2+b2 k). Each candidate k is verified at charged cost ceil(1.5*bitlen r) group ops (no free
oracle); the first verified candidate halts the program. Run cap: total cost <= 12*sqrt(r) (failure => counted as cost
12*sqrt(r)); at most 10*cap VM steps. Implementation detail (not visible to programs): a point is stored with its hidden
discrete log v so that x lookup is O(1); this is exact for a cyclic group of prime order r.
Designer priors disclosed: constants are on an r^(e/32) grid (biases toward sqrt/cuberoot-scale constants, i.e. toward
the known structures); the initial population is biased to start with SETC.

## Curves and data splits (prime-order curves y^2=x^3+ax+b over F_p, p in +-6% of 2^tb, r in [2^(tb-.2), 2^(tb+.2)), r<=65536)
- TRAIN: tb in {10,11,12}, curve seeds {0,1}; instances resampled per generation.
- VALIDATION: tb in {10,11,12}, curve seeds {150,151}; only used to pick each run's champion from its hall of fame.
- BASELINE TUNING (hand DSL programs, a few parameters nb, dp bits, restart only): tb=11 seed 101 (and tb 10,12 seed 100 smoke test).
- TEST-A (held-out sizes): tb in {13,14,15,16}, curve seeds {200,201,202}, 60 random k per curve (180 instances per size).
- TEST-B (held-out curves at training sizes): tb in {10,11,12}, curve seeds {210,211,212}, 60 k per curve.
Test curves are not used by evolve.py. Same instances (k, random seed) are given to the discovered programs and baselines.

## Search
Evolutionary: population 100, tournament 3, elites 6, 30% one-point crossover, point/insert/delete/field mutations,
hall of fame = top 3 per generation. Fitness (minimised) = mean over 24 train instances of
cost/sqrt(r) for solved, and 12*(1 - 0.3*min(1, hits/5)) for unsolved (shaping: `hits` = x-collisions with distinct
coefficients; added because without shaping the fitness plateau at 12 gave no gradient in a 60-generation smoke test)
+ 0.003*(program length). Per-run champion = lowest validation score (10 instances/curve) among hall-of-fame members.
Primary: 8 runs from random initial populations (seeds 0..7), 200 generations each. Secondary (labelled, NOT used for the
success criterion): 4 runs whose initial population contains the hand BSGS/rho/brute programs and their mutants
(seeds 10..13), to see whether search improves on the human structures.

## Success criterion (primary, fixed)
A champion is a "sub-square-root discovery" iff on TEST-A: (1) success rate >= 0.90 at every size, and
(2) the 99% bootstrap-percentile upper bound of the cost exponent beta is < 0.5.
Exponent = OLS slope of ln(mean cost) on ln(mean r) over the 4 test sizes (cost of failed run = cap); bootstrap = 2000
resamples of instances within each size stratum, seed 12345. 99% (not 95%) because up to 8 champions are tested.
Calibration gate: the same estimator is applied to the hand BSGS (provably Theta(sqrt r)) and hand rho on TEST-A.
If the BSGS 99% CI lies wholly below 0.5 (estimator biased low by fixed overheads), criterion (2) is replaced by
"champion upper99 < BSGS lower99", and any "<0.5" statement is reported as non-discriminating.
No speedup is claimed unless the criterion holds on TEST-A; failures count as honest negatives. Constant-factor
comparisons (mean cost / sqrt r) are reported but are not evidence of a better exponent.

## Overfitting guards
Disjoint train/validation/test curves; test sizes 13-16 are all larger than any training size; correctness on TEST-B
(new curves, same sizes) also reported; program verification is charged so a program cannot win by unverified guessing.

## What would kill / confirm
Kill: every champion fails (1) or (2), or the calibrated gate fails. Confirm needs both and a manual reading of the
program showing no hidden oracle use (check against instruction semantics). Expectation (stated in advance, not a result):
negative; search finds BSGS-like (table + giant steps) or rho-like (STEP/DP walks with collision) structures.
