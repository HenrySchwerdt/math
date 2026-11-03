"""Mahalanobis-Mallick Problem L reduction (arXiv 1703.07544v3) on toy curves.
Pure python. Rows of M are degree-n' monomials (x,y,1) of the points; left kernel K is l x N."""
import random, itertools, sys, os, json, time
from math import comb, isqrt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from toyec import Curve, is_prime

def monomials(n):
    return [(i, j, n - i - j) for i in range(n + 1) for j in range(n + 1 - i)]

def row(pt, mons, q):
    x, y = pt
    return [pow(x, i, q) * pow(y, j, q) % q for (i, j, k) in mons]

def nullspace_left(M, q):
    """left kernel of N x D matrix M: vectors v (len N) with v M = 0. Returns list of basis vectors."""
    N, D = len(M), len(M[0])
    # row-reduce augmented [M | I]; rows whose M-part becomes zero give kernel vectors
    A = [M[i][:] + [1 if k == i else 0 for k in range(N)] for i in range(N)]
    r = 0
    for c in range(D):
        piv = None
        for i in range(r, N):
            if A[i][c] % q:
                piv = i; break
        if piv is None: continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], -1, q)
        A[r] = [v * inv % q for v in A[r]]
        for i in range(N):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(a - f * b) % q for a, b in zip(A[i], A[r])]
        r += 1
    return [A[i][D:] for i in range(r, N)], r

def rank_mod(M, q):
    return nullspace_left(M, q)[1]

def gen_curve(qlo, qhi, rng, need_prime=True):
    while True:
        q = rng.randrange(qlo, qhi)
        if not is_prime(q) or q < 7: continue
        a, b = rng.randrange(q), rng.randrange(q)
        try: E = Curve(a, b, q)
        except ValueError: continue
        pts = E.points()
        r = len(pts)
        if need_prime and (not is_prime(r) or r == q): continue
        return E, r, pts

def random_instance(E, r, pts, rng):
    while True:
        P = rng.choice(pts)
        if P is not None: break
    m = rng.randrange(1, r)
    return P, E.mul(m, P), m

def kernel_vector_to_dlog(v, I, J, r):
    """v length N=len(I)+len(J), I scalars for rP rows, J scalars for -sQ rows."""
    A = sum(I[i] for i in range(len(I)) if v[i]) % r
    B = sum(J[j] for j in range(len(J)) if v[len(I) + j]) % r
    if B == 0: return None
    return A * pow(B, -1, r) % r
