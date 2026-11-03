# HYP-ad5bc0e3-30cc-4eb8-b823-4df42edd44a6 — Cover-based Jacobian index calculus does not beat sqrt(p) for prime-field curves (known algorithms)

## Exact statement
Let E/F_p, p prime, #E = r prime, and pi: C -> E a cover of genus g with computable pullback. (A) For fixed g >= 2 (Diem/GTTD, O~(q^{2-2/g})) or plane degree d >= 4 (Diem, O~(q^{2-2/(d-2)})) the cost exponent is >= 1 > 1/2. (B) For g >= delta log q the L_{q^g}(1/2) cost (Enge–Gaudry) is q^{omega(1)}; for g >= (log q)^2 the L(1/3) cost (Enge–Gaudry–Thomé) exceeds sqrt(q) for large q. (C, heuristic) generic degree-1 factor-base index calculus on J_C costs >= ~q/20; formulas dip below sqrt(q) only for g = O(log q / log log q) where no theorem applies. (D) Pullback relations have disjoint supports and determine no individual factor-base logarithm. Missing ingredient: a factor base of size <= p^{1/2-eps} adapted to pi^*(E(F_p)) with fast decomposition.

## Provenance and status
A proved from cited statements (Diem arXiv math/0606607, Diem JTNB verified; Gaudry 2000 and Enge–Gaudry regime unverified recollection); B conditional on regimes; C heuristic; D elementary. One sentence in Enge–Gaudry–Thomé intro read literally conflicts with C (treated as loose; unresolved). Cover t->t^d genus (3d-1)/2 (d odd), (3d-2)/2 (d even), generic h: 2d-1 (toy-checked).

Status: proof-attempt; unreviewed.

## Next
Decisive test T2 (genus-2 index calculus on J_C at p ~ 2^20) not run; literature-verify Gaudry 2000 and Enge–Gaudry regime; resolve EGT sentence.
