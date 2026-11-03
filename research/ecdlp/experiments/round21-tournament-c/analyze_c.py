"""E6 fit and E4 cost bar (model). ops = alpha sqrt(r) + gamma, least squares, bootstrap 95% CI over instances."""
import json, math, glob, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(os.path.join(HERE, 'results_e6_*.json'))): rows += json.load(open(f))
r = np.array([o['r'] for o in rows], float); y = np.array([o['ops'] for o in rows], float)
def fit(r, y):
    A = np.stack([np.sqrt(r), np.ones_like(r)], 1); return np.linalg.lstsq(A, y, rcond=None)[0]
a, g = fit(r, y)
rng = np.random.default_rng(1); bs = []
for _ in range(2000):
    i = rng.integers(0, len(r), len(r)); bs.append(fit(r[i], y[i]))
bs = np.array(bs)
print('n_instances', len(r), 'sizes', sorted(set(o['bits'] for o in rows)))
print('rho fit: alpha=%.3f [%.3f,%.3f]  gamma=%.1f [%.1f,%.1f]' % (a, *np.percentile(bs[:, 0], [2.5, 97.5]), g, *np.percentile(bs[:, 1], [2.5, 97.5])))
for b in sorted(set(o['bits'] for o in rows)):
    m = [o for o in rows if o['bits'] == b]; print(' bits', b, 'mean r %.0f mean ops %.1f  ops/sqrt(r) %.2f  fit %.1f' % (np.mean([o['r'] for o in m]), np.mean([o['ops'] for o in m]), np.mean([o['ops'] / math.sqrt(o['r']) for o in m]), a * math.sqrt(np.mean([o['r'] for o in m])) + g))
# cost bar for a planted multiplicative-class oracle with advantage eps (model, not measured)
def votes(eps, q, delta=0.01):  # Hoeffding-style count to read a q-ary class with error delta from eps-advantage votes
    return math.ceil(2 * math.log(2 * q / delta) / eps ** 2)
def cost(eps, r, S, beta=2.0):
    cv = 1.5 * math.log2(r) + 2           # one vote: multiply Q by a known random c (scalar mult) + oracle call
    Q = 1
    for q in S: Q *= q
    return sum(votes(eps, q) * cv for q in S) + beta * math.sqrt(max(r / Q, 1))
def eps_star(r, S):
    lo, hi = 1e-9, 1.0
    if cost(hi, r, S) >= a * math.sqrt(r) + g: return None
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if cost(mid, r, S) < a * math.sqrt(r) + g: hi = mid
        else: lo = mid
    return hi
print('break-even advantage eps* for the planted multiplicative-class oracle (model; BSGS beta=2 on the reduced space):')
S3 = [2, 3, 5]; S20 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
for e in (20, 24, 40, 64, 128, 256):
    r = 2.0 ** e
    print('  r=2^%d  S={2,3,5}: %s   S=20 primes<=71 (r-1 smooth): %s   r^(-1/4)=%.2e' % (e, eps_star(r, S3), eps_star(r, S20), r ** -0.25))
print('max possible gain from S={2,3,5} alone: sqrt(30)=%.2f' % math.sqrt(30))
