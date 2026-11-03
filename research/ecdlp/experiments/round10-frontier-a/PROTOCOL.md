# Round 10 frontier-A pre-registered protocols (RUN-d97ea396, ECDLP-28)

Written and hashed BEFORE any test script was executed. Python stdlib only, toyec.py reference arithmetic.
Seeds fixed. All toy sizes; findings support only the tested domain.

## T3 (F-A3): complexity of the homomorphic-section digit
Setup: prime p, curve E/F_p of prime order N (N != p, N odd), lift (a,b) to Z/p^2 with fixed random lift.
Homomorphic section s(R) = [p*m]R~ (m = p^-1 mod N), R~ any lift; s is a group homomorphism E(F_p) -> E(Z/p^2).
Define u(R) = ((x(s(R)) - x(R))/p) mod p in F_p (second p-adic digit), likewise v(R) for y.
Sequence u_k = u(kP), k=1..N-1.
Hypothesis H3: u_k (or v_k) has low linear complexity (< 0.4*(N-1)) or satisfies a P-recursive recurrence
(order<=3, polynomial coefficient degree<=3) with coefficients nonzero, verified out-of-window.
Pre-registered kill: H3 false if Berlekamp-Massey L >= 0.45*(N-1) for all tested (p, lift) and no holonomic
relation is found. Sanity checks required first: s(R+S)=s(R)+s(S) on 200 random pairs; points on curve mod p^2;
reduction of s(R) equals R. Positive controls for the detectors: sequence c*k+d (BM L=2), sequence k*g^k mod p
(holonomic order 1 degree 1), must be detected. Negative control: uniform random F_p sequence of same length.
Sizes: p in {1009-ish, 4099-ish, 12007-ish} chosen as first prime >= value with prime curve order, seeds 1,2.

## T1 (F-A1): Freiman-homomorphism / cross-structure test (additive combinatorics)
Sets: X_I = {x(jP): 1<=j<=M}. Count quadruples (a,b,c,d) (ordered pairs a<=b, c<=d, distinct pairs) with
x_a + x_b = x_c + x_d mod p ("A"), x_a*x_b = x_c*x_d ("M"). Among them count those with index relation
a+b=c+d ("I+") resp. a*b=c*d in Z ("I*"), and compare with the expectation for random labelling
(permuting the x-values among indices; 20 permutations as null; z-score on I+ count).
Hypothesis H1: A-type or M-type coincidences concentrate on index-additive (or index-multiplicative) quadruples
(z > 5 against permutation null) i.e. x is an approximate Freiman homomorphism.
Positive controls (detector validity): s_j = c*j mod p (A concentrates on I+), s_j = g^j mod p (M concentrates on I+).
Sizes p ~ 2^20 prime order curve, M = 1500; seeds 1,2.

## T2 (F-A2): random-energy-model landscape test (statistical mechanics)
Energy H_Q(j) = |x(jP) - x(Q)| (cyclic distance mod p) and Hamming distance of x-bits. (i) Autocorrelation of H over
index shifts delta in {1,2,3,4,8,64} (sample all j) normalized; null: 0; reference scale 1/sqrt(N).
(ii) Greedy/annealing on bit-flip landscape over k in [0,N) with budget B evaluations vs. rho-like cost 1.25 sqrt(N)
and random sampling (success rates over 200 random Q). Hypothesis H2: some energy has |corr| > 5/sqrt(N) at small shifts,
or annealing success at budget 3*sqrt(N) exceeds random-sampling success by factor > 3.
