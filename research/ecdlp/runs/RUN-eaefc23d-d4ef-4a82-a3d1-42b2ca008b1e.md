# RUN-eaefc23d-d4ef-4a82-a3d1-42b2ca008b1e — Round 19 / frontier explorer I (TSK-9a54da92-9afe-4d8a-b907-20336f7adb0a)

Verdict up front: **both long shots are killed.** (1) Mahalanobis–Mallick "Problem L" is exactly a zero-sum-subset
search in Z_r over about C(N,l) ≈ r supports; every solver I can state costs Θ(r) (their own) or Θ(√r) (generic
meet-in-the-middle, no better than rho). The survey's "exponent about 1" estimate is **verified**. (2) Every group-theoretic
weakness is an isogeny invariant (trivially negative); the one non-invariant structure (j = 0 or 1728 automorphisms) is
class-wide, occurs for a fraction ≈ 2.5/√p of curves, and is worth at most a constant factor √6. No speedup over √r is claimed.
Nothing here is a proof; all numbers are toy-size experiments.

## Question, selection rationale and inputs
Role: frontier-explorer (docs/roles/frontier-explorer.md). Read: AGENTS.md, role file, STATUS.md, survey.md (round17),
RUN-58dee679 (inventor B, volcano ascent, isogeny-to-j=0 fraction about p^-0.47). Directions already closed (STATUS/B): isogeny
ascent to j=0 on constructed floors, Aut-orbit rho, transfers (HYP-caa15771). I reuse B's finding as a prior and measure the
exact distance question that B named as "the only quantitatively interesting handle".

Sources actually read (retrieved 2026-11-03 via WebFetch; the PDFs were saved locally and extracted with pdftotext):
- S14 Mahalanobis–Mallick, arXiv 1703.07544v3: **full text read** (12 pp.): Thm 2.1–2.3, Alg. 1, Thm 3.1–3.2, Problem L, Alg. 2, §5.1.
- S15 Mahalanobis, "A Guess and Determine Attack on the ECDLP", arXiv 2607.09814v2: **abstract, §1.1, §5 (algorithm, pseudocode, Tables 1–2)
  read; §3–4 (matrix reductions, hyperplane arrangements, signatures) only skimmed via keyword search.** Not re-implemented.
- Not retrieved (recollection, marked unverified): Galbraith–Hess–Smart path finding between isogenous curves in about √h steps;
  Kohel / Fouquet–Morain volcano structure; Deuring/Schoof class-number count of curves per trace (used as a formula, checked below by 2p+6 total).

## The exact reduction (Problem L)
Fix n', l; N = 3n'+l. Choose N distinct multiples: P_i = s_i P (i ≤ N/2-ish) and Q_j = -t_j Q. Let ν_{n'}(x:y:1) ∈ F_q^D,
D = C(n'+2,2), be the degree-n' Veronese row, and M ∈ F_q^{N×D} the matrix of those rows. Then:
1. (Thm 2.1, Cayley–Bacharach/Riemann–Roch) 3n' distinct points of E(F_q) lie on a degree-n' curve iff they sum to O.
2. rank M = 3n' for general points (n' ≥ 1), so the left kernel K ⊂ F_q^N has dimension exactly l (Thm 2.3).
3. K has a nonzero vector with ≥ l zeros iff some l×l column-minor of the l×N basis matrix of K is singular iff some 3n'-subset S of the
   points sums to O. (Support of the vector = S.) Problem L = "given an l-dim subspace W ⊂ F^N, find a vector of W with l zeros".
4. A zero-sum S containing both types gives A·P − B·Q = O with A = Σ s_i, B = Σ t_j over S, hence m = A/B mod r (B ≠ 0).
So Problem L is *exactly* a k-sum problem (k = 3n') over the N random multiples, restated as a Plücker-coordinate vanishing problem.
Expected number of zero-sum supports is C(N,l)/r; the linear algebra over F_q adds no information beyond evaluating that predicate
on supports. The paper sets C(N,l) ≈ r with N = O(log r).

**E1 (exact check, e1_equiv.py, seed 1).** For all C(N,3n') subsets on 4 toy curves (n' = 1,2,2,3; N = 6,12,12,18; subsets 20, 924, 924, 48620):
rank(M_S) < 3n' iff sum_S = O held for **all 50,488 subsets, 0 disagreements**; rank M = 3n' (n'=3: D = 10, rank 9), kernel dimension = l in every case.

## Solvers and their cost
- **Paper Alg. 1 + Alg. 2** (diagonalise two l×l blocks of K, look for one extra zero). It inspects only ≈ 2l(l+1) of the C(N,l) supports per pass.
  Per-pass success P2 = c·l²/r. Claimed: Alg. 1 success 0.63, total 0.6(log p)²/p per pass, "only little better than exhaustive search" (§5.2).
- **Exhaustive Problem L**: test all C(N,l) supports (each a l×l determinant, or Gray-code rank-one updates, ≥ l² field mults).
- **Generic MITM (mine)**: N ≈ log2 r + 1 multiples, enumerate subset sums of each half (2·2^{N/2} ≈ 2√(2r) group additions), match sums. Any zero-sum subset of any
  size solves the DLP. This is a birthday collision on subset sums; it needs no linear algebra.
- Paper 2 (zero minor via hyperplane-arrangement signatures, defect d): polynomial for fixed d, but its own Table 2 gives
  log2 C(ℓ'+d,d−1) + log2 C(ℓ',d) = 53+48 = 101 for log2 p = 100 (and 60+53 vs 112, etc.), i.e. exponent ≈ 1; the authors write that the attack is "no better than exhaustive search".
  Its penultimate-intersection rho is a birthday over C(2ℓ,ℓ−1) objects, ≈ √p steps each costing a kernel computation: ≥ √p·poly. Not implemented here.

### E2 — per-pass success of the real algorithm (real linear algebra over F_q, 15 curves, e2_alg2.py)
Prime-order curves, l = 3n', N = 2l; all returned m verified (m·P = Q), 0 wrong answers. Normalised c = P2·r/l² (se ≈ 0.04–0.3):
| n' | r | P2 | c |
|---|---|---|---|
| 2 | ≈190 (r < C=924, saturating) | 0.32–0.34 | 1.6–1.7 |
| 2 | ≈1900–2100 | 0.041–0.050 | 2.3–2.8 |
| 2 | ≈16500–21000 | 0.0042–0.0060 | 2.2–2.9 |
| 3 | ≈25300–29300 (C=48620) | 0.0073–0.0091 | 2.6–2.85 |
c is flat (≈ 2.5) over a factor 150 in r, so P2 ∝ l²/r: **exponent 1 in r confirmed**; the constant is ≈ 2l(l+1)/l² times Alg. 1's success, consistent with the
number of inspected supports. (The paper's "(log p)²" is l² up to a constant, since C(2l,l) ≈ r gives l ≈ (log2 r)/2.)
Total cost of Alg. 1+2 ≈ (1/P2)·(N point multiplications ≈ 2l·1.5·log2 r group ops) ≈ 3 r log2 r/(c·l) ≈ 6r/c ≈ 2.4·r group operations (+ ≈ r·l/3 field multiplications for elimination).
That is about 5× naive exhaustive search (r/2), and ≈ r/√r = √r times worse than rho asymptotically. **Verified: the survey's estimate (exponent ≈ 1) is right.**

### E3 — cost fits against a rho control (e3_cost.py; 60–105 instances per size; counted group additions/support tests)
EXH and MITM use the dlog-equivalent zero-sum test (justified by E1); RHO is real curve arithmetic (r-adding walk, Brent cycle detection, 16-entry table,
setup counted). Instances: 3 prime-order curves per size r ≈ 2^10..2^18 for RHO/EXH/MITM; EXH to 2^21 and MITM to 2^34 in the log model (random prime r, 8–30 instances).
Fit y = α·x^β + γ on relative error (grid in β, linear LS for α, γ; no log-log), bootstrap over instances:
| solver | r range | fit | note |
|---|---|---|---|
| EXH (Problem L exhaustive, paper parametrisation) | 2^10..2^21 | free β = 0.94, CI [0.82, 1.00]; fixed β = 1: α = 1.04, γ = 383 | mean tests/r = 0.9–1.4 at every size |
| MITM | 2^10..2^34 | fixed β = 1/2: α = 3.5, γ = 281 (rel. SSE 0.25); free β = 0.48 CI [0.46, 0.48] | α√r + γ, memory ≈ √r; ratio to RHO ≈ 1.3 at 2^18 |
| RHO control | 2^10..2^18 | fixed β = 1/2: α = 2.97, γ = 370 (rel. SSE 0.024); free β = 0.36, CI [0.30, 0.44] | γ and β confounded over 8 bits (setup ≈ 360 ops); β = 1/2 is the better-conditioned model |
Raw: `experiments/round19-frontier-i/raw_*.jsonl`, `analysis_e3.json`; evidence under `runs/RUN-eaefc23d-…-command-*.evidence`.
So: every Problem-L solver is Θ(r) (paper) or Θ(√r) (generic); none beats rho. At toy sizes the Θ(r) solver is 3× (r = 2^10) to about 500× (r = 2^21) slower than rho in ops, growing like √r.

### Why no better solver should exist (exact obstruction, heuristic where marked)
A zero-sum support is a collision-type event of probability ≈ 1/r in Z_r. Subset sums of N = O(log r) points give C(N,l) ≈ r supports, so success needs either
testing ≈ r supports (linear algebra tests ≈ l² supports per O(l³) work: no help) or a birthday over ≈ √r partial sums (MITM). Wagner-style k-tree filtering
(zeroing partial bits of subset sums) needs a way to read bits of the *discrete log* of a point, which is the problem itself; coordinates of s·P carry none
(consistent with the lab's equidistribution results). So reaching below √r would require partial-zero information the instance does not give. **Heuristic, not a proof**; a generic-group Ω(√r)
lower bound applies to the subset-sum predicate, but the linear algebra uses coordinates, so it is not a theorem for this algorithm family.

Status: **Idea 1 killed** (cost Θ(r) measured, Θ(√r) best known, kill criterion ≥ √p met).

## Task 2 — isogeny distance to a weak curve
### Exact obstructions (derived)
Let E, E' be F_p-isogenous (Tate). Then #E = #E', t, r, and the embedding degree k = ord_r(p) are equal (they depend only on p, t and r), so: small embedding degree (MOV/Frey–Rück),
anomalous (#E = p, SSSA), and supersingularity are properties of the class, not of the curve. Supersingular is also excluded for prime order r: #E = p+1 is even. Hence for these
weaknesses the "nearest weak curve" is the curve itself or no curve at all: distance 0 or infinity. For a rational isogeny φ of degree coprime to r, φ restricted to E[r^∞] is a group isomorphism,
so ECDLP transports exactly (and for degree dividing r the image of ⟨P⟩ collapses: nothing is gained; HYP-caa15771 covers this).
**E4-INV (e4_isog.py INV):** 380 explicit Vélu 2-isogeny steps on random toy curves (p < 2000; seed 7, 150 trials): order changed in 0, and k with φ(Q) = k·φ(P) held in 380/380.
Non-invariants are only the endomorphism *order* (conductor), j, and the automorphism group. Aut(E) ⊋ {±1} needs End⊗Q = Q(π) ∈ {Q(√−3), Q(i)}; this field is the same for all curves in the class
**even over F̄_p** (π^k ∉ Q for ordinary E), so j = 0 / 1728 is reachable by isogeny iff d_K ∈ {−3, −4}, a condition on t² − 4p alone; otherwise there is no path of any length, over any extension.
Further, for every E' in the class and every non-scalar endomorphism α ∈ End(E') ⊂ O_K: deg α ≥ |d_K|/4. If |d_K| ≈ p (generic), **no curve of the class has an endomorphism of degree below p/4**,
so GLV/GLS-type and efficient-endomorphism structure is absent class-wide.

### Measured weak fraction and path cost (E4-CM, E4-STAT)
Fraction of curves (F_p-iso classes weighted by Kronecker class numbers N_t = H(4p−t²); total Σ N_t = 2p+6 verified, e.g. 2024 at p = 1009) with d_K ∈ {−3,−4}:
32 primes p ≡ 1 (mod 12), 577 ≤ p ≤ 1.07·10^6 (the congruence class where both can occur; P = 0 when p ≡ 2 mod 3 for d_K = −3 and p ≡ 3 mod 4 for −4):
**P_cm = α·p^β + γ with β = −0.49, CI [−0.55, −0.43] (bootstrap over primes); P_cm·√p = 2.5 ± 0.4 (range 2.0–3.4).** Agrees with B's −0.467 and with the prediction −1/2.
Weighted by prime order (p ≤ 39097; 17 primes with traces restricted to prime #E) the d_K = −3 fraction is 0–7% and noisy; not fitted.
Path cost when the class does contain j = 0 or 1728: ascent to the crater (a single vertex, class number 1) costs Σ_ℓ e_ℓ·ℓ over the conductor f = ∏ ℓ^{e_ℓ}
(model: one Vélu step of degree ℓ costs ≈ ℓ; ℓ = 2 validated by B, other ℓ unvalidated). This is below √p for 82–100% (mean 96%) of the CM class weight per prime; the rest has a prime
factor ℓ of f near √p, killed by the criterion. Distance in steps is O(log f), but cost depends on the *size* of the primes in f.
For targets that are not canonical (any other specific curve, class number h ≈ √p) a meet-in-the-middle walk costs about √h ≈ p^{1/4} steps (unverified recollection, Galbraith–Hess–Smart); the generic class walk
cannot find a canonical weak curve, because none exists (|d_K| ≈ p: median |d_K|/p between 1.6 and 3.3 over traces in the 17 sampled primes, unweighted).

### Value of the weakness when reached
j = 0 / 1728 only give an automorphism quotient |Aut| = 6 or 4: constant ≤ √6 on the walk length (B1/B2, measured 1.45× and 2.6× with noisy baseline). Other small-|d_K| curves
have no units beyond ±1 and no known group-order or rho gain from a small-norm endomorphism beyond constants. Expected gain over a random curve ≈ 2.5/√p · log2(√6) bits → 0.

Status: **Idea 2 killed.** Invariant weaknesses are trivially negative; the only non-invariant weakness has probability ≈ 2.5/√p and gain ≤ √6.

## Claims and verification
- C1 (verified experiment, E1): Problem-L equivalence rank-deficient ⇔ zero-sum on all 50,488 tested subsets, 0 exceptions.
- C2 (measured, E2): per-pass success of paper's Alg. 2 = c·l²/r with c ≈ 2.5, flat over r = 190..29000, so exponent 1 in p; total ≈ 2.4 r group ops.
- C3 (measured, E3): exhaustive Problem L: β = 0.94 [0.82, 1.0]; generic MITM: α√r+γ with α ≈ 3.5; rho control α ≈ 3.0. No solver beats √r.
- C4 (derived + checked): isogeny invariants; deg α ≥ |d_K|/4 (elementary, quadratic orders); prime-order forces non-supersingular.
- C5 (measured): P(isogenous to j = 0 or 1728) ≈ 2.5·p^{-1/2} for p ≡ 1 mod 12.
No Lean statement is made; none is claimed to be novel; the survey's Alg. 1/2 claims are checked, not endorsed. Proof status: not-applicable.

## Outcome, limitations and next action
Established at toy level: both ideas are dead by the pre-set kill criterion. Limitations: sizes r ≤ 2^21 (EXH), 2^18 (RHO, real curves); 60–105 instances per size, so means are heavy-tail-sensitive;
EXH/MITM use a dlog-model equivalence validated only on 4 curves (E1) while Alg. 2 uses real linear algebra only for n' ≤ 3; rho baseline setup counted generously (γ ≈ 370) and its free-β fit is poorly
conditioned; paper 2's algorithm was read, not implemented (its own table supports exponent ≈ 1); ascent cost model for ℓ > 2 not validated by explicit Vélu code; S15 §3–4 only skimmed;
class-number weights assume the standard Deuring/Schoof count (sanity-checked only via 2p+6); no independent review (single model, self-reported identity claude-sonnet-5-5).
Next action: none promising on these two routes. If a reviewer wants closure, implement the S15 signature algorithm at ℓ ≤ 12 and measure its pass count against C(2ℓ,ℓ−1); I predict a count of order r. A different direction would need *partial-zero* information on discrete logs (the missing Wagner ingredient), which is the DLP itself.

Files (all under /home/user/math/research/ecdlp/experiments/round19-frontier-i/): ecL.py, e1_equiv.py, e2_alg2.py, run_e2.sh, e3_cost.py, e4_isog.py, analyze.py, analyze_cm.py, analysis_e3.json, raw_*.jsonl.
Evidence: /home/user/math/research/ecdlp/runs/RUN-eaefc23d-d4ef-4a82-a3d1-42b2ca008b1e-command-*.evidence.
