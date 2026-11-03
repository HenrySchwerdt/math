# HYP-d6cc9bce-05d5-4d2b-92f8-e4baf3b986e0 — Inventor B: representation change gives only constant factors (orbit rho, volcano ascent)

Status: completed; proof status: experimental; outcome: refuted.

## Question, selection rationale and inputs
Inventor B (ECDLP-43, representation change): no asymptotic gain over Pollard rho. B1 automorphism-orbit rho (j=0 |Aut|=6, j=1728 |Aut|=4) recovers k in 450/450 runs, r <= 2^36; fitted exponents 0.44-0.49 (CIs contain or nearly contain 0.5); pooled rho/orbit ratio 1.45 [1.14,1.88] (j=0, below pre-registered 1.15 threshold) and 2.62 [2.15,3.17] (j=1728, inflated by heavy-tailed rho baseline 2-3x above textbook). Known technique (constant sqrt|Aut|). B2 2-isogeny volcano ascent to j=0 then B1: 150/150, isogeny evaluations ~ a^1.86 (polylog); pre-registered rule printed "asymptotic improvement" but this is a false positive from additive overhead shrinking 60%->3%; medians indicate exponent 1/2, constant ~2-2.5; applies only to curves isogenous to j=0 (fraction ~ p^-0.47 [-0.58,-0.38]); equivalent in kind to Jao-Miller-Venkatesan / Galbraith volcano climbing. Isogeny-pooled, twist-pooled and other curve models rejected on paper (preserve r and group structure).

Strategic correction: constructive algorithm candidates benchmarked vs rho.

Assumptions:
- none

References:
- RUN-58dee679-198d-45aa-8a53-36bba92d67f9

Sources:
- none

## Claims and verification
- Inventor B (ECDLP-43, representation change): no asymptotic gain over Pollard rho. B1 automorphism-orbit rho (j=0 |Aut|=6, j=1728 |Aut|=4) recovers k in 450/450 runs, r <= 2^36; fitted exponents 0.44-0.49 (CIs contain or nearly contain 0.5); pooled rho/orbit ratio 1.45 [1.14,1.88] (j=0, below pre-registered 1.15 threshold) and 2.62 [2.15,3.17] (j=1728, inflated by heavy-tailed rho baseline 2-3x above textbook). Known technique (constant sqrt|Aut|). B2 2-isogeny volcano ascent to j=0 then B1: 150/150, isogeny evaluations ~ a^1.86 (polylog); pre-registered rule printed "asymptotic improvement" but this is a false positive from additive overhead shrinking 60%->3%; medians indicate exponent 1/2, constant ~2-2.5; applies only to curves isogenous to j=0 (fraction ~ p^-0.47 [-0.58,-0.38]); equivalent in kind to Jao-Miller-Venkatesan / Galbraith volcano climbing. Isogeny-pooled, twist-pooled and other curve models rejected on paper (preserve r and group structure).

Evidence:
- research/ecdlp/experiments/round12-inventor-b/analysis.txt
- research/ecdlp/experiments/round12-inventor-b/PROTOCOL.md

## Outcome, limitations and next action
Next action: Closed. Only open thread: measure isogeny distance from generic curve to structured curve (expected ~sqrt(p) steps, i.e. no gain). Low priority.

Notes: PI re-ran analyze.py via exec: identical after normalising numpy float repr (numpy version difference). Toy Python sizes; one prime per size in B1; rho baseline 2-3x above textbook; no independent review. Pre-registered rule for T2 should be amended to use medians/normalised cost.

_Generated from the JSON record by `research.py render-md`; the JSON is authoritative._
