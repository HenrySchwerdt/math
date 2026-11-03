# RUN-b0ccd1bd-6bbc-4f34-b347-0ade0bde13b7 - Round 1 / A sealed submission

Role: discovery. Model (self-reported from system prompt): Sonnet 5.5, model ID claude-sonnet-5-5. Not runtime-verified by the repository.

## Question and inputs

Task TSK-19085a69-6fc1-440f-b7a1-ac2182eea490 (ECDLP-2), target hypothesis HYP-2de84d42-f26b-45c1-ae82-7ffb4a404b61
(universal classical ECDLP in O(n log n) bit operations, n = encoded input length; open, unproved).

Question: do standard coordinate representations of points of E(F_q) (affine/projective Weierstrass over prime and
extension fields, compressed encodings, x-only) expose efficiently computable information not available to a
generic-group algorithm, and could any of it plausibly reduce the cost of ECDLP? Classify each candidate as
(i) known and exploited, (ii) known/provably or empirically useless for DLP, (iii) conjectural/new.

Independence: I read only AGENTS.md, docs/METHODOLOGY.md, docs/roles/discovery.md, my TSK JSON, my RUN files and
HYP-2de84d42. I read no other run or hypothesis file. I did not read docs/LAB_MISSION.md or LAB_PROTOCOL.md in full (instructed file list was narrower).

Framing used throughout. Write G = <P> of prime order n inside E(F_q), Q = [k]P. A generic algorithm sees only
group-operation and equality oracles; Shoup (1997) gives an Omega(sqrt(n)) bound for it. Representation-dependent
information falls into exactly two kinds:

* Kind H (homomorphic): an efficiently computable group homomorphism rho: E(F_q) -> A. Lemma L2 below: if
  gcd(n, |A|) = 1, rho is trivial on G. Kind H is useful for the n-part only if rho restricted to G is injective, i.e.
  n | |A|, AND DLP in A is easier than in G. All known cases are G_a (Smart, Semaev, Rueck) and G_m over F_{q^k} (MOV, Frey-Rueck).
* Kind N (non-homomorphic): a coordinate function f(x(kP), y(kP)) such as a Legendre symbol or a bit. It can only help if
  k -> f([k]P) has structure exploitable without knowing k. Everything I tested and know of says it is pseudorandom.

A third kind, Kind S (symmetry/endomorphism with known action: negation, Frobenius, CM automorphisms), gives only
constant/sqrt(m) factors, because the group of symmetries is small.

## Approach and observed execution

Web sources consulted (11 searches; all retrieved 2026-11-03). Several claims below remain "unverified recollection" where the
searches returned only secondary material.
1. Semaev, "Summation polynomials and the discrete logarithm problem on elliptic curves", ePrint 2004/031 (found via search; ia.cr/2004/031).
2. Semaev, "New algorithm for the discrete logarithm problem on elliptic curves", arXiv 1504.01175 (heuristic 2^{c sqrt(n ln n)} for F_{2^n}; as reported by the search snippet).
3. Diem, "On the discrete logarithm problem in elliptic curves", Compositio Math. 147 (2011) 75-104; and "II", Algebra & Number Theory 7(6) (2013) 1281-1323 (as listed in results).
4. Gaudry, "Index calculus for abelian varieties and the elliptic curve discrete logarithm problem", ePrint 2004/073 (title as found) / J. Symbolic Comput. 44 (2009) (venue: recollection).
5. Joux, Vitse, "Elliptic curve discrete logarithm problem over small degree extension fields" (J. Cryptology 2013; recollection; found only as a reference in search snippets).
6. Galbraith, Gaudry, "Recent progress on the elliptic curve discrete logarithm problem", Des. Codes Cryptogr. 78 (2016), ePrint 2015/1022.
7. Gallant, Lambert, Vanstone, "Faster point multiplication on elliptic curves with efficient endomorphisms", CRYPTO 2001; Galbraith, Lin, Scott, EUROCRYPT 2009 / ePrint 2008/194 (both about scalar multiplication, not DLP).
8. Satoh, Araki, "Fermat quotients and the polynomial time discrete log algorithm for anomalous elliptic curves", Comment. Math. Univ. St. Pauli 47 (1998); Semaev, Math. Comp. 67 (1998); Rueck, "On the discrete logarithm in the divisor class group of curves", Math. Comp. 68 (1999); Smart, J. Cryptology 12 (1999) (Smart: not primary-verified here).
9. arXiv:1702.07107 "The discrete logarithm problem over prime fields: the safe prime case. The Smart attack, non-canonical lifts and logarithmic derivatives" (author list not checked).
10. Menezes, Okamoto, Vanstone, "Reducing elliptic curve logarithms to logarithms in a finite field", STOC 1991 / IEEE Trans. IT 39 (1993); Frey, Rueck, Math. Comp. 62 (1994) 865-874; Shoup, "Lower bounds for discrete logarithms and related problems", EUROCRYPT 1997.
11. Boneh, Shparlinski, "On the unpredictability of bits of the elliptic curve Diffie-Hellman scheme", CRYPTO 2001; Jetchev, Venkatesan, "Bits security of the elliptic curve Diffie-Hellman secret keys", CRYPTO 2008; Bernstein, Hamburg, Krasnova, Lange, "Elligator", ePrint 2013/325 (CCS 2013).
12. Silverman, "The xedni calculus and the elliptic curve discrete logarithm problem", Des. Codes Cryptogr. 20 (2000) 5-40; Jacobson, Koblitz, Silverman, Stein, Teske, "Analysis of the xedni calculus attack", Des. Codes Cryptogr. 20 (2000) 41-64 (found at pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf).
Not retrieved, so labelled "unverified recollection" where used: Wiener-Zuccherato (SAC 1998), Duursma-Gaudry-Morain (ASIACRYPT 1999), Jao-Miller-Venkatesan (ASIACRYPT 2005), Gaudry-Hess-Smart (J. Cryptology 2002), Petit-Quisquater (ASIACRYPT 2012), Petit-Kosters-Messeng (PKC 2016), Biehl-Meyer-Mueller (CRYPTO 2000), Balasubramanian-Koblitz (J. Cryptology 1998), Kohel-Shparlinski (ANTS 2000), Boneh-Venkatesan HNP (CRYPTO 1996), Howgrave-Graham-Smart (DCC 2001), Pohlig-Hellman (IEEE IT 1978), Miller (CRYPTO 1985).

Experiments (Python 3.13, numpy 2.5.3; each < 1 s; code and outputs in
/tmp/claude-0/-home-user-math/1a63ece5-8e90-57cd-878a-b7d0d1d0ee6f/scratchpad/agentA/ : exp1.py/exp1.out, exp2.py/exp2.out, exp2b.py/exp2b.out;
scratchpad files are not committed - the code is reproducible from the descriptions below and can be re-attached by the PI on request).
My first run of exp1 had a bug (numpy bool used as an index gave chi-square exactly 0.0 everywhere) and the first
descent test used a point with chi=+1, making the test vacuous; both were fixed and rerun before any claim below. A control-experiment prediction of mine was also falsified (see E3).

* E1 (Kind N, seeds 1 and 2): random prime-order curves y^2=x^3+ax+b over F_p, p=10771 (a=3439, b=1537, n=10861) and p=11923 (a=585, b=9522, n=12109). With k in 1..(n-1)/2 (one representative per +-k class, since x([k]P)=x([-k]P)): chi-square of chi(x(kP)) and chi(y(kP)) against k mod m for m=2,3,4,5,8; max nontrivial DFT magnitude of chi(x) over k against 30 random +-1 sequences of equal length; lag-1 autocorrelation.
  Observed: chi-square values 0.2-16.8 (df 1..7); curve 2 chi_y vs k mod 8 = 16.75 at df 7 (p about 0.019) and chi_y vs k mod 4 = 10.0 at df 3 (p about 0.019) are the largest; with 20 tests per curve and 40 total, a couple of p ~ 0.02 values is consistent with chance, and the corresponding chi_x values show nothing. Max DFT: 172.1 and 182.3 for chi_x versus baseline ranges [187.2, 227.1] and [199.2, 267.4]; lag-1 autocorrelations -0.0057 and 0.0064 (SD 0.0136, 0.0129). Conclusion: no detectable structure at this size; this supports only "no linear or low-modulus dependence at p ~ 10^4", not pseudorandomness in general. Not corrected for multiple testing.
* E2 (Kind H, 2-descent character, seeds 1,2,3): curves y^2 = x(x^2+Ax+B) over F_p, p = 3307, 4861, 3517, point P with chi(x(P)) = -1 forced. Claim tested: chi(x([k]P)) = chi(x(P))^k for all k with [k]P not in {O, T}. Observed 3416, 2436, 3466 checked multiples, 0 violations. This confirms the homomorphism property exhaustively on those curves (not a proof).
* E3 (Kind H, Smart lift, seed 20261103 and 5): anomalous curve y^2 = x^3+622x+190 over F_761 with #E = 761. Hensel-lift points to Z/p^2, compute psi(P~) = (-x/y)([p]P~)/p mod p, recover k = psi(Q~)/psi(P~). Observed: 20/20 recoveries; with random x-lifts (x + p s) also 20/20 (exp2b). So the lift independence predicted by theory (p*E1 subset E2) holds.
  Negative control (falsified prediction): on a non-anomalous curve (p=397, #E=419 prime) I predicted that the same [#E]P~ construction vanishes for all P. It did NOT: 19 distinct nonzero values over 20 random lifted P. Corrected understanding: the value of the p-adic logarithm of [#E]P~ depends on the arbitrary lift (a lift changes by t in E1, and [N]t has nonzero log), so for non-anomalous curves the map is a function of the lift, not of P; only a canonical lift would make it a homomorphism, and a canonical lift gives N.P^ = O (torsion lifts), hence zero. So the data show only "arbitrary lifts carry no information about k when p does not divide #E" - the control illustrates why, it does not prove it.
No other computation was run. No result of mine is a proof or a formal verification.

## Candidates

Common notation: E/F_q, P of prime order n, Q=[k]P, q = p^m.

### A1. Negation, automorphisms and Frobenius equivalence classes (Kind S) - classification (i)
1. Statement: for P, P' nonzero points, x(P)=x(P') iff P' = +-P (L1). More generally if Aut_{F_q}(E) (order 2, 4 or 6) or Frobenius pi (acting as [lambda] on G with lambda a root of T^2 - tT + q mod n; for E/F_{q0} with q = q0^m, an m-element orbit) acts, one may run Pollard rho on orbits of the group H = <-1, pi, automorphisms>, giving expected cost about sqrt(pi n/(2|H|)) group operations.
2. Property relied on: efficiently computable endomorphisms with known eigenvalue; canonical representatives of orbits (e.g. min x, then y-sign bit).
3. Why it helps: constant (sqrt(|H|)) factor on rho, plus x-only storage.
4. To prove: random-walk analysis with fruitless cycles for orbit walks (known to need extra care).
5. Invalidators: |H| bounded (<= 2m for Frobenius over F_{p^m}, <= 6 for automorphisms) hence never asymptotic; for prime fields only |H| <= 6.
6. Cheapest test: implement rho with and without -1 on a 10^4-size curve and compare step counts (cheap, but only reproduces a known constant).
7. Existing results: Wiener-Zuccherato (SAC 1998), Gallant-Lambert-Vanstone (Math. Comp. 69, 2000, "Improving the parallelized Pollard lambda search on anomalous binary curves"), Duursma-Gaudry-Morain (ASIACRYPT 1999) - all unverified recollection.
Relevance to O(n log n): none, since 2^{n/2}/|H| is still exponential.

### A2. Homomorphic characters from 2-descent and the Tate/Lichtenbaum pairing to small groups (Kind H) - classification (ii) for prime n; (i) as Pohlig-Hellman for composite order
1. Statement: if f(x) = (x-e)g(x) has a rational root e, then delta(P) = (x(P)-e) mod (F_q*)^2 (with the standard conventions at T=(e,0) and O) is a group homomorphism E(F_q) -> F_q*/(F_q*)^2 with kernel containing 2E(F_q). Hence chi(x([k]P)-e) = chi(x(P)-e)^k, depending only on k mod 2 (E2 verifies). General form: the Tate-Lichtenbaum pairing E(F_q)/lE x E[l](F_q) -> F_q*/(F_q*)^l.
2. Property: delta is a homomorphism into a group of order 2 (or l).
3. Why it could help: it computes k mod 2 (resp. mod l) from coordinates alone at cost one Legendre symbol, which a generic algorithm cannot do cheaply (needs the 2-part Pohlig-Hellman, also cheap there though).
4. To prove: standard (descent); Lean-friendly (L2, L3).
5. Invalidators: for n prime and odd, L2 shows rho(G)=1: zero information. It only reveals k modulo divisors of the cofactor.
6. Cheapest test: E2 (done).
7. Existing: Silverman, The Arithmetic of Elliptic Curves, Ch. X (2-descent; textbook knowledge); Pohlig-Hellman 1978 (unverified recollection). Not new.

### A3. Weil and Tate pairings and the embedding degree (Kind H) - classification (i) for small embedding degree, (ii) for generic curves
1. Statement: for n prime, n != p, let k_e be the least k with n | q^k - 1. For a fixed R in E(F_{q^{k_e}})[n] independent of P, the maps e_n(., R) or the reduced Tate pairing t_n(., R) are homomorphisms G -> mu_n subset F_{q^{k_e}}*, injective for suitable R; so DLP in G reduces to DLP in mu_n.
2. Property: bilinearity and nondegeneracy; efficient Miller algorithm; arithmetic of F_{q^{k_e}}.
3. Helps: DLP in F_{q^k}* has subexponential algorithms (number field / function field sieves).
4. Proof obligations: Miller loop correctness (formalization is hard; pairings not in Mathlib to my knowledge).
5. Invalidators: for random curves k_e ~ n (Balasubramanian-Koblitz, unverified recollection), so F_{q^{k_e}} arithmetic costs exponential time. For supersingular curves k_e <= 6 and the attack is poly-time reduction.
6. Cheapest test: enumerate embedding degrees of random prime-order curves with p < 10^4 and tabulate k_e/n (cheap; not run).
7. Existing: MOV 1993; Frey-Rueck 1994; Shoup 1997 (generic hardness); Balasubramanian-Koblitz 1998 (unverified).
Representation point: F_q is represented with its field structure; this is the exact non-generic information used.

### A4. p-adic lifts, formal-group logarithm, Smart/Semaev/Rueck (Kind H) - classification (i) for #E=p and E[p]; (ii) otherwise; (iii) for "partial canonical lifts"
1. Statement (Smart; Satoh-Araki; Semaev): if #E(F_p) = p, choose any lift E~/Z_p and P~, Q~ in E~(Q_p) lifting P, Q. Then psi = -x/y of [p]P~ divided by p, taken mod p, is a homomorphism E(F_p) -> F_p (additive) independent of the lift, injective, so k = psi(Q~)/psi(P~) mod p. Cost O(log^c p) field operations. Semaev/Rueck handle the p-torsion in characteristic p via Artin-Schreier/logarithmic derivative.
2. Property: formal group: E1(Q_p)/E2(Q_p) ~ F_p additive and [p] maps E1 into E2 only up to the log (valuation arithmetic of the formal group).
3. Why it helps: transports DLP into additive group F_p, where it is division.
4. To prove (for generalisation): any ring/representation giving a homomorphism from a large cyclic subgroup of E(F_q) into a group with easy DLP.
5. Invalidators: for n != p, torsion lifts to torsion (Hensel) and the formal logarithm kills torsion; arbitrary lifts give lift-dependent values (E3 control). The arXiv 1702.07107 note studies non-canonical lifts for DLP in F_p* with the analogous conclusion (as stated in its title).
6. Cheapest test: E3 (done: 20/20 on p=761; control shows lift-dependence). A harder experiment: vary lift type on curves with #E=p*c, c small, and measure k mod p recovery.
7. Existing: Smart 1999, Satoh-Araki 1998, Semaev 1998, Rueck 1999. Conjectural (iii) extension: "curves with #E = p*c or with large p-part in E(F_{p^m})" - known only for the p-part, which Pohlig-Hellman style isolates, so no new gain.

### A5. Summation polynomials and decomposition over factor bases (Kind N/relations) - classification (i) for E(F_{q^m}) with small m>1; (iii)/(open) for prime fields
1. Statement: Semaev's polynomial S_{r+1}(X_1..X_{r+1}) vanishes iff there exist points with those x-coordinates summing to O; set F = {points with x in a subspace V of F_{q^m} of dimension about m/r over F_q}; a relation R = [a]P + [b]Q is found by solving S_{r+1}(x(R), x_1..x_r)=0 with x_i in V via Weil restriction / Grobner basis, giving subexponential or q^{2-2/m} DLP over E(F_{q^m}) (Gaudry 2009, Diem 2011).
2. Property: x-coordinates are an F_q-vector space; sums of points have rational-function coordinate relations; "smoothness" := x in V.
3. Helps: replaces rho's sqrt(q^m) by roughly q^{2-2/m} (m fixed); for m = 2 no gain over rho, m = 3: q^{4/3} vs q^{1.5}; m >= 4 gains.
4. Prove: probability that a random point is a sum of r factor-base points (about 1/r! heuristic), and complexity of the Grobner basis system (degree fall conjectural; Galbraith-Gaudry survey).
5. Invalidators: for prime fields no natural factor base with nonvanishing probability and cheap relation search (the polynomial system has no structure; Petit-Kosters-Messeng and Semaev 2015 give only heuristic bounds that remain exponential; see the search snippet: the prime-field variant is "still exponential"). Miller's 1985 heights-based argument (unverified recollection) says the naive analogy to smoothness fails.
6. Cheapest test: relation-yield experiment for m=2 and m=3 with q ~ 100 using brute-force enumeration; not run.
7. Existing: Semaev 2004 (ePrint 2004/031); Gaudry 2009; Diem 2011 and 2013 (ANT 7); Joux-Vitse 2013; Galbraith-Gaudry 2016 survey; Semaev arXiv:1504.01175 (binary fields, heuristic 2^{c sqrt(n ln n)}).
Within the project target: all of these are exponential in n = log q^m unless m grows with q, and only for restricted families; none generic.

### A6. Non-homomorphic coordinate functions: Legendre symbols, parity/bit predicates, correlations with k (Kind N) - classification (ii)
1. Statement (tested, empirical): for random (a,b) with prime n, the sequences chi(x([k]P)), chi(y([k]P)) for k = 1..(n-1)/2 have no detectable dependence on k mod m (m <= 8), no large DFT peak, no lag-1 autocorrelation beyond sqrt(1/K) (E1).
2. Property: character-sum (Weil-type) bounds for sums over cyclic subgroups of size n of rational-function characters (Kohel-Shparlinski, ANTS 2000, unverified recollection; Weil bounds apply to the whole group and to subgroups of size > q^{1/2+eps}).
3. Helps? Only if the sequence were predictable from k; the opposite statement is the hard-core-bit results: Boneh-Shparlinski 2001 and Jetchev-Venkatesan 2008 show bits of the ECDH secret x([ab]P) are as hard as the whole secret, i.e. no bit predictor exists unless ECDH is broken. That is the converse direction, so an accepted statistical bias would be new information.
4. To prove: nothing established beyond the cited reductions; nonexistence of bias cannot be proved empirically.
5. Invalidators: any statistically significant bias on cryptographically sized curves; E1 is a single tested domain (p ~ 10^4, 2 curves).
6. Cheapest test: E1 extended across 200 curves with multiple-testing correction (not run).
7. Existing: the above plus Elligator (Bernstein-Hamburg-Krasnova-Lange 2013) showing representation-level encoding tricks (injective map from strings to half the points), a representation-privacy result, not a DLP one.
Also Hidden Number Problem lattice attacks (Boneh-Venkatesan 1996; Howgrave-Graham-Smart 2001, both unverified recollection) are (i) but require side-channel nonce leakage and are not DLP algorithms.

### A7. Compressed encodings and x-only/Kummer arithmetic (Kinds N and S) - classification (ii) with (i) for twist/invalid-curve implementation attacks
1. Statement: (x, sign bit) determines the point; x alone determines +-P; the Montgomery ladder computes x([k]P) from x(P) using differential addition x(P+Q) from x(P), x(Q), x(P-Q). The x-only structure is a pseudo-group on the Kummer line: the DLP "given x(P), x(Q) find k with x(Q)=x([k]P)" has solutions +-k, so one needs n odd for a unique representative in 1..(n-1)/2 (parity of k is not even well-defined on the ratio, since k and n-k have different parity when n is odd).
2. Property: Kummer variety quotient E/<-1> = P^1.
3. Helps: storage and constant factor only (A1).
4. To prove: L1. Trivial.
5. Invalidators: none; the information is exactly "k up to sign". Generic lower bound in a pseudo-group with differential-addition oracle should be the same up to constants (conjecture, unverified).
6. Test: check that parity of k vs x is independent (E1 shows chi-square df 1 values 0.29, 0.35).
7. Existing: invalid-curve attacks from x-only inputs that lie on the quadratic twist (Biehl-Meyer-Mueller CRYPTO 2000, unverified recollection) exploit that a bare x lies on E or its twist E^t with possibly smooth order; this is an implementation vulnerability, not an ECDLP speedup.

### A8. Division polynomials and rational-function relations x([k]P) = phi_k/psi_k^2 (Kind N/algebraic) - classification (ii)/(iii)
1. Statement: x([k]P) = x(P) - psi_{k-1}(P) psi_{k+1}(P)/psi_k(P)^2 with deg psi_k^2 = k^2 - 1 in x; DLP is the problem of finding k from (x(P), x(Q)) with x(Q) = that expression: solving a univariate polynomial equation of degree about n^2 over F_q in the unknown k, not in x.
2. Property: k enters as the degree, not as a variable (non-algebraic exponent).
3. Helps?: Schoof's algorithm uses psi_l for ell small to obtain the Frobenius trace; for DLP one has exponent in the degree so no polynomial system captures it. Using the minimal polynomial of Frobenius, pi^2 - t pi + q = 0, gives P-relations among x(P), x(pi P), ..., for a P over F_{q^m}; it only gives eigenvalue data (A1).
4. Prove: lower bound on arithmetic degree of the relation (n^2).
5. Invalidators: any compact representation (e.g. straight-line program of length poly(log n) for psi_k, which is the double-and-add chain itself: that is how evaluation works but gives no inversion).
6. Test: none cheap.
7. Existing: standard (Schoof 1985; Washington, Elliptic Curves: Number Theory and Cryptography, Ch. 3) - textbook; no known DLP use.

### A9. Weil descent and GHS for composite extension fields (Kind H-like, transfers to Jacobians of higher-genus curves) - classification (i)
1. Statement: for E over F_{q^m}, Weil restriction to an m-dimensional abelian variety over F_q; GHS constructs a curve C/F_q of genus g with a homomorphism E(F_{q^m}) -> Jac_C(F_q) (conorm / covering), and index calculus on Jac_C has complexity L_{q^g}[1/2] style when g small.
2. Property: the field-tower structure of the coordinate field (F_{2^{ln}}, etc.).
3. Helps for specific composite extension degrees.
4. Prove: genus bound computing.
5. Invalidators: genus large for most curves; no effect for prime fields.
6. Test: none cheap.
7. Existing: Gaudry-Hess-Smart 2002 (unverified recollection); Galbraith-Hess-Smart (unverified); Gaudry 2009 and Diem 2011 for the abelian-variety versions.

### A10. Isogeny-class structure and random self-reduction (Kind H, between curves) - classification (ii) as an equivalence, (iii) as "weak-curve hopping"
1. Statement: if phi: E -> E' is an F_q-isogeny of degree d coprime to n, then phi restricted to G is injective and DLP on G transfers to DLP on phi(G) at cost of d-isogeny evaluation (known); all curves in an isogeny class have the same order and, under heuristic, an isogeny walk to a curve with weak property (small embedding degree, anomalous, larger Aut) is a possible reduction.
2. Property: isogenies preserve group structure (homomorphism) and are computable from kernel (Velu).
3. Helps: if the class contains a weak member reachable in poly(log q) steps, then ECDLP on all members falls.
4. Prove: for ordinary classes the isogeny graph structure (class group action, expander property: Jao-Miller-Venkatesan 2005, unverified recollection, proving random-self-reducibility under GRH for ordinary curves with sufficient walk length), so any weakness must have non-negligible density across the class for reductions to be non-trivial.
5. Invalidators: weak curves are exponentially rare in each class (embedding degree <= 6 with n large: negligible; anomalous: #E=p one specific order, preserved only if the whole class has order p). A class has constant order, so anomalous or small-embedding-degree is a class invariant, not something a walk can create (order is class invariant; embedding degree depends on n | q^k - 1 and n | #E, both class invariants, thus the embedding degree is class-invariant for each prime n!). Hence A3, A4 weakness is class-wide and nothing is gained. Only properties that vary within the class (endomorphism ring conductor, |Aut|, existence of an efficient endomorphism of small degree, Weil-descent genus, field of definition of the kernel) can be improved.
6. Cheapest test: for 10^3 random curves p < 10^4 compute #E, embedding degree: confirm class-invariance trivial; for varying property compute conductor of End across a class (needs isogeny volcano code; moderate cost).
7. Existing: Jao-Miller-Venkatesan 2005; Galbraith 1999 (isogenies, LMS JCM); Galbraith-Hess-Smart (Extending the GHS Weil descent attack, EUROCRYPT 2002) - all unverified recollection.
Speculation (iii): the only intra-class varying weaknesses are endomorphism-ring related (GLV-type speedups, larger conductor, small-degree endomorphisms), all of which give constant factors.

### A11. Canonical lifts, global points, heights and relation lattices (xedni) - classification (ii)
1. Statement: choose lifts of P, Q (and auxiliary points) to E~(Q) such that the lifted points become linearly dependent in E~(Q) (rank drop), producing a relation a P~ + b Q~ + ... = O whose reduction gives k. Silverman's xedni calculus.
2. Property: reduction E~(Q) -> E(F_p) is a homomorphism from a finitely generated group of controllable rank; Neron-Tate height is a quadratic form.
3. Helps: a relation in characteristic 0 implies relation in char p.
4. Prove: existence of liftings with vanishing rank at a rate better than p^{-c}.
5. Invalidators: Jacobson-Koblitz-Silverman-Stein-Teske prove (as summarised in the search result) that asymptotically the algorithm is virtually certain to fail due to height/coefficient bound, and experiments show the odds are prohibitive.
6. Test: not needed; replicate small case only if a variant bypasses the height bound (nothing known).
7. Existing: Silverman 2000; JKSST 2000.

### A12. Conjectural classification of "algebraic" injective homomorphisms (speculation) - classification (iii), labelled SPECULATION
1. Statement: Conjecture S1: let phi be an F_q-algebraic group (or abelian-variety-quotient or isogeny-composed) homomorphism from E[n](F_q) into some group scheme B(F_q') with B among G_a, tori, abelian varieties. Then phi factors through the Weil/Tate/Frobenius-logarithm homomorphisms of A3, A4 up to isogeny, so the list of efficiently computable injective reductions is exhausted by (G_a: Smart/Semaev/Rueck; G_m: MOV/FR; abelian varieties with an index calculus: GHS/Weil descent). Informal analogy only; no source.
2. Property: Tate-conjecture/Faltings-type classification of homomorphisms between algebraic groups over finite fields, Hom(E, B) = Z-module generated by isogenies.
3. Helps: would convert the vague "no representation-specific attack exists" into a precise theorem about reductions of this type; it is a negative statement.
4. To prove: very hard; maybe false because "efficiently computable homomorphism from G" need not come from an algebraic morphism.
5. Invalidator: counterexample homomorphism computable with non-algebraic (e.g. integer lattice/pairing in Q-vector spaces) means.
6. Cheapest test: none; a restricted version (n-torsion homomorphisms to F_{q^k}* from Hom-module of Galois-equivariant maps) is within A3.
7. Existing: no source; the Tate theorem on homomorphisms of abelian varieties over finite fields (Tate 1966, "Endomorphisms of abelian varieties over finite fields", Invent. Math. 2; recollection) is the classical result it would lean on.

## Proposed Lean lemmas

L1 (negation/x-fibre; Mathlib-oriented). For a field K and a Weierstrass curve W (WeierstrassCurve.Affine), for nonzero points P, Q: x(P) = x(Q) implies Q = P or Q = -P; and x(-P) = x(P).
Sketch (unverified against Mathlib source; exact names not checked since Mathlib is not in this checkout):
```lean
theorem x_eq_iff_eq_or_neg {K} [Field K] (W : WeierstrassCurve.Affine K)
  {x y1 y2 : K} (h1 : W.Equation x y1) (h2 : W.Equation x y2) :
  y1 = y2 ∨ y1 = W.negY x y2
```
Mathlib has a lemma of this shape (I recall `WeierstrassCurve.Affine.Y_eq_of_X_eq`; unverified). Then lift to Points via `Point.some` and `Point.neg`.

L2 (homomorphism to a coprime group is trivial on a cyclic subgroup; pure group theory).
Statement: for a group G, an element g of finite order d, a finite group H with gcd(d, |H|) = 1, and a monoid hom f: G -> H, f(g) = 1. Equivalently: f(g)^d = 1 and f(g)^{|H|} = 1, so orderOf (f g) divides gcd = 1.
```lean
theorem hom_trivial_of_coprime {G H : Type*} [Group G] [Group H] [Finite H]
  (f : G →* H) (g : G) (h : Nat.Coprime (orderOf g) (Nat.card H)) : f g = 1 := by
  have h1 : orderOf (f g) ∣ orderOf g := orderOf_map_dvd f g
  have h2 : orderOf (f g) ∣ Nat.card H := orderOf_dvd_natCard (f g)
  have : orderOf (f g) = 1 := Nat.eq_one_of_dvd_coprimes h h1 h2  -- or Nat.Coprime.eq_one_of_dvd
  exact orderOf_eq_one_iff.mp this
```
(names `orderOf_map_dvd`, `orderOf_dvd_natCard`, `orderOf_eq_one_iff` exist in Mathlib as far as I recall; not compiled here.) Consequence recorded as a corollary: any character chi: E(F_q) -> {+-1} is trivial on a subgroup of odd order, so the 2-descent character carries no information about k for odd prime n (A2).
L3 (stretch): the map delta in A2 is a homomorphism; follows from the factorisation formula for the line through P, Q and the chord identity (x_1-e)(x_2-e)(x_3-e) a square for P+Q+R=O collinear. Needs the explicit group law over a field with Mathlib's `WeierstrassCurve.Affine.Point.add` and is a non-trivial but finite algebraic computation.
Formal correctness of L1-L2 is Lean-only; none of this addresses bit complexity.

## Proposed falsification tests (all Python, p < 10^5, seconds)
T1 (A6, run as E1 on 2 curves): sequence statistics of chi(x([k]P)), chi(y([k]P)), parity, lag-1 correlation; extend to 200 random prime-order curves with Bonferroni correction. Falsifies "Kind N coordinate functions have k-dependent bias" if no test exceeds the corrected threshold.
T2 (A2, run as E2): verify chi(x-e) character is a homomorphism: falsified by any violation (none in about 9300 checks).
T3 (A4, run as E3): Smart recovery on #E = p curves, and test with non-anomalous curves as lift-dependence control; falsifies "arbitrary lifts give DLP information when p does not divide #E" in the sense that values must be uniform and independent of k. A stronger control (not run): compute values for P and [j]P with the same lift family and test for linearity in j mod p; linearity would be a counterexample to A4's invalidator.
T4 (A10, not run): over 10^3 curves, verify embedding degree class-invariance across isogenous curves (should always hold; a violation would indicate a bug).
T5 (A7, not run): count steps of rho with +- equivalence versus without; expect factor about sqrt(2).

## Ranked recommendation (by significance, falsifiability, verification cost)
1. A12/A3/A4 together as a "classification of injective computable homomorphisms from E[n] to easy-DLP groups" (significance high; falsifiability moderate; cost: literature + algebra; Lean cost moderate for L2, high for pairings). Provides a precise form for "generic bounds do not cover representation-specific algorithms".
2. A6 extended (statistical test, large-scale): low cost, directly falsifiable, but low prior for success; also needs an agreed multiple-testing protocol.
3. A5 for m = 2, 3 and prime fields: relation-yield experiments; significance high if some factor-base notion for prime fields works; verification cost medium; prior low.
4. A10 intra-class varying properties (endomorphism ring, conductor): medium significance, medium cost.
5. L1 and L2 Lean lemmas: low significance, very low cost, definite value for the formal framework.
6. A1, A7, A2, A8, A9, A11 are recorded for completeness (known or negative).

## Limitations
* Only 11 web lookups; several citations are marked unverified recollection and must be checked before use. No source text was read beyond search summaries.
* Experiments are tiny (p ~ 10^3-10^4, 2-3 curves); they test only their domains and do not show pseudorandomness at cryptographic size.
* The first exp1 run was buggy and was corrected before reporting; one pre-registered prediction (control in E3) was falsified and reinterpreted afterwards (the reinterpretation is a hypothesis consistent with the data, not a derived theorem).
* Lean sketches were not compiled; Mathlib lemma names are recollections.
* The speculative conjecture A12 has no source and may be false.
* Nothing here changes the proof status of HYP-2de84d42; classification (i)/(ii) are not claims about O(n log n) feasibility. For the stated target (bit complexity in log q), every known representation-dependent technique remains exponential in n for generic prime-field curves.
* Independence caveat: I did not read sibling runs by instruction; any overlap is accidental.
