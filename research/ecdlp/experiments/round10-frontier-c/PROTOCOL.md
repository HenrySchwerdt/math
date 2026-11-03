# Round 10 frontier-C pre-registered protocols (RUN-53c590b6, ECDLP-35)

Written and hashed BEFORE any test script was executed. Python stdlib (+numpy for T2 FFT), toyec.py
reference arithmetic. Seeds fixed. Toy sizes; findings support only the tested domain.

## T1 (candidate C1): lattice (Coppersmith/Howgrave-Graham) decomposition of an m=2 relation
Question: can lattice reduction impose the integer-boundedness x1,x2 < B = p^alpha (the one constraint polynomial
systems over F_p cannot express) so that, given xR, a pair (x1,x2) with S_3(x1,x2,xR)=0 mod p is found in polynomial
time for alpha close to 1/2?  alpha >= 1/2 is REQUIRED for usefulness: for a random R a decomposition into two points
of V_B={x<B} exists only with probability ~ B^2/p; for alpha < 1/2 only planted R in V_B + V_B are decomposable.
Setup: random 61-bit prime p, random (a,b), f(X,Y)=S_3(X,Y,c) in F_p[X,Y] (Semaev S_3 for y^2=x^3+ax+b; first verify
S_3(x1,x2,x(P1+P2))=0 numerically on 20 pairs on a toy curve), monic in X^2Y^2.  Planted root (x1,x2) uniform in [0,B)^2
with c = x(P1+P2) (points exist at those x: resample until both are x-coordinates of points).
Lattice L(D,m): rows x^i y^j f^k p^(m-k), leading monomial x^a y^b, 0<=a,b<=D, k=floor(min(a,b)/2) capped at m,
(i,j)=(a-2k,b-2k), coefficients scaled by B^a B^b.  Exact integer LLL (delta=0.99).
(i) Analytic: Howgrave-Graham feasibility  log_p(det)/n + (small-n slack ignored) < m, giving alpha_HG(D,m);
    report max over D<=40, m<=D/2+1.  (ii) Empirical: for D in {2,3,4,5}, alpha in {0.05,...,0.50 step 0.05},
    5 planted instances each (seed 1): SUCCESS(instance) = at least 2 pairwise non-proportional reduced-basis
    polynomials vanish at the planted root over Z (then the root is recoverable by resultant).
Hypothesis H1: SUCCESS rate >= 0.8 for some alpha >= 0.45 at some (D,m).
Pre-registered kill: H1 false if max analytic alpha_HG < 0.4 and empirical success rate < 0.8 for all alpha >= 0.45.
Sanity/positive control: success must occur for small alpha (0.05-0.10) at D>=3, else the lattice code is wrong.
Negative control: same lattice with the planted root replaced by a random pair must give 0 vanishing vectors.

## T2 (candidate C4): spectral bias of integer-structured (smoothness-type) coordinate predicates
Question: NFS-like integer structure (smoothness, primality, squarefreeness) of coordinates has huge Fourier l1-norm
over F_p characters, so the Kohel-Shparlinski-type bound (unverified recollection) does not exclude correlation with
group characters of E(F_p).  Test: does g(k)=pred(x(kP)) have an exceptional Fourier line over Z/r?
Setup: seed s in {1,2}; prime p in [2^19,2^19+2^14) with random (a,b) of PRIME curve order r != p; P of order r;
sequence k=1..r-1 of x(kP), y(kP) as integers in [0,p).  Predicates: S1 x is p^(1/3)-smooth; S2 x is prime;
S3 x squarefree; S4 y p^(1/3)-smooth; S5 Liouville lambda(x)=(-1)^Omega(x) (x>=1; x=0 -> +1); S6 Jacobi(x/p) control;
S7 x+1 is p^(1/3)-smooth; S8 gcd(x,6)==1.  Controls: C+ g(k)=1[min(k,r-k)<r/4] (must be detected); C- random even sequence.
Statistic T = max_{h=1..(r-1)/2} |DFT(g-mean)(h)|^2 / (r*var).  Null: 200 shuffles of values over the pairs {k,-k}
(preserving evenness x(-Q)=x(Q); this is the symmetry-aware null).  Detection requires T above all 200 null T's AND
p_Bonferroni = 16 tests * (rank-based p) < 0.01 in BOTH seeds at the SAME h-relative-to-P-change?  (h is not comparable
across curves, so require detection per seed independently, report both).
Hypothesis H2: some S1..S5,S7,S8 detected in both seeds.  Kill: none detected while C+ detected and C- not.
