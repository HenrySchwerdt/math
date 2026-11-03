"""E-A: near-character defect and Fourier correlation of low-complexity coordinate functions. See PROTOCOL.md."""
import sys, os, json, math, random, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from toyec import Curve, is_prime, dlog_bsgs
import stats

NCURVES, PLO, PHI = 12, 500, 5000
ALPHA = 0.01
FAMILY = [c for c in itertools.product((-1, 0, 1), repeat=4)
          if any(c) and next(v for v in c if v) > 0]
assert len(FAMILY) == 40


def gen_curve(rng):
    while True:
        p = rng.randint(PLO, PHI)
        if not is_prime(p):
            continue
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        E = Curve(a, b, p)
        pts = E.points()
        r = len(pts)
        if r == p or r < 5 or not is_prime(r):
            continue
        P = pts[rng.randrange(1, r)]
        return E, r, P


def enumerate_group(E, P, r):
    seq, R = [None], P
    for _ in range(r - 1):
        seq.append(R)
        R = E.add(R, P)
    assert R is None  # rP = O
    return seq


def defect_multi(N, Ms, rows=256):
    """N: (F, r) int64 numerators, Ms: (F,) denominators. Exact max/mean of ||f(a+b)-f(a)-f(b)|| over all pairs."""
    F, r = N.shape
    mx = np.zeros(F, dtype=np.int64)
    tot = np.zeros(F, dtype=np.float64)
    cols = np.arange(r)
    for s in range(0, r, rows):
        a = np.arange(s, min(r, s + rows))
        idx = (a[:, None] + cols[None, :]) % r
        for i in range(F):
            n, M = N[i], int(Ms[i])
            d = (n[idx] - n[a][:, None] - n[None, :]) % M
            d = np.minimum(d, M - d)
            mx[i] = max(mx[i], int(d.max()))
            tot[i] += float(d.sum()) / M
    return mx / Ms, tot / (r * r)


def fourier(n, M):
    r = len(n)
    z = np.exp(2j * np.pi * (n % M) / M)
    S = np.abs(np.fft.fft(z)) / r
    S[0] = 0.0
    return float(S.max()), int(S.argmax())


def tF(r, alpha_pt):
    return math.sqrt(math.log((r - 1) / alpha_pt) / r)


def run(seed):
    t0 = time.time()
    ncurve_tests = len(FAMILY) * NCURVES
    alpha_pt = ALPHA / ncurve_tests
    out = {'seed': seed, 'ncurves': NCURVES, 'family_size': len(FAMILY), 'alpha_fwer': ALPHA,
           'alpha_per_test': alpha_pt, 'curves': []}
    for ci in range(NCURVES):
        rng = random.Random(f'{seed}-{ci}')
        nrng = np.random.default_rng(rng.getrandbits(64))
        E, r, P = gen_curve(rng)
        p = E.p
        seq = enumerate_group(E, P, r)
        for j in rng.sample(range(r), 3):
            assert dlog_bsgs(E, P, seq[j], r) == j
        X = np.array([0 if q is None else q[0] for q in seq], dtype=np.int64)
        Y = np.array([0 if q is None else q[1] for q in seq], dtype=np.int64)
        T = tF(r, alpha_pt)
        # family
        N = np.array([(al * X + be * Y + ga * X * Y + de * X * X) % p for al, be, ga, de in FAMILY], dtype=np.int64)
        D, A = defect_multi(N, np.full(len(FAMILY), p))
        fam = []
        for i, c in enumerate(FAMILY):
            Fm, cs = fourier(N[i], p)
            pF = stats.max_exp_p(r * Fm * Fm, r - 1)
            fam.append({'coef': list(c), 'D': float(D[i]), 'avgD': float(A[i]), 'F': Fm, 'c_star': cs, 'p_F': pF,
                        'flag_F': Fm > T, 'flag_D': bool(D[i] < 0.25), 'flag_avg': bool(A[i] < 0.20)})
        # controls
        j = np.arange(r, dtype=np.int64)
        c0 = rng.randrange(1, r)
        ctr = {}
        chi = (c0 * j) % r
        specs = {'character': (chi, r)}
        specs['character_1/p_grid'] = (np.rint((chi / r) * p).astype(np.int64) % p, p)
        M30 = 2 ** 30
        base = np.rint((chi / r) * M30).astype(np.int64)
        noise = nrng.integers(-int(0.05 * M30), int(0.05 * M30) + 1, size=r)
        nz = (base + noise) % M30
        nz[0] = 0
        specs['character_noise0.05'] = (nz, M30)
        for w in (0.5, 0.2, 0.1):
            mask = nrng.random(r) < w
            mix = np.where(mask, base, nrng.integers(0, M30, size=r)) % M30
            mix[0] = 0
            specs[f'mixture_w{w}'] = (mix, M30)
        names = list(specs)
        Dc, Ac = defect_multi(np.array([specs[k][0] for k in names]), np.array([specs[k][1] for k in names]))
        for i, k in enumerate(names):
            Fm, cs = fourier(*specs[k])
            ctr[k] = {'D': float(Dc[i]), 'avgD': float(Ac[i]), 'F': Fm, 'c_star': cs, 'c_true': c0,
                      'flag_F': Fm > T, 'flag_D': bool(Dc[i] < 0.25)}
        # null
        nn = nrng.integers(0, M30, size=(10, r))
        nn[:, 0] = 0
        Dn, An = defect_multi(nn, np.full(10, M30))
        nullF = []
        for i in range(10):
            nullF.append(fourier(nn[i], M30)[0])
        for _ in range(300):
            v = nrng.integers(0, M30, size=r)
            v[0] = 0
            nullF.append(fourier(v, M30)[0])
        out['curves'].append({'index': ci, 'p': p, 'a': E.a, 'b': E.b, 'r': r, 'P': list(P), 'T_F': T,
                              'family': fam, 'controls': ctr,
                              'null': {'D_min': float(Dn.min()), 'D_max': float(Dn.max()), 'avgD_mean': float(An.mean()),
                                       'F_max': max(nullF), 'F_mean': float(np.mean(nullF)),
                                       'F_exceed_T': int(sum(f > T for f in nullF)), 'n_F': len(nullF)}})
        print(f'curve {ci} p={p} r={r} done {time.time()-t0:.1f}s', flush=True)
    # summary
    cs = out['curves']
    allf = [(c['index'], f) for c in cs for f in c['family']]
    pFs = [f['p_F'] for _, f in allf]
    ksD, ksP = stats.ks_uniform(pFs)
    out['summary'] = {
        'n_flag_F': sum(f['flag_F'] for _, f in allf), 'n_flag_D': sum(f['flag_D'] for _, f in allf),
        'n_flag_avg': sum(f['flag_avg'] for _, f in allf),
        'max_F_family': max(f['F'] for _, f in allf), 'max_F_over_T': max(f['F'] / c['T_F'] for c in cs for f in c['family']),
        'min_D_family': min(f['D'] for _, f in allf), 'min_avgD_family': min(f['avgD'] for _, f in allf),
        'min_pF': min(pFs), 'min_pF_bonferroni': min(1.0, min(pFs) * len(pFs)),
        'KS_pF_uniform': {'D': ksD, 'p': ksP, 'n': len(pFs)},
        'null_D_min': min(c['null']['D_min'] for c in cs), 'null_F_max_over_T': max(c['null']['F_max'] / c['T_F'] for c in cs),
        'null_F_exceed_T_total': sum(c['null']['F_exceed_T'] for c in cs), 'null_F_draws_total': sum(c['null']['n_F'] for c in cs),
        'controls_detected': {k: {'F_flag': sum(c['controls'][k]['flag_F'] for c in cs),
                                  'D_flag': sum(c['controls'][k]['flag_D'] for c in cs), 'of': len(cs)}
                              for k in cs[0]['controls']},
        'runtime_s': time.time() - t0}
    return out


if __name__ == '__main__':
    stats.selftest()
    seed = int(sys.argv[1])
    res = run(seed)
    path = os.path.join(HERE, sys.argv[2])
    json.dump(res, open(path, 'w'), indent=1)
    print(json.dumps(res['summary'], indent=1))
