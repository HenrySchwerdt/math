# Round 6 / ECDLP-16 pre-registered protocol (RUN-6cc3ff88-5ba0-4f61-b733-be953a11876b)

Written BEFORE running round6.py (code drafted, not executed). Owner: algorithm-engineering agent (Sonnet 5.5, self-reported).
Toy sizes only; counted field operations, not timings; no asymptotic claim from experiment.

QUESTION: at m=3, does any decomposition-finding method have per-relation cost T (counted field mults) < p^{1/6}
on toy prime-field curves, for a factor base V of size ~p^{1/3}?

## Cost model (fixed in advance)
Unit = field multiplication (squaring = 1). Inversion I charged w_I=1 mult (headline) and w_I=10 (sensitivity); additions free.
x-only paired addition (computes x(P+Q) and x(P-Q) sharing one inversion): 1 I + 4 M. x-only doubling: 1 I + 3 M.
Hash lookups free (favours the table methods; stated). Baseline rho = sqrt(pi*N/2) affine additions of (1 I + 3 M) each
(analytic expectation, not measured). Linear algebra (sparse, 3 nonzeros/row, Wiedemann-style) charged 3*|V|^2 mults
(model; no actual elimination counted except in the end-to-end check). Total = table build + (|V|+10)*T + LA.

## Step 1 correctness oracle (before everything)
Semaev S_3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2((x1+x2)(x1x2+a)+2b) x3 + ((x1x2-a)^2-4b(x1+x2)).
S_4(x1..x4) = Res_X(S_3(x1,x2,X), S_3(x3,x4,X)) via the closed 2x2-quadratic resultant
(A2B0-A0B2)^2-(A2B1-A1B2)(A1B0-A0B1). Checks, using toyec.Curve as oracle, seed 20261108:
 (i) >= 2000 random 3-tuples: S_3(x(P1),x(P2),x(P1+P2))==0 (P1,P2 random affine, sum != O);
 (ii) >= 2000 random 4-tuples P1..P3 random, P4=-(P1+P2+P3) != O: S_4(x1,x2,x3,x4)==0, across p in {4001,15791,65537,1000003};
 (iii) completeness at p=4001: for 300 tuples, the set of x4 in F_p with S_4(x1,x2,x3,x4)==0 equals {x(+-P1+-P2+-P3)} exactly
      (generic case: the 4 sign classes), up to degenerate coincidences, which are counted and reported;
 (iv) negative control: 2000 random x4 not in that set give S_4 != 0.
Any failure aborts the experiment.

## Step 2 factor bases (per prime p, per curve; n = number of x-values, |V|=2n signed points, V negation-closed)
 Primes: for k in {12,14,16,18,20}, deterministic search in [2^k, 1.03*2^k]: p prime, p-1 with largest prime factor <= 97,
 minimising |log(hA/p^{1/3})|+|log(hB/(2p^{1/3}))| over divisors hA,hB of p-1.
 PKM-A: V_x = {x in g*H : x^3+ax+b nonzero square}, H order hA ~ p^{1/3}, g uniform in F_p^*  (n ~ hA/2).
 PKM-B: same with hB ~ 2p^{1/3}                                                            (n ~ p^{1/3}).
 SX-A/B: n smallest x-values with a curve point, n = |PKM-A/B V_x| (equal size).
 RND-A/B: n uniformly random x-values with points (equal-size control).
 Curves: 4 random nonsingular (a,b) per p for k=12..18; 2 for k=20 (B-sets only, M1 only). random.Random(f"20261108-{tag}").

## Step 3 methods
 M1 (table): hash of x(P1+-P2) over all pairs (incl. doubling and P-P=INF), built once per V; per attempt for each x3 in V_x
   compute x(R+-P3) (paired, 1I+4M) and look up; early exit on hit. Cost per attempt measured; table build counted.
   Verified: hit iff R in {P1+P2+P3} (exact enumeration), and decomposition reconstructed and checked with the group law.
 M2 (S_4 pair-scan with univariate root test): for every unordered pair (x1<=x2) in V_x form q(x3)=S_4(x1,x2,x3,x(R)) (quartic),
   and test for a root in V: (a) evaluation of q at all n x3 (Horner, 4 M each) [SX and PKM]; (b) PKM only: gcd(q, X^h - g^h)
   after X^h mod q by square-and-multiply (all poly mults, inversions counted). Implemented with explicit counted polynomial
   arithmetic; run only at k=12,14 (cost per attempt measured, 40 R per curve, 2 curves) and its agreement with M1 verified
   (spurious formal-resultant zeros counted separately and checked against the group law).
 M3 (smarter elimination): analytic only. Eliminating x3 and x2 from S_4(x1,.,.,x(R)) with the membership equations
   x_i^h = g^h gives univariate degree ~16h^2 (x1 loop) or per-x1 degree ~4h in x2; the final gcd/root test has cost >= degree.
   Lower bounds are stated, not measured (no CAS / Groebner available: sympy absent). Also stated analytically: partial table /
   sub-sampling P3 gives T unchanged (cost and pi both scale with k/n), and the meet-in-the-middle family has total >= |V|^2.
 NOTE (correction to task text): for a FIXED low-degree polynomial q (deg 4), X^h mod q by powering costs O(deg^2 log h), not O(h*deg);
 the O(h) bound applies only after eliminating variables so that the univariate has degree Theta(h) or more.

## Step 4 measurements
 Exact pi = |{P1+P2+P3 : Pi in V}| / #E(F_p) by full enumeration of sums (all curves, all sets). Mean per-attempt cost of M1 on 200 random
 R per set (M1 hit must agree with exact membership for all samples). T = (mean cost per attempt)/pi. Total cost vs sqrt(p), and ratio
 vs rho baseline; T vs p^{1/6}. Log-log fits of T and of total vs p over k=12..18 (per set, curve-mean). Extra (M1 only,
 SX, p~2^16, 2 curves): |V| sweep n = c*p^{1/3}, c in {0.5,0.75,1,1.5,2} for best total.
## Step 5 decision rule
 "T < p^{1/6} achieved" iff some method has T < p^{1/6} at every k>=14 AND fitted exponent of T in p is < 1/6.
 Otherwise report best fitted exponent and structural reason. Secondary observation (analytic): LA 3|V|^2 = p^{2/3} > sqrt(p)
 for |V|=p^{1/3}, so total < sqrt(p) is impossible in this cost model even with T=O(1) (reported, not a measurement).
## Step 6 end-to-end
 Smallest prime (k=12), prime-order curve (search), best-total configuration: generate relations R=uP+vQ with M1, solve the linear system
 mod N (dense Gaussian elimination, n+1 unknowns), recover k, verify with dlog_bsgs and by Q==kP; report relation count and counted ops.
Runtime: each invocation < 5 minutes; reduce curves and say so if exceeded.
