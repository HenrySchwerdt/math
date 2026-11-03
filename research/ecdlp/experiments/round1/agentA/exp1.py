#!/usr/bin/env python3
"""EXP1: non-homomorphic coordinate functions vs k, and the 2-descent homomorphism.
Seeds fixed. Pure Python + numpy. Run: python3 exp1.py"""
import random, math
import numpy as np

def is_prime(n):
    if n < 2: return False
    i = 2
    while i*i <= n:
        if n % i == 0: return False
        i += 1
    return True

def leg(a, p):
    a %= p
    if a == 0: return 0
    return 1 if pow(a, (p-1)//2, p) == 1 else -1

def count_points(a, b, p):
    # table of Legendre symbols
    sq = [0]*p
    for y in range(p): sq[y*y % p] += 1
    return 1 + sum(sq[(x**3 + a*x + b) % p] for x in range(p))

def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q: l = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else: l = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (l*l - x1 - x2) % p
    return (x3, (l*(x1 - x3) - y1) % p)

def sqrt_mod(n, p):
    n %= p
    if n == 0: return 0
    if leg(n, p) != 1: return None
    for y in range(p):  # p small
        if y*y % p == n: return y

def find_point(a, b, p, rng):
    while True:
        x = rng.randrange(p)
        y = sqrt_mod(x**3 + a*x + b, p)
        if y is not None: return (x, y)

def chi_square_uniform(counts):
    n = sum(counts); e = n/len(counts)
    return sum((c-e)**2/e for c in counts)

def test_nonhom(seed):
    rng = random.Random(seed)
    while True:
        p = rng.choice([q for q in range(9000, 12000) if is_prime(q)])
        a, b = rng.randrange(p), rng.randrange(p)
        if (4*a**3 + 27*b*b) % p == 0: continue
        n = count_points(a, b, p)
        if is_prime(n) and n != p: break
    P = find_point(a, b, p, rng)
    pts = [None, P]
    for k in range(2, (n-1)//2 + 1): pts.append(add(pts[-1], P, a, p))
    K = len(pts) - 1  # k = 1..(n-1)/2, one per +-k class
    chi_x = np.array([leg(pts[k][0], p) for k in range(1, K+1)])
    chi_y = np.array([leg(pts[k][1], p) for k in range(1, K+1)])
    out = {"p": p, "a": a, "b": b, "n": n, "K": K}
    # contingency vs k mod m for several m (k in 1..(n-1)/2 representative)
    for name, arr in (("chi_x", chi_x), ("chi_y", chi_y)):
        for m in (2, 3, 4, 5, 8):
            tab = np.zeros((m, 2))
            for k in range(1, K+1): tab[k % m, int(arr[k-1] > 0)] += 1
            rows = tab.sum(1); cols = tab.sum(0); N = tab.sum()
            chi2 = ((tab - np.outer(rows, cols)/N)**2 / (np.outer(rows, cols)/N)).sum()
            out[f"{name}_vs_k_mod_{m}_chi2(df={m-1})"] = round(float(chi2), 2)
    # max nontrivial DFT magnitude of chi_x vs random +-1 baselines of same length
    def maxdft(s): return float(np.abs(np.fft.rfft(s - s.mean())[1:]).max())
    out["maxDFT_chi_x"] = round(maxdft(chi_x.astype(float)), 1)
    out["maxDFT_chi_y"] = round(maxdft(chi_y.astype(float)), 1)
    base = [maxdft(np.array([rng.choice((-1., 1.)) for _ in range(K)])) for _ in range(30)]
    out["maxDFT_random_baseline_min/mean/max"] = [round(min(base), 1), round(sum(base)/30, 1), round(max(base), 1)]
    # lag-1 autocorrelation
    out["lag1_autocorr_chi_x"] = round(float(np.mean(chi_x[:-1]*chi_x[1:])), 4)
    out["lag1_autocorr_expected_sd"] = round(1/math.sqrt(K), 4)
    out["mean_chi_x"] = round(float(chi_x.mean()), 4)
    out["mean_chi_y"] = round(float(chi_y.mean()), 4)
    return out

def test_descent(seed):
    """Curve with rational 2-torsion T=(e,0): f(x)=(x-e)(x^2+ex+c). Check
    chi(x([k]P)-e) == chi(x(P)-e)^k for all k with [k]P not in {O,T}  (homomorphism E->F_p*/sq)."""
    rng = random.Random(seed)
    while True:
        p = rng.choice([q for q in range(3000, 5000) if is_prime(q)])
        e, c = rng.randrange(1, p), rng.randrange(1, p)
        # y^2 = (x-e)(x^2+e x+c) = x^3 + (c - e^2)... expand with shift: use general cubic -> convert by x-> x+e/3? avoid:
        # use y^2 = x(x^2+Ax+B) with T=(0,0), e=0 (WLOG by translation)
        A, B = rng.randrange(p), rng.randrange(1, p)
        if (A*A - 4*B) % p == 0: continue
        break
    f = lambda x: (x*(x*x + A*x + B)) % p
    # a2 != 0 model: group law formulas with a2=A: use generic addition for y^2=x^3+Ax^2+Bx
    def addg(P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0: return None
        if P == Q: l = (3*x1*x1 + 2*A*x1 + B) * pow(2*y1, -1, p) % p
        else: l = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (l*l - A - x1 - x2) % p
        return (x3, (l*(x1 - x3) - y1) % p)
    while True:
        x = rng.randrange(1, p); y = sqrt_mod(f(x), p)
        if y is not None and y != 0 and leg(x, p) == -1: P = (x, y); break  # force chi(x(P)) = -1
    chiP = leg(P[0], p)
    R = None; checked = viol = 0; odd_even = {}
    for k in range(1, 4*p):
        R = addg(R, P)
        if R is None: break
        if R[1] == 0: continue  # R = T
        checked += 1
        pred = 1 if chiP == 1 else (-1 if k % 2 == 1 else 1)
        if leg(R[0], p) != pred: viol += 1
    return {"p": p, "A": A, "B": B, "chi(x(P))": chiP, "checked": checked, "violations": viol}

if __name__ == "__main__":
    for s in (1, 2):
        print("NONHOM seed", s, test_nonhom(s))
    for s in (1, 2, 3):
        print("DESCENT seed", s, test_descent(s))
