# PROTOCOL ADDENDUM (RUN-809bfa01) — deviations, written after the first data (honest, post-run where noted)
1. (before main learn runs finished) First launch of `learn.py` with default multithreaded HistGradientBoosting overloaded the 4-core machine (load ~15) and several jobs hit the 270 s timeout,
   leaving empty output files. Killed and re-ran only the missing jobs with OMP_NUM_THREADS=1; results of completed jobs are unchanged. `learn.py` regress branch was changed afterwards so
   control=0 runs real-only and control=1 runs planted-only (max_iter 200 -> 150); regress data come only from the re-run. Code hashes refreshed in SHA256_code_frozen.txt BEFORE the rerun.
2. (post-hoc, before reading P4 results at stop=300) P4 closeness scan: initial stop=3 collapsed T shifts onto duplicate points when the test window wc < T (noisy detector cannot be amplified by
   repeating the same point; hash noise is deterministic per point), giving 6/12 success independent of nu. Changed default stop to 300 (finish by enumerating <= 601 candidates, counted). Both
   result sets kept (out/p4.json, out/p4b.json = stop 3; out/p4c.json = stop 300). nu_d=1 is calibrated from p4c (47/48 success for delta >= 0.1, 12 sizes x cells).
3. P3 was run first with z=2 per-round (coverage 95% per round, overall success 47-83%), then z=4 (p3b): both reported.
4. P1 eps=0.05: n=8 instances per size (cost of the ML grid), runs per size in separate commands; P1 calibration: nu in {0.5,1,1.5,2,3,4} (1.5 was added to the registered {0.5,1,2,4,8}); the registered rule picks nu=2 (30/30);
   nu=1.5 gave 29/30. Calibration was at eps=0.1, 20 bits, 30 instances, kappa 2 and 3 (kappa=2 chosen).
5. Closeness control with w=256 (<= ~2000 train samples, 8 curves x distinct |d|) is underpowered: planted delta=0.05 was not flagged there, so the w=256 (and w=16, 128 test points) nulls are inconclusive; only w=4096 at 20..28 bits has a working control.
6. The 12-bit MSB control: M1 flagged (lo>0) but M2/M3 not: test power at 12 bits (6.8k test points) is ~+-0.016. The 2^12 row is low-power, not evidence.
7. Pipelines use curves seeded 500+ (not the learner curves); planted-oracle simulators know the scalar of each queried point by construction (the planted family is defined by its dlog table).
8. (post-hoc, motivated by the cost model, written before the runs) Extra closeness windows at w ~ r/32 (16 bits: 2^11, 20: 2^15, 24: 2^19, 28: 2^23), because the cost model shows scan detectors only help
   at test windows w >= ~r^(1/2+): w <= 2^12 (the registered values) is far below that at 24 and 28 bits. Same pipeline/models/splits; reported separately as "w=r/32" (out/*_close{2048,32768,524288,8388608}_*.json).
