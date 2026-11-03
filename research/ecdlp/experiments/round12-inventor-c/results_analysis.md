## Single-instance: reference rho vs C1 (frozen) and C1b (post-hoc amendment)

- ref: 88 runs, incorrect outputs: 0
- C1: 76 runs, incorrect outputs: 0
- C1b: 88 runs, incorrect outputs: 0

| bits | n | trials | ref mean ops | ref/sqrt(n) | C1 mean ops | C1/sqrt(n) | ratio ref/C1 (95% CI) | capped walks/run |
|---|---|---|---|---|---|---|---|---|
| 24 | 9864721 | 16 | 5788 | 1.843 | 4816 | 1.533 | 1.202 (0.915, 1.539) | 0.06 |
| 28 | 163661777 | 16 | 20015 | 1.564 | 14969 | 1.170 | 1.337 (0.947, 1.958) | 0.25 |
| 32 | 2266878331 | 16 | 42078 | 0.884 | 88907 | 1.867 | 0.473 (0.303, 0.707) | 0.88 |
| 36 | 51831578413 | 16 | 271269 | 1.192 | 867468 | 3.810 | 0.313 (0.225, 0.439) | 4.06 |
| 40 | 701298629047 | 12 | 1010514 | 1.207 | 9876283 | 11.793 | 0.102 (0.066, 0.171) | 14.08 |
| 44 | 13787536989269 | - | 5667140 | 1.526 | not completed (censored) | | | |

| bits | n | trials | ref mean ops | ref/sqrt(n) | C1b mean ops | C1b/sqrt(n) | ratio ref/C1b (95% CI) | capped walks/run |
|---|---|---|---|---|---|---|---|---|
| 24 | 9864721 | 16 | 5788 | 1.843 | 4816 | 1.533 | 1.202 (0.915, 1.539) | 0.06 |
| 28 | 163661777 | 16 | 20015 | 1.564 | 13824 | 1.081 | 1.448 (1.060, 2.033) | 0.12 |
| 32 | 2266878331 | 16 | 42078 | 0.884 | 60774 | 1.276 | 0.692 (0.470, 0.978) | 0.12 |
| 36 | 51831578413 | 16 | 271269 | 1.192 | 240776 | 1.058 | 1.127 (0.883, 1.436) | 0.00 |
| 40 | 701298629047 | 12 | 1010514 | 1.207 | 882508 | 1.054 | 1.145 (0.759, 1.732) | 0.00 |
| 44 | 13787536989269 | 12 | 5667140 | 1.526 | 4229535 | 1.139 | 1.340 (0.847, 2.181) | 0.17 |

Fitted exponent ref (sizes [24, 28, 32, 36, 40]): ops ~ n^e, e = 0.461  95% CI (0.435, 0.487)
Fitted exponent C1 (sizes [24, 28, 32, 36, 40]): ops ~ n^e, e = 0.687  95% CI (0.652, 0.719)
Fitted exponent ref (sizes [24, 28, 32, 36, 40, 44]): ops ~ n^e, e = 0.486  95% CI (0.467, 0.506)
Fitted exponent C1b (sizes [24, 28, 32, 36, 40, 44]): ops ~ n^e, e = 0.482  95% CI (0.458, 0.504)
C1 cycle statistics (sums over runs): repeats@2 250223, repeats@other 3874, capped-walks 253
C1b cycle statistics (sums over runs): repeats@2 1031676, repeats@other 16799, capped-walks 7

## C2: preprocessed fixed-walk table

- 160 queries, incorrect: 0

| bits | n | pre ops | pre/n^(2/3) | S (DPs) | S/n^(1/3) | online mean | online/n^(1/3) | online/sqrt(n) | ref mean | S*T^2/n | break-even #queries |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 688777 | 16976 | 2.177 | 129 | 1.46 | 119.4 | 1.35 | 0.1438 | nan | 2.67 | nan |
| 24 | 9864721 | 79782 | 1.735 | 330 | 1.54 | 363.7 | 1.70 | 0.1158 | 5788 | 4.42 | 15 |
| 28 | 163661777 | 662363 | 2.214 | 679 | 1.24 | 1100.6 | 2.01 | 0.0860 | 20015 | 5.03 | 35 |
| 32 | 2266878331 | 2833031 | 1.642 | 1895 | 1.44 | 2206.8 | 1.68 | 0.0464 | 42078 | 4.07 | 71 |
| 36 | 51831578413 | 16193267 | 1.165 | 5947 | 1.60 | 5921.8 | 1.59 | 0.0260 | 271269 | 4.02 | 61 |

Online exponent e_on = 0.344  95% CI (0.317, 0.371)
Single-query total (pre+online) exponent e_tot = 0.619  95% CI (0.619, 0.619)
Slope of log2(S*T^2/n) vs bits (0 = sits on ST^2 ~ N): 0.027
Preprocessing exponent: 0.619  Memory(S) exponent: 0.338

## C3: batch (M = 16 instances, shared DP set) vs reference per instance

- 54 batches, incorrect: 0

| bits | n | trials | batch total ops | per-instance | per-inst/sqrt(n) | ref mean ops | ref/per-instance (95% CI) | DPs stored |
|---|---|---|---|---|---|---|---|---|
| 24 | 9864721 | 12 | 34952 | 2184 | 0.696 | 5788 | 2.65 (2.04, 3.30) | 338 |
| 28 | 163661777 | 12 | 102596 | 6412 | 0.501 | 20015 | 3.12 (2.39, 3.93) | 318 |
| 32 | 2266878331 | 12 | 388897 | 24306 | 0.511 | 42078 | 1.73 (1.24, 2.29) | 332 |
| 36 | 51831578413 | 12 | 1596474 | 99780 | 0.438 | 271269 | 2.72 (2.15, 3.31) | 371 |
| 40 | 701298629047 | 6 | 6141208 | 383826 | 0.458 | 1010514 | 2.63 (2.00, 3.35) | 336 |

Per-instance cost exponent in n (M=16): e = 0.465  95% CI (0.455, 0.477)

## C3: M-sweep at 32 bits

- 84 batches, incorrect: 0

| M | per-instance ops | total/sqrt(M n) | ref/per-instance |
|---|---|---|---|
| 1 | 170487 | 3.58 | 0.25 |
| 2 | 85626 | 2.54 | 0.49 |
| 4 | 45657 | 1.92 | 0.92 |
| 8 | 32244 | 1.92 | 1.30 |
| 16 | 24306 | 2.04 | 1.73 |
| 32 | 15465 | 1.84 | 2.72 |
| 64 | 10893 | 1.83 | 3.86 |

Per-instance cost vs M exponent (all M): -0.634  95% CI (-0.682, -0.583)
Per-instance cost vs M exponent (M >= 2): -0.570  95% CI (-0.632, -0.502)
