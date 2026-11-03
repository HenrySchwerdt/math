# RUN-fec2442f-7d58-41e5-a4d0-ee0dbd2a8d88 — sealed Round-1/B submission (universal transformations of ECDLP)

Model identity (self-reported from system prompt): Sonnet 5.5, model ID `claude-sonnet-5-5`. Not runtime-verified by the repository.
Status labels used below: KNOWN (published; source given), ELEMENTARY (short proof included here, not formally verified), CONJECTURE (mine), UNVERIFIED RECOLLECTION (not checked in this run).

## 1. Question and inputs
Task TSK-30c839fa-0520-4fd6-a552-a243b2987d5e (ECDLP-3). Question: can an arbitrary instance (E/F_q, P of prime order r, Q=[k]P) be mapped in (quasi-)linear time to an equivalent instance with exploitable extra structure, with k recoverable? Inputs read: AGENTS.md, docs/METHODOLOGY.md, docs/roles/algebraic-geometry.md, the TSK JSON, HYP-2de84d42-* (universal O(n log n) objective, aspirational and unproved). Per the independence rule no other RUN or HYP file was read. Nothing here proves or disproves the universal objective.

## 2. Approach and observed execution
- Web lookups (5 of ~25 budget), only to confirm bibliographic data: Semaev 1998 (AMS page), Jacobson-Koblitz-Silverman-Stein-Teske 2000 (DOI 10.1023/A:1008312401197), Galbraith-Hess-Smart 2002 (ePrint 2001/054), Jao-Miller-Venkatesan 2009 (arXiv 0811.0647), Petit-Quisquater 2012 (ePrint 2012/146). Search snippets gave abstracts only; no full texts were read. All other citations are UNVERIFIED RECOLLECTION.
- Experiments (Python 3 stdlib only, trial-division factoring, naive point counting), code and output in `/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/agentB/` (`emb.py`/`emb.out`, `cnt.py`/`cnt.out`); these are scratch files outside the repo.
  - E1 (`emb.py`): 1498 random short-Weierstrass curves over primes p in [1000,3000); r = largest prime factor of #E. Observed: 12 anomalous (#E=p); 239 with ord_r(p)<=6, but these are dominated by tiny r (r<=5 excluded only), so this number is NOT evidence about cryptographic sizes; mean of ord_r(p)/r over non-anomalous curves = 0.580 (so the embedding degree is typically of order r, consistent with the known heuristic). Also checked for all primes q<400, r<200 that #{x in F_q^*: x^r=1} = gcd(r,q-1): 0 mismatches.
  - E2 (`cnt.py`): for p in {10007,20011,40009,80021}, count of traces t in the Hasse interval for which #E=p+1-t has a prime factor r>4*sqrt(p) with ord_r(p)<=6: 1,1,2,3 out of 401,565,801,1129 traces; the proven bound (Lemma B3) is M(M+1)=42. Consistent with the bound; finite tests only.
- No Lean was compiled in this run; the Lean statements in section 7 are untested sketches.

## 3. Abstract transfer requirements
Setting: G=<P>, |G|=r prime, instance (P,Q), Q in G. A transfer is a pair (T, phi) plus a decoder.
R1 (map): phi: G -> T (or on the ambient E(F_q)), where T is a structure with a DLP-like solver S.
R2 (homomorphism): phi(aP+bP)=phi(aP) * phi(bP) for the group law of T (or a bilinear/pairing relation with an auxiliary point R, giving a hom x -> e(x,R)). Without it no relation between phi(Q) and phi(P) exists.
R3 (injectivity on G): ker phi != G. By Lemma L1 (r prime) this is equivalent to phi nontrivial on G, and then phi is injective, so k mod r is determined by (phi(P),phi(Q)).
R4 (cost): computing phi(P), phi(Q) and the description of T costs poly(n), ideally n polylog n; size of T-elements poly(n) (Weil descent/Jacobian transfers can blow up the dimension, pairings blow up the field degree).
R5 (target easiness): S solves "phi(Q)=phi(P)^k" in cost well below sqrt(r) (the generic bound). Exactly what makes it easy, by type: (a) T additive torsion-free or additive in char p with r=p: DLP = division/linear algebra (anomalous attack, p-adic log); (b) T=F_{Q}^*: the multiplicative group of a finite field has an index-calculus/NFS algorithm using the ring structure (smoothness of integers/polynomials, factor base) - subexponential L(1/3) in log Q, so useful only when log Q is small compared with log r (embedding degree small: log Q = k log q); (c) T = Jacobian/class group where divisors split into small primes with decent probability (genus large vs log q) -> index calculus; (d) T is a group whose order is smooth - this can never apply with r large (Lemma L3).
R6 (decoder): k recovered mod r from the T-solution (e.g. discrete log in mu_r gives k mod r directly; p-adic log ratio gives k in Z_p).
Key necessary conditions proved/known below: L1 (hom from prime-order cyclic groups), L2 (nontrivial hom needs r | |T|), L3 (Pohlig-Hellman style easiness is incompatible), L4 (rigidity: no algebraic hom from E to linear groups), L5 (Frobenius-equivariance obstruction), L6 (isogeny invariance of the arithmetic obstructions).

## 4. Known transfers
| Transfer | Hypothesis needed | Cost | Why not generic | Source |
|---|---|---|---|---|
| MOV / Frey-Rück (Weil / Tate-Lichtenbaum pairing into mu_r subset F_{q^k}^*) | r | q^k-1 (embedding degree k), r != p; for MOV E[r] in E(F_{q^k}) | pairing evals poly(k log q), then DLP in F_{q^k}^* subexp in k log q | k = ord_r(q) is typically ~r for random curves (E1; Balasubramanian-Koblitz); fraction with k<=M is <= about M^2/sqrt(q) by Lemma B3; kills only supersingular k<=6 and sparse pairing-friendly curves | Menezes-Okamoto-Vanstone, "Reducing elliptic curve logarithms to logarithms in a finite field", IEEE Trans. Inf. Theory 39 (1993) [unverified recollection]; Frey-Rück, "A remark concerning m-divisibility and the discrete logarithm in the divisor class group of curves", Math. Comp. 62 (1994) [unverified recollection]; Balasubramanian-Koblitz, J. Cryptology 11 (1998) [unverified recollection] |
| Semaev / Smart / Satoh-Araki (anomalous) | #E(F_p)=p (r=p), p-adic lift + formal group log, or Artin-Hasse/Semaev in char p | poly(log p) | needs r=p; for r != p the r-torsion lifts to E(Q_p)[r] where p-adic log vanishes (see B4) | Semaev, "Evaluation of discrete logarithms in a group of p-torsion points of an elliptic curve in characteristic p", Math. Comp. 67 (1998), 353-356 (verified bibliographic data); Smart, J. Cryptology 12 (1999); Satoh-Araki, Comment. Math. Univ. St. Pauli 47 (1998) [both unverified recollection] |
| GHS Weil descent | E over F_{q^n} (n>1, composite for GHS in char 2), curve C over F_q covering E with small genus; cover found by isogeny search | heuristic subexponential when C has genus ~ small and attack factor base of rational points, Gaudry-style | needs extension field; prime fields have no subfield; many curves have no suitable cover/isogeny (Galbraith-Hess-Smart enlarge the class but only over composite-degree char-2 fields); Diem showed descent covers of large genus do not help in general | Galbraith-Hess-Smart, "Extending the GHS Weil descent attack", EUROCRYPT 2002, LNCS 2332, 29-44 (verified); Gaudry-Hess-Smart, J. Cryptology 15 (2002) [unverified recollection]; Frey 1998 talk/Diem [unverified recollection] |
| Summation-polynomial index calculus | E over F_{q^n} (small n), factor base V = F_q-subspace; relation = point set summing to given point; Semaev polynomial S_{m+1} | Gröbner/Weil descent system solving; Gaudry: q^{2-2/n}; Diem: for n fixed Otilde(q^{2-2/n}); Petit-Quisquater: heuristic subexponential for char 2, n ~ >2000 breakeven | In a prime field no subfield => no algebraic definition of a "small" factor base; encoding small integers as a factor base gives systems of exponential degree 2^{m-1} with exponentially many variables | Semaev, "Summation polynomials and the discrete logarithm problem on elliptic curves", ePrint 2004/031 [unverified recollection]; Gaudry, J. Symb. Comput. 44 (2009) [unverified recollection]; Diem, Compositio 147 (2011) [search did not return; unverified recollection]; Petit-Quisquater, ASIACRYPT 2012 pp. 451-466 (verified) |
| Isogeny walks / random self-reducibility | E' isogenous to E over F_q with smooth-degree isogenies | each step poly(log q); walk length polylog by expansion (GRH) | #E(F_q) is an isogeny invariant (Tate), so r, embedding degree, anomalous status never change; only End-geometry dependent weaknesses (GHS cover, automorphisms, GHS-vulnerable class) can be reached; also DLP hardness is random self-reducible within a class: a weak class member gives all members only if the weak members are a non-negligible fraction | Jao-Miller-Venkatesan, J. Number Theory 129 (2009) 1491-1504, arXiv:0811.0647 (verified); Galbraith-Hess-Smart 2002 (verified); Teske, "An elliptic curve trapdoor system", J. Cryptology 19 (2006) [unverified recollection] |
| Xedni calculus | lift points to Q-curve with dependent lifted points; use rank drop | feasibility depends on probability of rank drop | JKSST analyze: probability of dependence is prohibitively small; lifted points have huge heights; Silverman's own paper expected need for 9 lifts [details unverified recollection] | Silverman, "The xedni calculus and the elliptic curve discrete logarithm problem", Des. Codes Cryptogr. 20 (2000), 5-40; Jacobson-Koblitz-Silverman-Stein-Teske, "Analysis of the xedni calculus attack", ibid. 41-64, DOI 10.1023/A:1008312401197 (verified citation; contents beyond abstract not read) |
| Genus-g cover / GHS-Diem class | Jacobian of cover C->E with g large vs log q, divisor smoothness | Enge-Gaudry L_{q^g}(1/2) for g >~ log q; Gaudry-Thome-Theriault-Diem q^{2-2/g} for fixed g | needs a cover whose Jacobian points are efficiently computable and g large; group order grows q^g >> r which hurts | Enge-Gaudry [unverified recollection]; Gaudry-Thome-Theriault-Diem, Math. Comp. 76 (2007) [unverified recollection] |
| Others, brief | Smith: isogenies to Jacobians of genus 3 hyperelliptic (J. Cryptology 2009) [unverified recollection]; Joux-Vitse small extension fields (J. Cryptology 2013) [unverified recollection]; Petit-Kosters-Messeng prime-field algebraic approaches (PKC 2016) [unverified recollection] | | | |

## 5. Candidates
Fields per candidate: (1) exact statement; (2) property relied on; (3) why it could help; (4) what must be proved; (5) what could invalidate it; (6) cheapest decisive test; (7) existing results.

### B1 — Hom-order obstruction (ELEMENTARY; impossibility)
1. Let G be a group of prime order r, T any group, f: G->T a homomorphism. Then f is trivial or injective; if f is nontrivial then r divides |T| when |T| is finite (and T has an element of order r otherwise). For T=F_{Q}^*: nontrivial hom exists iff r | Q-1 (Cauchy, cyclic group F_Q^*). For T=(F_Q,+) with Q=p^m: nontrivial hom iff r=p. For T torsion-free (Z, Q_p,+, Z_p,+, R): only trivial hom when r != ... all trivial. For T=GL_n(F_ℓ): iff r | |GL_n(F_ℓ)|.
2. Property: Lagrange + prime order.
3. Pins down the necessary arithmetic coincidence for any "target = field/torus/matrix group" transfer: the pairing field degree k must satisfy r | q^k-1; for the p-adic/additive transfer r=p.
4. Nothing more (see Lean L1/L2).
5. Nothing; it is a theorem. It does not cover set-theoretic or multi-valued transfers, pairings with extra point R (those are homs x -> e(x,R) but still land in mu_r), or transfers that give only partial information.
6. Done by experiment E1 (counting hom check, 0 mismatches) and Lean (section 7).
7. Standard group theory (no specific citation needed).

### B2 — Pohlig-Hellman incompatibility (ELEMENTARY; impossibility)
1. If T is finite with |T| being B-smooth, and f: <P> -> T nontrivial (so r | |T|, by B1), then r <= B. Hence no transfer to a group whose DLP is easy merely because the group order is smooth is possible for r > B. Corollary: any "easiness" of T must come from representation structure (additive realization, ring structure/smoothness in a function/number field, p-adic filtration), not from group order.
2. Lagrange (B1).
3. Eliminates the class "find a smooth-order target group" (e.g., a random-isogeny search for smooth order doesn't work: #E is an isogeny invariant, and an auxiliary group with smooth order cannot contain an image of order r).
4. Exactly the statement above (trivial).
5. The target need not be finite (use Z/N-module structure with r | N; then N has factor r and an N-smoothness argument fails again). Also targets where only an approximate hom (not exact) exists are not covered; see B9.
6. None needed; trivial.
7. Pohlig-Hellman, IEEE Trans. Inf. Theory 24 (1978) [unverified recollection].

### B3 — Embedding-degree sparsity counting lemma (ELEMENTARY; counting)
1. Fix prime power q and integer M>=1. Call a trace t (|t| <= 2 sqrt q) M-bad if #E=q+1-t has a prime factor r > 4 sqrt q with ord_r(q) <= M. Then the number of M-bad traces is at most M(M+1). Proof: r | q^m-1 for some m<=M, so r | Pi_{m<=M}(q^m-1) < q^{M(M+1)/2}; since r > 4 sqrt q > q^{1/2}, at most M(M+1) distinct such primes; each r > 4 sqrt q = width of the Hasse interval has at most one multiple of... at most one value of q+1-t in the interval divisible by r. Hence <= M(M+1) bad values of t out of ~4 sqrt q. The bound is on traces; isomorphism classes of curves are weighted by Hurwitz class numbers H(t^2-4q), which are roughly uniform away from extreme t (not proved here), so the fraction of curves is O(M^2/sqrt q) under that weighting assumption only.
2. Property: r large vs the Hasse width forces unique multiple; cyclotomic divisibility.
3. Quantifies the failure of "any curve has small embedding degree": a generic curve over F_q with prime-order r ~ q has embedding degree essentially > polylog(q) (all M <= polylog), so MOV/FR is exponentially unlikely to apply (ord_r(q) ~ r under random-order heuristic: E1 mean 0.58 r).
4. A weighted statement for curve counts (needs class-number bound; e.g., Lenstra 1987 gives H(t^2-4q) = O(sqrt q log q (log log q)^2)), giving fraction O(M^2 polylog / sqrt q) rigorous; not proved in this run.
5. Cofactor large (r<4 sqrt q) escapes the lemma; curves with small cofactors are the relevant ones for cryptography, where r > 4 sqrt q holds automatically when the cofactor <= sqrt(q)/4.
6. E2 above (finite check; 1-3 hits vs bound 42).
7. Balasubramanian-Koblitz 1998 (unverified recollection) proves a closely related probability statement; Lenstra, Ann. Math. 126 (1987) "Factoring integers with elliptic curves" for the class number bound [unverified recollection].

### B4 — p-adic lifting of the r-torsion for r != p kills the information (ELEMENTARY/KNOWN-style; impossibility for the SSSA generalization)
1. Let E/F_p be an elliptic curve with p != r. For any lift E~/Z_p, reduction induces an isomorphism E~(Q_p)[r^inf] -> E(F_p)[r^inf] (Hensel; kernel E~_1(Q_p) is a pro-p group, which has no r-torsion). So P lifts uniquely to P~ in E~(Q_p)[r] and Q lifts uniquely to Q~ = [k]P~. But the formal logarithm is defined on E~_1(Q_p) and every element of E~(Q_p)[r] is outside E~_1; any hom E~(Q_p) -> (Q_p,+) is trivial on torsion (B1: torsion-free target). Hence no p-adic additive map recovers k. In the anomalous attack (r=p) the point [p]P~ lies in the formal group, where the log is injective on E_1 ~ pZ_p; that is the exact point where r=p is used.
2. Property: orders of r-torsion in a pro-p group; torsion-freeness of the target.
3. Explains why the lift-to-Q_p trick fails precisely for r != p, and why generic lifts to Z_p/ number fields lose the discrete log (arbitrary lifts Q~' = Q~ + T, T in E_1, destroy the relation).
4. Hensel/torsion statements for E~(Q_p) (standard; Silverman AEC VII, not re-derived here).
5. Using a different structure than additive Q_p, e.g. the multiplicative/Tate-curve structure E(Q_p) = Q_p^*/q^Z when E has split multiplicative reduction - not relevant to good-reduction F_p curves; Lubin-Tate/Serre-Tate canonical lifts are a possible refinement (see B7).
6. Check on tiny examples (e.g. p=11,r=5) with Sage/PARI: confirm that lifted r-torsion has nonvanishing reduction and log = 0. Not run here (no CAS in my environment).
7. Silverman, AEC, Ch. VII (formal group) [unverified recollection]; Smart 1999, Semaev 1998, Satoh-Araki 1998.

### B5 — Rigidity: no algebraic hom from E into a linear group (KNOWN-style theorem; impossibility)
1. Let E be an elliptic curve over a field K and G a linear (affine) algebraic group over K (G_a, G_m, tori, unipotent groups, GL_n, any affine group scheme of finite type). Every morphism E -> G of K-varieties over K-bar is constant; in particular every algebraic group hom E -> G is trivial. Proof: E is proper and connected, G is affine, so the image is a proper connected closed subvariety of an affine variety, hence a point.
2. Property: properness of E vs affineness of G.
3. Consequence: every nontrivial transfer from <P> into F_{Q}^*, an additive group, or an algebraic torus must be non-algebraic in P alone: pairings (bilinear, using an auxiliary point R and the full r-torsion over an extension) or maps defined only on finite sets of points (reduction/lifting of torsion). Rules out "universal natural transformation" E -> G_m, E -> G_a as morphisms.
4. Nothing further (standard); however the extension "no natural-in-E construction" requires defining natural precisely.
5. Does not exclude non-algebraic maps (e.g. Frobenius-defined maps on finite point sets, trace-based maps on E(F_q), p-adic analytic maps from E~(Q_p)); this is the loophole B4 and B6 explore.
6. Trivial; check by Lean? (hard in Mathlib: proper vs affine not available in this form).
7. Standard algebraic geometry (Hartshorne II.; Silverman AEC III) [unverified recollection of numbering].

### B6 — Frobenius-equivariance obstruction (ELEMENTARY; impossibility for "defined-over-F_q" transfers)
1. Let F=Frob_q act on the r-torsion module E[r] (a 2-dim F_r-space). Let P satisfy F(P)=P (P in E(F_q)). Let M be an F_r-module with a linear action of F by a scalar c in F_r^*. If f: E[r] -> M (or just f: <P> -> M) satisfies f(F x) = c f(x), then (1-c) f(P)=0, so f(P)=0 unless c=1 in F_r. Over F_{q^k}: the scalar for mu_r is q^k, so a nonzero equivariant f needs r | q^k - 1. For the additive target F_p with trivial action c=1 but there F_r-linear homs F_r -> F_p exist iff r=p.
2. Property: Galois equivariance (the map is defined over the field of definition) plus F-fixedness of P.
3. Unifies MOV/FR (c=q^k), anomalous (r=p), and explains why only target Galois-characters with eigenvalue 1 mod r can receive <P> naturally. Any "natural" target built from etale cohomology/Tate module has Frobenius eigenvalues among {1,q,q^2,...} mod r (E[r] has eigenvalues 1 and q when r | #E since the char polynomial x^2-tx+q has root 1 mod r). So natural transfers exist only when q^j = 1 mod r with j small.
4. Formalization of "natural" (Galois-equivariant homomorphisms defined by correspondences); then the above is a theorem for that class.
5. Non-equivariant maps (depending on choices, e.g., a chosen lift or a chosen non-rational point R) fall outside, but then computing them typically requires information equivalent to the DL.
6. Lean lemma L5 (section 7). Numerical check: for random E/F_p small, compute ord_r(p) vs r (E1).
7. Standard Galois-module/weil pairing facts (Silverman AEC III.8-11) [unverified recollection].

### B7 — Isogeny invariance (KNOWN: Tate's theorem)
1. For E, E' over F_q, E isogenous to E' over F_q iff #E(F_q)=#E'(F_q) (Tate 1966). Hence r, the field degree k=ord_r(q), anomalous status and subgroup structure of order divisible by r are shared by the whole isogeny class; an isogeny transfer can only help with End-dependent weaknesses (GHS covers, automorphism speedups, GHS-vulnerable subclasses), never with MOV or SSSA.
2. Property: Tate's theorem.
3. Explains why isogeny walks (Jao-Miller-Venkatesan, GHS-isogeny) cannot generalize the pairing/lift attacks.
4. Verified known; the open part is how many isogeny classes contain a GHS-weak member (heuristically exponentially few; unresolved).
5. A rigorous statement of the weak-member density per class is missing.
6. Experiment: compute isogeny classes over small prime/extension fields, count GHS-weak members; needs a CAS.
7. Tate, "Endomorphisms of abelian varieties over finite fields", Invent. Math. 2 (1966) [unverified recollection]; GHS 2002 (verified).

### B8 — Genus/dimension trade-off for cover transfers (CONJECTURE/heuristic; precise open requirement)
1. Given a cover pi: C -> E over F_q of degree d with C of genus g, pi^*: E -> J_C is a hom with kernel killed by d; it is injective on E[r] when r does not divide d (since pi_* pi^* = [d]). Fibre divisors pi^*(P), pi^*(Q) are computable in time poly(d, g, log q) (field extension for the fibre). Open requirement: a family of covers with g ~ c log q (so that Enge-Gaudry applies, with cost L_{q^g}(1/2)) AND with the J_C-DLP subexponential cost less than sqrt r ~ q^{1/2}. Heuristic arithmetic: with g log q = log #J, subexp cost exp(c' sqrt(g log q log(g log q))) is below q^{1/2}=exp((log q)/2) iff g log(g log q) < (log q)/(4 c'^2) up to constants; Enge-Gaudry validity needs g >~ log q; the two regimes appear incompatible (g ~ log q gives exponent ~ log q * sqrt(log log q) > (log q)/2). So the genus must be in the intermediate regime (the regime of GTTD q^{2-2/g}, which is worse than sqrt q for all g>=2 since 2-2/g >= 1 > 1/2). I did not find a regime where cover-based index calculus beats sqrt(q) on a generic E over a prime field; Weil descent beats it only when the cover comes from Weil restriction of an extension-field curve (not available for prime fields).
2. Property: genus-g divisors are smooth with probability ~1/g! (Hasse-Weil for plane curves).
3. Would transfer E(F_q) to a Jacobian where smoothness-based index calculus works, with efficient computation of pi^*.
4. A rigorous version of the regime analysis from published complexity statements (Enge-Gaudry, GTTD) which I have not read in this run.
5. If subexponential algorithms for genus-g curves over F_q in the regime g ~ (log q)^eps with q large are developed; or if covers with large "gonality-to-genus advantage" (low-degree maps to P^1 with many rational points, Diem) exist.
6. Compute for small q=10007, g in {2,3,4}: find covers of E and time index calculus (needs a CAS/Magma; not run).
7. Enge-Gaudry, Acta Arith. 102 (2002) [unverified recollection]; Gaudry-Thome-Theriault-Diem [unverified recollection]; Diem, Compositio 2011 [unverified recollection].

### B9 — Approximate-homomorphism transfer to lattices (CONJECTURE; precise open requirement + obstruction)
1. A lattice/HNP transfer would need an efficiently computable f: G -> R/Z (or Z_r) with |f(a+b)-f(a)-f(b)| <= delta (mod 1) for all a,b in G, with delta < 1/ (poly) and f not nearly constant. Ulam-Hyers stability for finite (amenable) abelian groups suggests such an f is within delta' of a true character chi_c(x)=c x/r, i.e. f(Q) approximates c k/r mod 1; then (P,Q) yields k via continued fractions once c is known. Equivalently, computing f is a "most significant bits / bit-security oracle" for the DL in G, which are not available without a structural hom.
2. Property: stability of near-characters.
3. Would send ECDLP to lattice problems (HNP) which are polynomial-time given oracle bits.
4. A precise stability theorem with explicit delta' = O(delta) for Z/r -> R/Z and the explicit reduction from "approximate character" to k.
5. Existence of an efficiently computable nonconstant approximate character is itself equivalent to partial DL knowledge (bit security results). Boneh-Venkatesan 1996 [unverified recollection] show MSB oracles reduce to the HNP, not that they exist.
6. Test: for small p (<=2^20), exhaustive search over polynomial-size families of candidate f (e.g. f(x,y)= (x/p) or fractional parts of low-degree polynomials in coordinates) to find nonconstant approximate characters: compute max_{a,b}|f(a+b)-f(a)-f(b)| and compare to 1/2.
7. Hyers 1941 (unverified recollection); Boneh-Venkatesan CRYPTO 1996 [unverified recollection].

### B10 — Abstract-isomorphism transfers are exactly DL-hard (ELEMENTARY; impossibility)
1. Let (P,E,F_q) and (P',E',F_q') be two instances with the same prime order r, and let iota: <P> -> <P'>, P -> P', the unique hom. If an algorithm computes iota(x) from x for all x in <P> in time t, then it solves ECDLP on E in time t + (time for DL in <P'>) only when DL in <P'> is easy; conversely, computing iota on a single input Q yields [k]P' = iota(Q), so DL in E with base P reduces to DL in E' with base P' (and reverse). Thus any map between instances with same r is as hard as DL in one of them unless it exploits structure of Q beyond group law. Corollary: no non-structural transfer exists; a transfer must be a natural/algebraic construction (B5, B6).
2. Property: uniqueness of homs between prime cyclic groups.
3. Closes the "arbitrary relabeling" class: general bijections/random relabelings of G.
4. Immediate.
5. Cannot invalidate; limits scope of "universal" claims: the hypothesis of HYP-2de84d42 requires representation-specific algorithms (as the mission already states).
6. None needed.
7. Generic-group lower bound: Shoup, "Lower bounds for discrete logarithms and related problems", EUROCRYPT 1997 [unverified recollection]; Nechaev 1994 [unverified recollection]. These apply only to generic algorithms; they do not apply to representation-specific ones such as index calculus.

### B11 — Factor-base-by-definability requirement for prime fields (CONJECTURE; precise open requirement)
1. Open requirement: find, for E/F_p with p prime, a family of subsets V ⊂ E(F_p) with |V| ~ p^{1/m} such that (a) membership is decidable in poly(log p), (b) the relation problem "find v_1..v_m in V with sum v_i = R" can be solved in time p^{o(1)} (not p^{1/2}) heuristically, and (c) each relation is found with probability >= 1/poly. For extension fields F_{q^n} V is an F_q-linear subspace (Weil restriction), so relation finding is a polynomial system of bounded degree in n m variables; summation polynomial S_{m+1} has degree 2^{m-1} in each variable (known). For F_p no such algebraic V exists; V = {x < p^{1/m}} (small integers) gives systems of m*(log p)/m variables with exponential-degree constraints, essentially a subset-sum type problem in a group. 
2. Property: low-degree definability of the factor base.
3. If found, gives Diem-type subexponential on prime fields: all index calculus ideas (Semaev 2004, Petit-Kosters-Messeng 2016) reduce to this.
4. A rigorous lower bound on Gröbner-basis cost of the bit-encoded system (degree-regularity; unproven), or a construction of V.
5. A conjecture-style argument: Any V with polynomial membership and fast relation finding yields a collision-like algorithm contradicting Shoup's generic bound only if the algorithm is generic; non-generic structure (arithmetic of integers in x-coordinates) could in principle be used, so there is no impossibility, just no known construction.
6. Experiment: tiny p (~2^20), V = points with x < p^{1/2}, measure relation-finding time via Gröbner (needs CAS); compare to p^{1/2} and the known small-field results (Petit-Kosters-Messeng report experiments). Not run.
7. Semaev ePrint 2004/031; Petit-Kosters-Messeng PKC 2016; Faugère-Perret-Petit-Renault EUROCRYPT 2012 "Improving the complexity of index calculus algorithms in elliptic curves over binary fields" [all unverified recollection]; Petit-Quisquater ASIACRYPT 2012 (verified).

### B12 — Torus and algebraic-group targets reduce to B1/B5/B6 (ELEMENTARY/KNOWN; impossibility)
1. Targets: algebraic tori T of dimension d over F_q (e.g., Weil restriction/norm-one tori, XTR/CEILIDH torus T_6) have T(F_q) of order Phi_m(q)-type polynomials; hom <P> -> T(F_q) nontrivial iff r | |T(F_q)|; via natural maps (pairings into mu_r in F_{q^k}^* then trace-compressed to the torus T_k) this is the embedding degree k condition and no new transfer arises (the torus is a quotient/subgroup representation of mu_r inside F_{q^k}^*). Additive/unipotent targets need r=p. Non-commutative targets (GL_n(F_ℓ)): homs from cyclic group are just choice of an order-r element: a nonconstant hom exists iff r | |GL_n(F_ℓ)|, but computing it from (E,P) with Galois-equivariance needs Frobenius eigenvalue 1 (B6): E[r] with F-action gives the 2-dim rep itself, but the hom from <P> to a unipotent line in GL_2(F_r) (the Galois action on E[r] when F acts nonsemisimply) is just the abstract group iso — equivalent to B10 and does not give new information.
2. Property: B1, B5, B6.
3. Closes the "torus/other algebraic group" class as a source of new transfers in the algebraic category.
4. Complete case analysis including non-split tori over ext. fields (not done).
5. Possible new targets using non-linear algebraic groups, e.g. abelian varieties other than Jacobians of covers: the image of an isogeny/Hom(E,A) is an abelian variety isogenous to E (E simple); so the target group A(F_q) has #A(F_q) related to #E by isogeny factors: no new structure either (Poincare reducibility), except covering/dimension-increasing A containing E as a factor (B8).
6. Cheap test: verify numerically that for random curves, r | q^k-1 for k<=M only at rare cases (E1 ≈ yes).
7. Rubin-Silververg: "Torus-based cryptography", CRYPTO 2003; CEILIDH Rubin-Silverberg 2003 [unverified recollection].

## 6. Overall conclusion of this analysis (my claim, ELEMENTARY/CONJECTURE mixed)
Within classes of transfers that are (i) group homomorphisms or pairings defined algebraically over the base field, the following are impossible except under arithmetic coincidences: B1, B5, B6, B7, B12. Abstract relabeling is exactly as hard as DLP (B10). Smooth-order targets are excluded (B2). The remaining open directions are (a) non-algebraic transfers such as approximate characters (B9), (b) factor-base definability for prime fields (B11), (c) dimension-raising covers in an intermediate genus regime (B8). None implies a lower bound for the universal quasi-linear algorithm; this is not a proof that no universal algorithm exists. The finite experiments constrain only tiny parameters.

## 7. Proposed Lean 4 / Mathlib lemmas (untested sketches; not compiled in this run)
L1 (hom from prime-order group). For G a group with Nat.card G = r, r prime, f : G →* H: f = 1 or Function.Injective f.
```lean
theorem hom_trivial_or_injective {G H : Type*} [Group G] [Group H] {r : ℕ}
    [hr : Fact r.Prime] (hG : Nat.card G = r) (f : G →* H) :
    f = 1 ∨ Function.Injective f := by
  -- ker f : Subgroup G, card divides r; use Subgroup.card_subgroup_dvd_card and Nat.Prime.eq_one_or_self_of_dvd
  -- ker = ⊥ (injective: MonoidHom.ker_eq_bot_iff) or ker = ⊤ (f = 1: MonoidHom.ker_eq_top_iff / eq_one)
  sorry
```
L2 (nontrivial hom forces r | |H|). Same hypotheses plus [Finite H] and f ≠ 1 gives r ∣ Nat.card H. Sketch: injective => Nat.card G ∣ Nat.card H via f.range : Subgroup H and Subgroup.card_subgroup_dvd_card plus Nat.card_range_of_injective (names to be checked against pinned Mathlib).
L2' (finite fields). For a finite field K and r prime with nontrivial f : Multiplicative (ZMod r) →* Kˣ (or a group G of order r), r ∣ Fintype.card K - 1. Uses Fintype.card_units. Converse (existence of such f when r ∣ |K|-1): from IsCyclic Kˣ and Cauchy: exists_prime_orderOf_dvd_card; cheap but separate lemma.
L5 (Frobenius/equivariance obstruction). For r prime, M a ZMod r-module, f : ZMod r →+ M... simplest form: if x : ZMod r, c : ZMod r, F : M →+ M and f : M →+ N with f (F m) = c • f m and F x0 = x0 then (1 - c) • f x0 = 0, hence f x0 = 0 if c ≠ 1 (field: IsUnit (1-c)). Pure algebra; Lean: `by have := hF x0; ... ; exact (smul_eq_zero.mp ...)`.
L6 (Lean-feasible counting lemma B3, harder): at most M(M+1) primes r > √q... needs Nat.factors and cyclotomic divisibility; medium effort.
Check recommended: L1 and L2 are 20-30 lines; L5 is 5-10 lines.

## 8. Proposed falsification tests
T1 (B3): extend cnt.py to p up to 10^6 with Pollard-rho factoring and larger M; any trace set exceeding M(M+1) falsifies the proof (it cannot; sanity of implementation).
T2 (B3 weighted): compute Hurwitz class numbers and the true curve-fraction with ord_r(q)<=M versus M^2/sqrt q.
T3 (B4): in PARI/Sage, p=11, 13, E with 5 | #E: lift P to Q_p with precision 20 digits; verify the unique lift of order 5 maps to log=0.
T4 (B9): search approximate characters over small prime fields (described above).
T5 (B11): small-prime relation finding timings via Gröbner for factor base x<p^{1/2}, m=2,3.
T6 (B8): small q covers with g=2,3 and index calculus timings vs sqrt(q).

## 9. Ranked recommendation (significance, falsifiability, verification cost; not confidence)
1. B6 + L5: unifies the arithmetic coincidences, formalizable now; high significance for scoping "which transfers can exist". Verification cost low.
2. B1/B2/L1-L2: foundation lemmas; verification cost very low; moderate significance, they rule out smooth targets and field targets except r | Q-1.
3. B3: quantifies sparsity of the MOV-vulnerable family; verification medium (class numbers).
4. B11: highest potential significance (prime-field index calculus), falsification via small experiments, but high verification cost.
5. B9: speculative, cheap test T4, plausible negative result.
6. B8: heuristic gap analysis; needs reading of Enge-Gaudry/GTTD to make rigorous.
7. B4, B5, B7, B10, B12: mostly closing known loopholes; low novelty but good guardrails for the lab.

## 10. Limitations
Only five web lookups, abstract-level; most citations are unverified recollections as marked. No Lean compile, no CAS (so B4/B7/B8/B11 tests unrun). Finite experiments only on p<=80021. Claims B3 (fraction of curves), B8 (regime), B9 (stability) are not proved. Nothing establishes or refutes the universal quasi-linear objective. Model identity is self-reported.
