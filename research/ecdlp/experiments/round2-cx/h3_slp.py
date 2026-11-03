"""H3 attack. (1) numeric L0 claims; (2) exact reachable-set sizes of addition-subtraction SLPs in Z
(P=1, the generic/universal case) vs the claimed bound 4^L (L!)^2; (3) 'length <= L' vs 'length = L' gap;
(4) trivial 2^i growth bound. Deterministic, stdlib only."""
from math import factorial, log2
import itertools

def bound(L): return 4**L * factorial(L)**2
def L_lower(r):   # largest L with bound(L) < r  => every Q-covering SLP has length >= L+1
    L = 0
    while bound(L + 1) < r: L += 1
    return L
for b in (256, 521):
    r = 2**b
    L = L_lower(r)
    print(f'r=2^{b}: largest L with 4^L(L!)^2 < r is {L}; so SLP length >= {L+1} for some Q (claimed 29/50).')
    print(f'   log2 r/(2 log2 log2 r) = {b/(2*log2(b)):.2f}; trivial bound (|a_i|<=2^i) gives length >= {b-1}: some Q needs >= log2(r-1)-1 = {log2(r-1)-1:.1f}')

# exact distinct outputs, programs of length exactly L, over Z (P = 1)
def outputs_exact(L):
    """set of last elements a_L over all programs of length exactly L; also union of all intermediate values"""
    outs = set(); allv = set(); progs = 0
    def rec(a):
        nonlocal progs
        i = len(a)
        if i == L + 1:
            progs += 1; outs.add(a[-1]); allv.update(a); return
        seen = set()
        for j in range(i):
            for l in range(i):
                for e1 in (1, -1):
                    for e2 in (1, -1):
                        v = e1*a[j] + e2*a[l]
                        rec(a + [v])
    rec([1])
    return outs, allv, progs
print('\nL | 4^L(L!)^2 | #programs enumerated | distinct a_L (exact length L) | distinct values appearing in any program of length<=L | 2^(L+1)+1 | sum_{i<=L}4^i(i!)^2')
for L in range(0, 5):
    outs, allv, progs = outputs_exact(L)
    S = sum(bound(i) for i in range(L + 1))
    print(L, bound(L), progs, len(outs), len(allv), 2**(L+1)+1, S)
# Z/r coverage: smallest r (prime) such that SOME element of Z/r is not reachable with length<=L
for L in range(1, 5):
    _, allv, _ = outputs_exact(L)
    # all residues mod r covered iff r <= ... check for r up to 2*max
    covered_r = [r for r in range(2, 2**(L+2)+3) if len({v % r for v in allv}) == r]
    print(f'L={L}: largest r for which every residue mod r has an SLP of length<={L}: {max(covered_r)}; claimed-bound threshold 4^L(L!)^2={bound(L)}')
# gap: output of a length-(L-1) program need not be an output of a length-L program (r=anything): L=1
o0,_,_ = outputs_exact(0); o1,_,_ = outputs_exact(1)
print('\nexact length 0 outputs', sorted(o0), ' exact length 1 outputs', sorted(o1), ' => S_0 not subset of S_1 (P itself has no length-1 SLP)')
