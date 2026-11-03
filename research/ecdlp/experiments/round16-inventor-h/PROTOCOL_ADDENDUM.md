# PROTOCOL_ADDENDUM (written after protocol freeze, before any registered benchmark run)
Debug pilots only (16-bit E2/E3, one 32-bit E3 timing run with 4 candidates; outputs discarded or not analysed). Implementation details
not fixed in PROTOCOL.md, set before the registered runs:
1. E1 T convention: T = giant-step ops + 1 (initial lookup counts one op, so the full table has T=1, rho=1/2 and rho is defined). Sensitivity T = ops + interpolation probes.
2. E2 train/test split by index halves of the affine stride (a first parity split was found in debugging to leak the label k' mod 2 into the split; fixed).
3. E3 training evaluation aborts a candidate after 4 failed queries (success rate then < 0.98 anyway); eval runs never abort.
   Step-point setup (<=256 scalar multiplications) is not charged to prep or T. Query generation kP is not charged. 
4. E3 candidate table seed ts in {0,1,2} for H; EVAL-B rebuilds with ts=100,101,102. B0 candidates are the 12 grid points with F0, ss=0, ts=0.
5. Bootstrap for slope: 2000 resamples; per size mean rho over 3 curves, then OLS on bits.
