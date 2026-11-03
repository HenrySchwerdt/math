# Amendment 1 (written after E1/E2/E5 results, BEFORE running e6_carry.py)

Deviations already incurred in E1 (recorded, not hidden): n_null reduced from 150 to 60 (REAL) and 20 (controls)
because a first attempt with 150 nulls exceeded the 280 s timeout and produced no output (killed; no results
observed from it). Min attainable p is therefore 1/61 REAL, 1/21 controls. Seeds 1 and 2 both found p=524309 (first
prime above 2^19 admitting a prime-order curve) with different (a,b).

## E6: three-term carry predicate (inspired by E1 'carries')  [script e6_carry.py]
Algebra: x(Q+P), x(Q-P) are the two roots of a quadratic over F_p whose coefficients are rational in u=x(Q) (standard
x-only addition). The integers x_{k+1}, x_{k-1} in [0,p) satisfy x_{k+1}+x_{k-1} = s(u) + c_k p, where s=(sum mod p) in
[0,p) is computable from u and c_k in {0,1} is a carry bit. c_k = [x_{k+1}+x_{k-1} >= p] is therefore a poly-time
computable predicate of u (via modular sqrt), invisible to degree/Weil arguments for algebraic predicates (it depends on
integer representatives of two conjugate roots). c_k is even in k (c_{r-k}=c_k).
Test: g(k)=c_k for k=2..r-2 (even fold). Statistics: (M) |mean-1/2|*2*sqrt(Neff) z-score with Neff=(r-3)/2;
(T) max normalised periodogram over h=1..(r-1)/2 with the even-shuffle null (200 shuffles, values permuted among
k=2..M with even mirror), as in round10 T2. Seeds 1,2 (same curves as E1/E2). Positive control: overwrite a random
10% of entries of g by 1[cos(2 pi h0 k/r)>0], h0=777 (even in k). Detection: T above all 200 shuffles in both seeds, or
|z_M|>4 in both seeds. KILL: otherwise.
