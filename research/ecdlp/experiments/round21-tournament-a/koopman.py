"""Round 21 A1: Koopman/Prony/DMD test on translation orbits jP. See PROTOCOL.md (hash-registered)."""
import sys, os, json, random, cmath
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'round12-inventor-c'))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from lib12 import find_prime_order_curve

N = 400; L = 200; M = 30; NSH = 30

def orbit(E, P, n):
    xs, ys, R = [], [], P
    for _ in range(n):
        xs.append(R[0]); ys.append(R[1]); R = E.add(R, P)
    return xs, ys

def legendre(a, p):
    if a % p == 0: return 0
    return 1 if pow(a, (p-1)//2, p) == 1 else -1

def norm(s):
    s = np.asarray(s, dtype=complex); s = s - s.mean()
    sd = np.sqrt((abs(s)**2).mean()); return s / sd if sd > 0 else s

def pr_hankel(s):
    H = np.lib.stride_tricks.sliding_window_view(s, N - L + 1)[:L]
    sv = np.linalg.svd(H, compute_uv=False)
    return float((sv**2).sum()**2 / (sv**4).sum())

def nmse_ar(s):
    tr = np.array([s[i:i+M] for i in range(0, 200 - M)]); yt = s[M:200]
    A = tr.conj().T @ tr + 1e-8 * np.eye(M)
    w = np.linalg.solve(A, tr.conj().T @ yt)
    te = np.array([s[i-M:i] for i in range(230, N)]); yy = s[230:N]
    err = yy - te @ w
    return float((abs(err)**2).mean() / (abs(yy)**2).mean())

def peak(s):
    F = np.fft.fft(s, 4 * N); return float((abs(F)**2).max() / N)

def bm(seq, p):
    """Berlekamp-Massey over F_p, returns linear complexity."""
    C, B = [1], [1]; Lc, m, b = 0, 1, 1
    for n in range(len(seq)):
        d = seq[n]
        for i in range(1, Lc + 1): d = (d + C[i] * seq[n - i]) % p
        if d == 0: m += 1; continue
        T = C[:]; coef = d * pow(b, -1, p) % p
        C = C + [0] * (len(B) + m - len(C))
        for i, bi in enumerate(B): C[i + m] = (C[i + m] - coef * bi) % p
        if 2 * Lc <= n: Lc = n + 1 - Lc; B = T; b = d; m = 1
        else: m += 1
    return Lc

def stats(s, rng):
    s = norm(s); pr, nm, pk = pr_hankel(s), nmse_ar(s), peak(s)
    cp, cn, ck = [], [], []
    for _ in range(NSH):
        t = s.copy(); rng.shuffle(t); t = norm(t)
        cp.append(pr_hankel(t)); cn.append(nmse_ar(t)); ck.append(peak(t))
    z = lambda v, c: (v - np.mean(c)) / (np.std(c) + 1e-12)
    return dict(PR=pr, PR_ctrl=float(np.mean(cp)), zPR=z(pr, cp), NMSE=nm, NMSE_ctrl=float(np.mean(cn)),
                peak=pk, zpeak=z(pk, ck))

def planted(rng, K=5):
    f = [rng.random() for _ in range(K)]; ph = [rng.random() for _ in range(K)]
    j = np.arange(N)
    s = sum(np.exp(2j*np.pi*(f[i]*j + ph[i])) for i in range(K))
    nz = 0.1 * (np.random.default_rng(rng.randrange(1<<30)).standard_normal(N) + 1j*np.random.default_rng(rng.randrange(1<<30)).standard_normal(N))
    return s + nz

def main():
    rng = random.Random('round21-A1'); out = []
    for bits in (16, 20, 24):
        for seed in (1, 2, 3):
            E, P, r = find_prime_order_curve(bits, seed); p = E.p
            xs, ys = orbit(E, P, N)
            obs = {
                'O1_e(x/p)': [cmath.exp(2j*cmath.pi*x/p) for x in xs],
                'O2_e(y/p)': [cmath.exp(2j*cmath.pi*y/p) for y in ys],
                'O3_leg(x)': [legendre(x, p) for x in xs],
                'O4_x_mod2': [1 - 2*(x & 1) for x in xs],
                'O5_x/p': [x/p for x in xs],
                'O6_e(x^2/p)': [cmath.exp(2j*cmath.pi*((x*x) % p)/p) for x in xs],
            }
            rec = dict(bits=bits, seed=seed, p=p, r=r, obs={})
            for name, s in obs.items(): rec['obs'][name] = stats(s, rng)
            rec['planted'] = stats(planted(rng), rng)
            rec['BM_x'] = bm(xs, p); rec['BM_y'] = bm(ys, p)
            rr = random.Random(seed * 7 + bits)
            rec['BM_ctrl'] = [bm([rr.randrange(p) for _ in range(N)], p) for _ in range(3)]
            out.append(rec)
            o = rec['obs']
            print(bits, seed, 'BM', rec['BM_x'], rec['BM_y'], rec['BM_ctrl'],
                  'planted PR=%.2f NMSE=%.3f' % (rec['planted']['PR'], rec['planted']['NMSE']),
                  ' | '.join('%s z=%.1f nmse=%.3f' % (k[:2], v['zPR'], v['NMSE']) for k, v in o.items()), flush=True)
    json.dump(out, open(os.path.join(HERE, 'koopman_results.json'), 'w'), indent=1)

main()
