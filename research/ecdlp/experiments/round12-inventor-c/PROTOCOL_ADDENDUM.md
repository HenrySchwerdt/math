# Addendum A1 to PROTOCOL.md (registered AFTER observing the frozen C1 result; post-hoc, labelled as such)

Date (UTC) of registration: see PROTOCOL_ADDENDUM.registered_at. PROTOCOL.md sha256 d6daf4f17f8df9521577f808a6a95dd075d47dbd18af4337e0cccc1f57109129.

## What happened (facts that triggered the addendum)
Frozen C1 (cycle detection for periods 2 and 4 only) ran correctly but its cost per instance blew up with size:
ops/sqrt(n) = 1.2-8 at 36 bits, 1.9-23.5 at 40 bits, and 44-bit runs did not finish in >10 minutes of CPU each
(killed; censored, no 44-bit C1 data). The count of walks that hit the 20(mask+1) step cap (fruitless cycles of
period >= 6 that the frozen detector does not recognise) grows with the walk length L ~ sqrt(n)/16.
Also: the 295 s per-mode timeout truncated the ref (1 trial) and neg (3 trials at 40 bits, all of 44) runs; the
missing 40/44-bit ref and 40-bit C1 trials were completed with resume.py (same code, same seeds, appended).
Frozen-C1 decision (rule in PROTOCOL.md) is evaluated on the sizes it completed: 24,28,32,36,40.

## Amendment C1b (new candidate variant, code algos2.py, runner bench2.py)
Same as C1 except: cycle detection compares the new class with ALL of the last W=16 classes (any repeat
distance d in 2..16 is treated as a cycle: the smallest-x member of the repeated segment is doubled and the
history cleared). cap = 20(mask+1) unchanged. Sizes {24,28,32,36,40,44}, trials 16/12, same curves, same
k_t and walk seeds as ref. Pilot (seed namespace 'pilot', 34 bits, 16 trials): frozen C1 1.75 sqrt n with
1.7 capped walks/run; C1b W=16 0.81 sqrt n with 0 capped; ref 1.45 sqrt n (pilot only, not evidence).
Decision rules: identical to C1 (constant-factor rule; exponent unchanged). C1b results are labelled
POST-HOC AMENDMENT; the frozen C1 failure is retained as a result.
