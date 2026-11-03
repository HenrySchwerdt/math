# HYP-adb581ff-5c5a-43f1-bc18-e5fa83ddeadd — Corrected Theorem A / A'

## Exact statement
Theorem A (corrected, generalized): Let E/F_p be short Weierstrass and P in E(F_p) of order r >= 3 (no condition r != p). If a rational function f on E is defined at kP and satisfies f(kP) = k mod p for 1 <= k <= N <= r-1, then deg(f) (pole divisor degree) >= (N-1)/2, and a polynomial f in X, Y has total degree >= (N-1)/6. Proof: h = f∘τ_P − f − 1 has the N−1 distinct zeros kP (1 <= k <= N−1) and deg h <= 2 deg f; if h ≡ 0 then the pole set of f is invariant under translation by P, so it is a union of <P>-orbits of size r, giving deg f >= r > (N−1)/2 (f is nonconstant since f(P) != f(2P) when N >= 2). Theorem A' (corrected constant, explicit model): in the algebraic SLP model over F_q with +, −, ×, ÷ where every division is defined at every kP (no comparisons, no x/0 convention), computing k mod p for all kP, 1 <= k <= N, requires length >= log2((N−1)/6). The Ω(n^2) bit-cost statement holds only under the extra charge of Ω(log q) bit operations per field operation; it is not a bit-complexity lower bound for ECDLP.

## Provenance
Corrected variant of HYP-5a550ab6-75ad-4e6b-a08c-af2a066c69c7 from blind adversarial review RUN-4b283c25-b43d-4720-994d-3c285789a273 (REV-83ec2fc9-e871-4434-a5da-49db92c61a55).

## Status
Reviewed (model review, not formal). Novelty unsettled.
