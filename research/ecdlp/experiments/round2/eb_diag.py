"""POST-HOC diagnostic (not pre-registered) for the E-B spectral-flatness anomaly of Legendre predicates.
For 40 curves (seed 20261104 curve indices 0..39) compute the variance of the normalised periodogram ordinates
(Exp(1) null => 1) for several predicates of [k]P, k=1..h, and the same quantity for hash-based pseudo-random predicates
of the same x-values (control for 'fixed population' effects)."""
import sys, os, json, random, hashlib, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
import eb
eb.SEED = 20261104


def powvar(bits):
    s = 2.0 * bits - 1; s = s - s.mean(); N = len(s)
    S = np.fft.rfft(s); pw = np.abs(S[1:(N - 1) // 2 + 1]) ** 2 / (N * (s * s).mean())
    return float(pw.var())


def lag1sd(bits):
    s = 2.0 * bits - 1; s = s - s.mean(); N = len(s)
    return float((s[:-1] * s[1:]).sum() / (s * s).sum() * math.sqrt(N))


res = {}
for ci in range(40):
    rng = random.Random(f'{eb.SEED}-{ci}')
    E, r, P = eb.gen_curve(rng); p = E.p; h = (r - 1) // 2
    pts = eb.half_sequence(E, P, h)
    X = np.array([q[0] for q in pts], dtype=np.int64); Y = np.array([q[1] for q in pts], dtype=np.int64)
    sq = np.zeros(p, bool); sq[(np.arange(p, dtype=np.int64) ** 2) % p] = True
    hx = lambda v, t: int(hashlib.sha256(f'{t}-{v}-{p}'.encode()).digest()[0]) & 1
    preds = {'chi(x)': sq[X], 'chi(y)': sq[Y], 'chi(x+1)': sq[(X + 1) % p], 'chi(2x)': sq[(2 * X) % p],
             'chi(x^2+x+1)': sq[(X * X + X + 1) % p], 
             'parity(x)': (X % 2 == 0), 'parity(y)': (Y % 2 == 0), 'x<p/2': (X < p / 2),
             'sha256(x) bit': np.array([hx(int(v), 'x') for v in X], bool),
             'chi(x*y)': sq[(X * Y) % p], 'chi(x) order-shuffled': np.array(rng.sample(list(sq[X]), h)), 'iid': np.array([rng.random() < .5 for _ in range(h)])}
    for k, v in preds.items():
        res.setdefault(k, []).append((powvar(v.astype(int)), lag1sd(v.astype(int)), p % 4))
out = {}
for k, v in res.items():
    pv = np.array([a for a, _, _ in v]); lg = np.array([b for _, b, _ in v])
    out[k] = {'mean_periodogram_var': float(pv.mean()), 'sd_of_that_across_curves': float(pv.std()),
              'var_of_lag1_z(expect 1)': float((lg ** 2).mean()), 'n_curves': len(v)}
    print(f'{k:28s} periodogram-var {pv.mean():.3f} (sd {pv.std():.3f})  mean z1^2 {np.mean(lg**2):.3f}')
json.dump(out, open(os.path.join(HERE, 'eb_diag.json'), 'w'), indent=1)
