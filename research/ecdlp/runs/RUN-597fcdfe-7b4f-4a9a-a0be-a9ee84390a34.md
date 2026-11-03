# RUN-597fcdfe-7b4f-4a9a-a0be-a9ee84390a34: prime-field small-x factor bases at toy sizes (ECDLP-12)

Role: experimenter (Claude Sonnet 5.5, model id claude-sonnet-5-5 as stated by the runtime prompt). Toy synthetic curves only. Proof status: not-applicable (finite experiment).

## Inputs
- Task TSK-db0e4159-ba4a-4577-821b-b29f8e46ed2c (ECDLP-12); hypothesis HYP-db508348-69da-451b-ba37-d4d4f472c121 (quoted in the question: "no (m,B) yields a relation-collection cost below sqrt(p) group operations on prime fields at toy sizes").
- Library: research/ecdlp/experiments/lib/toyec.py (Curve, is_prime, dlog_bsgs oracle). Master seed 20261107. No other run reports were read. No web lookups used; no recursive agents; no commits.
- Files (owned dir research/ecdlp/experiments/round4/): PROTOCOL.md, PROTOCOL.sha256, round4.py, results_20261107.json, output_20261107.txt, SHA256SUMS.

## Protocol and hash
Pre-registered in research/ecdlp/experiments/round4/PROTOCOL.md before the script was written or run. sha256(PROTOCOL.md) = 9564f318926d7d7e283c9c4e37e7b37d29b1641dc5c9f41a20d04a8f1771b334 (PROTOCOL.sha256). Summary: buckets p near 2^12/2^14/2^16/2^18 (random prime in [0.9, 1.1]*2^k), 3 prime-order curves per bucket (12 curves), m in {2,3}, B = floor(beta p^(1/m)), beta in {0.5,1,2}; exact enumeration of all m-sums; unit-cost model; decision rule fixed in advance (FALSIFIED iff some config has mean model cost < 0.5 sqrt(p) at 2^18 AND log-log exponent < 0.5).

Deviations/notes (honest accounting):
- The script was executed twice: a development run, then the final run (output_20261107.txt, results_20261107.json) after splitting rho setup cost from steps in the baseline reporting. Cost model, parameters, seeds and the decision rule did not change between the runs; the model rows were identical.
- No subsampling was needed: m=3 was enumerated exhaustively (all n^3 triples via pair-sum set + V_B; max n = 128 at 2^18, beta=2).
- S_3 oracle test design: P1,P2 random points, x3 = x(P1+P2) and x(P1-P2) (positive checks), plus random x3 from a random point R (S_3==0 must hold iff x3 is one of those two); slight reading of the protocol sentence "triples incl. sign choices".
- The commands were run directly (not via scripts/research.py exec) because this task restricts edits of the RUN JSON to claims/notes/next_action/run.benchmark; exec would append to run.commands. Hence output capture is the tee'd file output_20261107.txt, not an exec record.
- NAIVE-A attempt cost uses the registered 2*nx (sign symmetry exploited); an honest implementation tests all n = 2 nx values V, so this is a lower bound (favourable to the candidate by factor ~2 in the attempt term). The same favour is applied to the Semaev route (one root solve = 1 unit, only the nx x-values with points).

## Environment
Linux 6.18.44 (Claude Code remote container, 4 vCPU Intel Xeon 2.30 GHz, 15 GiB), Python 3.13.18, numpy 2.5.3, single process. Branch claude/exciting-mccarthy-yljzor, starting commit d860d3fb0961237c7d9be2735484049a8da7ed39. Command: `cd research/ecdlp/experiments/round4 && python3 round4.py > output_20261107.txt` (exit 0, 4.1 s wall; budget 5 min not an issue, no size reduction). Costs below are counted operations, not wall time.

## S_3 correctness check (done first, as oracle)
S_3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2+a)+2b) x3 + (x1 x2-a)^2 - 4b(x1+x2), checked on curves over F_1009 and F_4093 (random a,b):
- positive checks (x3 = x(P1+P2) or x(P1-P2) from the group law): 3983, failures 0 (including 3 cases with x1=x2);
- random-x3 iff checks (S_3==0 exactly when x3 is x(P1+-P2)): 2000, failures 0;
- quadratic-in-x2 expansion (A2=(x3-x1)^2, A1, A0 as coded in round4.py) vs direct S_3: 2000 checks, failures 0.
Semaev route consistency (m=2, beta=1, 300 random R each): p=4001: agreement 300/300 with brute-force pair table (decomposable R: 126); p=15791: 300/300 (decomposable 128). Per-attempt loop cost = nx root solves (32 and 69).

## Decomposition probabilities (exact, mean over 3 curves per bucket)
n = |V_B| counts both signs of each point (V_B is symmetric, nx = n/2 x-values). With V_B already containing +-V, the number of unordered m-sums is about n^m/m!, so H1 = n^m/(m! r) is the sign-consistent heuristic; the task's H2 = (2n)^m/(m! r) double counts signs when n = |V_B| (it is correct only if n denotes the number of x-values), shown for comparison.
| bucket | m | beta | mean p | mean n=|V_B| | pi measured | H1 n^m/(m! r) | H2 (2n)^m/(m! r) cap 1 |
|---|---|---|---|---|---|---|---|
| 2^12 | 2 | 0.5 | 4003 | 32.7 | 0.1264 | 0.1339 | 0.5354 |
| 2^12 | 2 | 1 | 4003 | 67.3 | 0.4421 | 0.5668 | 1.0000 |
| 2^12 | 2 | 2 | 4003 | 130.7 | 0.8945 | 1.0000 | 1.0000 |
| 2^12 | 3 | 0.5 | 4003 | 6.0 | 0.0110 | 0.0090 | 0.0719 |
| 2^12 | 3 | 1 | 4003 | 14.0 | 0.1122 | 0.1171 | 0.8384 |
| 2^12 | 3 | 2 | 4003 | 33.3 | 0.8010 | 1.0000 | 1.0000 |
| 2^14 | 2 | 0.5 | 15880 | 60.0 | 0.1070 | 0.1138 | 0.4553 |
| 2^14 | 2 | 1 | 15880 | 126.7 | 0.3979 | 0.5069 | 1.0000 |
| 2^14 | 2 | 2 | 15880 | 245.3 | 0.8447 | 1.0000 | 1.0000 |
| 2^14 | 3 | 0.5 | 15880 | 9.3 | 0.0131 | 0.0123 | 0.0987 |
| 2^14 | 3 | 1 | 15880 | 22.7 | 0.1273 | 0.1344 | 0.7954 |
| 2^14 | 3 | 2 | 15880 | 47.3 | 0.6682 | 0.9238 | 1.0000 |
| 2^16 | 2 | 0.5 | 67446 | 131.3 | 0.1200 | 0.1280 | 0.5122 |
| 2^16 | 2 | 1 | 67446 | 262.7 | 0.4001 | 0.5121 | 1.0000 |
| 2^16 | 2 | 2 | 67446 | 544.7 | 0.8911 | 1.0000 | 1.0000 |
| 2^16 | 3 | 0.5 | 67446 | 16.7 | 0.0127 | 0.0125 | 0.0998 |
| 2^16 | 3 | 1 | 67446 | 39.3 | 0.1431 | 0.1527 | 0.9497 |
| 2^16 | 3 | 2 | 67446 | 83.3 | 0.7596 | 1.0000 | 1.0000 |
| 2^18 | 2 | 0.5 | 253128 | 242.7 | 0.1101 | 0.1167 | 0.4667 |
| 2^18 | 2 | 1 | 253128 | 484.7 | 0.3735 | 0.4653 | 1.0000 |
| 2^18 | 2 | 2 | 253128 | 990.7 | 0.8574 | 1.0000 | 1.0000 |
| 2^18 | 3 | 0.5 | 253128 | 28.7 | 0.0158 | 0.0157 | 0.1255 |
| 2^18 | 3 | 1 | 253128 | 54.0 | 0.0983 | 0.1045 | 0.8356 |
| 2^18 | 3 | 2 | 253128 | 118.7 | 0.6652 | 0.9563 | 1.0000 |

Reading: measured pi tracks H1 within 0-30% (below H1 as pi saturates, from collisions among sums); H2 overestimates by about 2^m at small pi. Heuristic pi ~ n^m/(m! r) is supported at these sizes; at beta=2 pi is 0.67-0.89, not 1.

## Cost model and results
Unit = one group operation or one hash lookup; N = nx+11 relations; attempts = N/pi; linear algebra m*nx^2 added. Decomposers: NAIVE-A ((m-1)-sum table, attempt scans nx candidates, 2 units each), NAIVE-B (full m-sum table: build n^m/m!, O(1) attempt), SEMAEV (m=2 only, nx root solves per attempt). Per-curve minimum taken, then averaged over curves (cost = best decomposer's total).
| bucket | m | beta | best decomposer (per curve) | mean total cost (units) | cost / sqrt(p) | cost / sqrt(pi r/2) |
|---|---|---|---|---|---|---|
| 2^12 | 2 | 0.5 | naiveB | 1477 | 23.4 | 18.6 |
| 2^12 | 2 | 1 | naiveB | 4245 | 67.1 | 53.5 |
| 2^12 | 2 | 2 | naiveB | 12300 | 194.4 | 154.9 |
| 2^12 | 3 | 0.5 | naiveB | 2624 | 41.5 | 33.0 |
| 2^12 | 3 | 1 | naiveB | 939 | 14.8 | 11.8 |
| 2^12 | 3 | 2 | naiveA | 2555 | 40.4 | 32.2 |
| 2^14 | 2 | 0.5 | naiveB | 4287 | 34.0 | 27.1 |
| 2^14 | 2 | 1 | naiveB | 14766 | 117.2 | 93.4 |
| 2^14 | 2 | 2 | naiveB | 44015 | 349.3 | 278.5 |
| 2^14 | 3 | 0.5 | naiveB | 10136 | 80.3 | 64.0 |
| 2^14 | 3 | 1 | naiveB | 2850 | 22.6 | 18.0 |
| 2^14 | 3 | 2 | naiveA | 5315 | 42.2 | 33.6 |
| 2^16 | 2 | 0.5 | naiveB | 18060 | 69.4 | 55.4 |
| 2^16 | 2 | 1 | naiveB | 62325 | 239.6 | 191.3 |
| 2^16 | 2 | 2 | naiveB | 209684 | 805.9 | 643.4 |
| 2^16 | 3 | 0.5 | naiveB | 5067 | 19.7 | 15.7 |
| 2^16 | 3 | 1 | naiveA,naiveB | 9662 | 37.1 | 29.6 |
| 2^16 | 3 | 2 | naiveA | 14469 | 55.6 | 44.4 |
| 2^18 | 2 | 0.5 | naiveB | 59855 | 118.8 | 94.8 |
| 2^18 | 2 | 1 | naiveB | 213404 | 424.1 | 338.5 |
| 2^18 | 2 | 2 | naiveB | 709284 | 1409.5 | 1124.9 |
| 2^18 | 3 | 0.5 | naiveB | 7910 | 15.7 | 12.6 |
| 2^18 | 3 | 1 | naiveA | 25026 | 49.7 | 39.7 |
| 2^18 | 3 | 2 | naiveA | 30260 | 60.2 | 48.0 |

At 2^18, m=2: NAIVE-B costs 61.8k / 218k / 706k (beta 0.5/1/2), Semaev route 172k / 281k / 784k, NAIVE-A 313k / 441k / 1.07M, versus sqrt(p) ~ 503 and sqrt(pi r/2) ~ 617. The Semaev route beats NAIVE-A by ~2-2.7x (attempt cost nx+1 vs 2nx+1) but never the full-table method, whose build cost n^2/2 is itself of order pi*r (it is a BSGS in disguise).

Measured baselines (one curve per bucket; counted units; rho = Brent cycle finding, 32-way additive walk, mean of 20 runs; setup = 33 scalar multiplications for the walk, estimated 3 log2 r units each; BSGS mean of 10):

| bucket | r | BSGS units | rho steps | sqrt(pi r/2) | sqrt(p) |
|---|---|---|---|---|---|
| 2^12 | 4049 | 210 (111 adds + 98 lookups) | 124 (+1188 setup) | 80 | 63 |
| 2^14 | 15919 | 407 (210 adds + 197 lookups) | 290 (+1386 setup) | 158 | 126 |
| 2^16 | 69031 | 835 (426 adds + 409 lookups) | 490 (+1617 setup) | 329 | 263 |
| 2^18 | 241321 | 1493 (755 adds + 738 lookups) | 829 (+1782 setup) | 616 | 491 |

At 2^18 every configuration is 15.7-1409x above sqrt(p) and 5-475x above measured BSGS (1493 units vs best config 7.9k).

Log-log scaling exponent of mean best-decomposer cost vs mean p (OLS over the 4 buckets; +- is OLS s.e., 2 d.o.f., indicative only):

| m | beta | exponent |
|---|---|---|
| 2 | 0.5 | 0.903 +- 0.031 |
| 2 | 1 | 0.950 +- 0.012 |
| 2 | 2 | 0.989 +- 0.022 |
| 3 | 0.5 | 0.187 +- 0.193 |
| 3 | 1 | 0.798 +- 0.017 |
| 3 | 2 | 0.606 +- 0.022 |

sqrt(p) itself gives 0.500 (pipeline check). Best (m,beta) per bucket:

| bucket | best config key (bucket|m|beta) | mean cost | cost / sqrt(p) |
|---|---|---|---|
| 2^12 | 12|3|1 | 939 | 14.8 |
| 2^14 | 14|3|1 | 2850 | 22.6 |
| 2^16 | 16|3|0.5 | 5067 | 19.5 |
| 2^18 | 18|3|0.5 | 7910 | 15.7 |

The sequence of best costs has exponent 0.50 +- 0.08, but this mixes configurations and is a small-n artifact: for (m=3, beta=0.5) the factor base has only n = 6..29 points, so the fixed epsilon=10 extra relations and the nx^2 linear algebra dominate at small p and the cost is only in the process of crossing over to the table-build term; its fitted exponent 0.19 (local slopes 0.98, -0.48, 0.34, noisy because the number of points per curve varies) is not a meaningful asymptotic exponent. Within the cost model the dominant terms are explicit: NAIVE-B costs about n^m/m! (= pi r) for the table plus about 2 nx/pi for attempts; balancing them gives pi ~ r^(-(m-1)/(2m-1)) and total ~ r^(m/(2m-1)) (2/3 for m=2, 3/5 for m=3, tending to 1/2 from above as m grows). This is a derivation inside my cost model (table-based decomposition, my unit costs) and not a statement about all algorithms; it only explains why the toy measurements stay above sqrt(p).

## Decision rule evaluation
Pre-registered: FALSIFIED iff some config has cost < 0.5 sqrt(p) at 2^18 and exponent < 0.5. Minimum cost ratio at 2^18 is 15.7 x sqrt(p) (m=3, beta=0.5), nowhere near 0.5; the only configuration with a fitted exponent < 0.5 (3|0.5) fails the first condition by a factor ~31. No configuration satisfies either condition at the required level together.

## End-to-end toy index calculus
Best parameters by model per bucket (3|1 at 2^12 and 2^14), first curve of the bucket, NAIVE-A-style relation collection by actual group operations (random-walk R = aP+bQ, 1 add per R; (m-1)-sum dict; test R-V for every V in V_B; linear system for unknowns log of the nx sign-normalised x-class representatives and k; incremental sparse-ish Gaussian elimination mod r; stop when the pivot for k appears; relations checked as group identities for the first 100):

| bucket | curve | config | collection | recovered vs oracle | measured units | sqrt(p) / sqrt(pi r/2) |
|---|---|---|---|---|---|---|
| 2^12 | p=4001, r=4049 | m=3, B=15 (n=14, nx=7) | 70 attempts, 7 relations | k_true=1924, recovered=1924, dlog_bsgs=1924 | 3272 (build 105, walk 1258, subtract 908, lookup 908, LA mults 93) | 63 / 80 |
| 2^14 | p=15791, r=15919 | m=3, B=25 (n=28, nx=14) | 58 attempts, 13 relations | k_true=7232, recovered=7232, dlog_bsgs=7232 | 5036 (build 406, walk 1444, subtract 1361, lookup 1361, LA mults 464) | 126 / 158 |

Both runs succeeded: k verified by k*P==Q and equal to the independent dlog_bsgs oracle. Measured totals (3272, 5036) are 52x and 40x sqrt(p) respectively. Note the "walk" term is dominated by the one-time 33 scalar multiplications for walk generators (my estimate 3 log2 r units each); the scan of V_B per attempt (all n values, no sign-symmetry shortcut) is the bulk of the rest. Caveat: the relation matrix became solvable for k with only 7/13 relations (nx = 7/14) because the pivot for k forms as soon as the span contains a vector supported on k; this is a verified mod-r consequence, not an assumption.

## Verdict
Hypothesis H (no (m,B) beats sqrt(p) at toy sizes) SURVIVES on the tested domain only: 12 curves with p in ~[3.8e3, 2.8e5], m in {2,3}, beta in {0.5,1,2}, one master seed, unit-cost model. Decomposition probability follows n^m/(m! r) (sign-consistent) rather than the sign-doubled formula. Index calculus works end to end at toy sizes but costs 15-1400x sqrt(p) in the model here. This is not evidence about asymptotic behaviour.

## Limitations
- Toy sizes, 4 bucket points, 3 curves each; exponents from 4 points with 2 d.o.f. are indicative only; no confidence claim.
- Cost model: unit weights (group op = lookup = root solve = 1), unweighted field ops; epsilon fixed at 10; sparse linear algebra counted as m*nx^2 without implementing it; NAIVE-A/Semaev use sign symmetry (nx not n) which is favourable to the candidate.
- Only m in {2,3}, beta <= 2, x-coordinate-bounded factor base only; larger beta (pi -> 1) and m >= 4 were not explored; other decomposition methods (Semaev for m=3 via S_4, Grobner/sieving, lattice) not tested.
- Rho baseline cost estimate for setup is approximate (3 log2 r per scalar mult); Brent walk steps not DP-optimised. Baselines use 1 curve per bucket.
- Primes p only; r prime assumed; anomalous curves excluded.
- Development run precedes the recorded final run (see deviations).
