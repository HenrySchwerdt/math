# PROTOCOL ADDENDUM 1 (written after the first E4 run at 16 bits, before any corrected E4 run)

Defect found in PROTOCOL.md section E4 (a pre-registration error, not a code bug): "full enumeration of k = 1..r-1, so no sampling error" and the chi-square
independence test are invalid, because the points kP and (r-k)P share the same x and (for odd q, and for q=2 when r = 1 mod 4) the same class c_q.
Every x-only feature therefore sees each x twice with the identical class, a design effect of 2 on chi-square. The first run (16 bits, two curves; 32 and 20
"significant" tests, all on x-based features, identical p-values for x, x[2]Q, x[3]Q, x[5]Q because c_q(mk) = c_q(m)+c_q(k) only relabels the table) is an artifact of this defect;
it is kept unmodified in aborted/ and not used. The planted control was flagged there too, so it could not have distinguished the artifact.

Correction (applies to every E4 size): units are k = 1..(r-1)/2 only (one representative per +-pair, so every x value occurs once). Same feature set, same classes.
(1) chi-square p-values on units, Bonferroni 0.01 over all (feature, q) tests, plus a label-permutation max-T check (30 permutations of the class labels over units; T=(chi2-dof)/sqrt(2 dof)).
(2) Advantage is measured out of sample: cross-fit by index parity (fit the per-feature-value majority class on units with even index, score on odd, and conversely); accuracy gain over 1/q with a
normal-approximation 99% interval. A feature "leaks" iff Bonferroni-significant AND the 99% lower bound of the held-out gain is > 0. Positive control (planted c_2 flipped w.p. 0.45) must be flagged.
(3) Sizes unchanged (16, 18, 20; two curves each with r = 1 mod 30). Verdict rule of PROTOCOL.md otherwise unchanged. run_c.py is edited (function e4 replaced by the corrected analysis); its new hash is in SHA256_code_frozen.txt.
