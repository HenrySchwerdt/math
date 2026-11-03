"""Round-20 inventor J: learned/hand estimators for MSB(k), k, and closeness |d|<=w. See PROTOCOL.md."""
import sys, os, json, subprocess, math, time
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
HERE = os.path.dirname(os.path.abspath(__file__))
CURVES = json.load(open(os.path.join(HERE, 'curves.json')))

def raw(c, scal):
    o = subprocess.run([os.path.join(HERE, 'feat'), str(c['p']), str(c['a']), str(c['b']), str(c['Px']), str(c['Py'])],
                       input=np.asarray(scal, dtype=np.uint32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(o, dtype=np.uint32).reshape(-1, 22).astype(np.int64)

def kclass(s, r):
    m = np.minimum(s, r - s).astype(np.uint64)
    return ((m * np.uint64(2654435761)) >> np.uint64(7)) & np.uint64(1)

def bitsof(v, n):
    return ((v[:, None] >> np.arange(n)[None, :]) & 1).astype(np.float32)

def features(c, R):
    p = c['p']; nb = int(p).bit_length(); f = []
    x, y = R[:, 1], R[:, 2]
    f += [x / p, y / p, (y % 2), (y > p // 2), bitsof(x, nb), bitsof(y, nb)]
    for j in range(6):
        xx, yy = R[:, 3 + 2 * j], R[:, 4 + 2 * j]
        dx = (xx - x) % p; dy = (yy - y) % p
        f += [xx / p, yy / p, dx / p, dy / p, (xx < x), (xx < p // 2), yy % 2, (yy < y), bitsof(xx, 8), bitsof(dx, 8)]
    x2, y2 = R[:, 15], R[:, 16]
    f += [x2 / p, y2 / p, (x2 < x), x2 % 2, y2 % 2, bitsof(x ^ x2, 8), ((x2 - x) % p) / p]
    f += [R[:, 17:22] == 1, R[:, 17:22] == 2]
    # carries / borrows
    for a, b, op in ((x, c['Px'], 1), (x, c['Px'], -1), (y, c['Py'], 1)):
        bb = np.full_like(a, b); car = np.zeros(len(a), dtype=np.int64); cols = []
        for i in range(nb):
            ai = (a >> i) & 1; bi = (bb >> i) & 1
            if op == 1:
                s = ai + bi + car; car = s >> 1
            else:
                s = ai - bi - car; car = (s < 0).astype(np.int64)
            cols.append(car)
        f.append(np.stack(cols, 1).astype(np.float32))
    F = [np.asarray(a, dtype=np.float32).reshape(len(x), -1) for a in f]
    return np.concatenate(F, 1)

def hbern(R, c, thr=450):
    h = (R[:, 1] * 6364136223846793005 + R[:, 2] * 1442695040888963407 + c['seed'] * 977 + 12345) & ((1 << 62) - 1)
    h ^= h >> 29; h = (h * 0xBF58476D1CE4E5B) & ((1 << 62) - 1); h ^= h >> 31
    return (h % 1000) < thr

def wilson(k, n, z=2.576):
    ph = k / n; den = 1 + z * z / n; cen = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return cen - hw, cen + hw

def draw(rng, c, n, cls, kind, w=None):
    """distinct +-pairs (key=min(s,r-s)) per curve; msb: s uniform; close: class a (|d|<=w, random sign) vs b (uniform), balanced.
    returns scalars, labels (capped by the number of distinct available points)."""
    r = c['r']; m = 6 * n + 200
    if kind == 'msb':
        s = rng.integers(1, r, m); y = (s > r // 2).astype(int)
    else:
        isa = rng.integers(0, 2, m)
        d = rng.integers(1, w + 1, m) * rng.choice([-1, 1], m)
        ub = rng.integers(1, r, m)
        s = np.where(isa == 1, d % r, ub); y = isa
    key = np.minimum(s, r - s)
    if cls is not None:
        keep = kclass(s, r) == cls; s, y, key = s[keep], y[keep], key[keep]
    code = key * 2 + (y if kind == 'close' else 0)
    _, first = np.unique(code, return_index=True); first.sort()
    s, y = s[first], y[first]
    if kind == 'close':
        ia, ib = np.where(y == 1)[0], np.where(y == 0)[0]
        h = min(len(ia), len(ib), n // 2); sel = np.concatenate([ia[:h], ib[:h]]); s, y = s[sel], y[sel]
    else:
        s, y = s[:n], y[:n]
    return s.astype(np.int64), y.astype(np.int64)

def build(bits, kind, w, nTr, nA, nB, seed):
    cs = [c for c in CURVES if c['bits'] == bits]
    rng = np.random.default_rng(seed)
    sets = {k: ([], [], [], []) for k in ('train', 'A', 'B')}
    for c in cs:
        c['seed'] = c['seed']
        if c['role'] == 'train':
            for name, n, cls in (('train', nTr, 0), ('A', nA, 1)):
                s, y = draw(rng, c, n, cls, kind, w)
                R = raw(c, s); F = features(c, R)
                sets[name][0].append(F); sets[name][1].append(y); sets[name][2].append(hbern(R, c)); sets[name][3].append(np.minimum(s, c['r'] - s) if kind == 'close' else s * 0 + s)
        else:
            s, y = draw(rng, c, nB, None, kind, w)
            R = raw(c, s); F = features(c, R)
            sets['B'][0].append(F); sets['B'][1].append(y); sets['B'][2].append(hbern(R, c)); sets['B'][3].append(np.minimum(s, c['r'] - s) if kind == 'close' else s * 0 + s)
    return {k: tuple(np.concatenate(v) for v in vs) for k, vs in sets.items()}

def theta_data(bits, nTr, nA, nB, seed):
    cs = [c for c in CURVES if c['bits'] == bits]; rng = np.random.default_rng(seed)
    sets = {k: ([], [], [], []) for k in ('train', 'A', 'B')}
    for c in cs:
        if c['role'] == 'train':
            for name, n, cls in (('train', nTr, 0), ('A', nA, 1)):
                s, _ = draw(rng, c, n, cls, 'msb'); R = raw(c, s)
                sets[name][0].append(features(c, R)); sets[name][1].append(s / c['r'])
        else:
            s, _ = draw(rng, c, nB, None, 'msb'); R = raw(c, s)
            sets['B'][0].append(features(c, R)); sets['B'][1].append(s / c['r'])
    return {k: (np.concatenate(v[0]), np.concatenate(v[1])) for k, v in sets.items() if v[0]}

def eval_cls(tag, D, rng, control, extra=None):
    Xtr, ytr, btr, _ = D['train']
    def aug(split):
        X, y, b, _ = D[split]
        if control:
            leak = (y ^ b).astype(np.float32)[:, None]   # planted: label xor hash noise (prob .45 flip)
            X = np.concatenate([X, leak], 1)
        return X
    Xtr_, XA, XB = aug('train'), aug('A'), aug('B')
    res = {}
    models = {}
    t = time.time()
    m1 = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, early_stopping=True, validation_fraction=0.1, random_state=0).fit(Xtr_, ytr)
    models['M1_hgb'] = m1.predict
    idx = rng.choice(len(Xtr_), min(100000, len(Xtr_)), replace=False)
    sc = StandardScaler().fit(Xtr_[idx])
    m2 = MLPClassifier((128, 64), early_stopping=True, max_iter=60, random_state=0).fit(sc.transform(Xtr_[idx]), ytr[idx])
    models['M2_mlp'] = lambda X: m2.predict(sc.transform(X))
    m3 = LogisticRegression(max_iter=300).fit(sc.transform(Xtr_[idx]), ytr[idx])
    models['M3_logit'] = lambda X: m3.predict(sc.transform(X))
    # M4 best single feature
    best = (0.5, None)
    for j in range(Xtr_.shape[1]):
        col = Xtr_[:, j]; qs = np.unique(np.quantile(col, np.linspace(0.02, 0.98, 25)))
        for th in qs:
            a = np.mean((col > th) == ytr)
            for sgn, aa in ((1, a), (-1, 1 - a)):
                if abs(aa - 0.5) > abs(best[0] - 0.5): best = (aa, (j, th, sgn))
    j, th, sgn = best[1] if best[1] else (0, 0, 1)
    models['M4_single'] = lambda X: ((X[:, j] > th) == (sgn == 1)).astype(int)
    for name, pred in models.items():
        for split, X in (('A', XA), ('B', XB)):
            y = D[split][1]; yh = pred(X); k = int((yh == y).sum()); n = len(y)
            lo, hi = wilson(k, n)
            res[f'{name}_{split}'] = dict(acc=k / n, n=n, lo99=lo, hi99=hi, adv=k / n - .5, adv_lo=lo - .5, adv_hi=hi - .5)
    res['train_acc_M1'] = float((m1.predict(Xtr_) == ytr).mean()); res['single_feature'] = [int(j), float(th), int(sgn)]
    res['secs'] = time.time() - t
    return res, models

def main():
    bits = int(sys.argv[1]); task = sys.argv[2]; control = int(sys.argv[3])
    seed = bits * 1000 + 7
    rng = np.random.default_rng(seed + 1)
    nTr, nA, nB = 20000, 25000, 50000
    out = dict(bits=bits, task=task, control=control)
    if task == 'msb':
        D = build(bits, 'msb', None, nTr, nA, nB, seed)
        res, _ = eval_cls(task, D, rng, control); out.update(res)
    elif task.startswith('close'):
        w = int(task[5:]); cs = [c for c in CURVES if c['bits'] == bits]
        if w > cs[0]['r'] // 16: out['skipped'] = 'w > r/16'; print(json.dumps(out)); return
        D = build(bits, 'close', w, nTr, nA, nB, seed)
        res, models = eval_cls(task, D, rng, control); out.update(res)
        # beyond-table: class a with |d|>16 versus class b (rebalanced) -- needs |d| per sample
        if w > 16:
            bt = {}
            for split in ('A', 'B'):
                X, y, b, dabs = D[split]
                if control: X = np.concatenate([X, (y ^ b).astype(np.float32)[:, None]], 1)
                keepa = (y == 1) & (dabs > 16); idxb = np.where(y == 0)[0]
                ia = np.where(keepa)[0]; ib = idxb[:len(ia)]
                sel = np.concatenate([ia, ib]); ysel = y[sel]
                for name, pred in models.items():
                    k = int((pred(X[sel]) == ysel).sum()); n = len(sel); lo, hi = wilson(k, n)
                    bt[f'{name}_{split}'] = dict(acc=k / n, n=n, lo99=lo, hi99=hi, adv=k / n - .5, adv_lo=lo - .5, adv_hi=hi - .5)
            out['beyond_table'] = bt
        else:
            out['beyond_table'] = 'table-trivial (all |d|<=16)'
    elif task == 'regress':
        D = theta_data(bits, nTr, nA, nB, seed)
        Xtr, th = D['train']
        t0 = time.time()
        def circ(a, b): d = (a - b + 0.5) % 1 - 0.5; return np.abs(d)
        for ctl in ([control]):
            def aug(X, th):
                if not ctl: return X
                rr = np.random.default_rng(5)
                lk = (th + rr.normal(0, 0.1, len(th))) % 1
                return np.concatenate([X, lk[:, None], np.sin(2 * np.pi * lk)[:, None], np.cos(2 * np.pi * lk)[:, None]], 1)
            ms = [HistGradientBoostingRegressor(max_iter=150, early_stopping=True, random_state=0).fit(aug(Xtr, th), f(2 * np.pi * th)) for f in (np.sin, np.cos)]
            rr = {}
            for split in ('A', 'B'):
                X, t = D[split]; Xa = aug(X, t)
                s_, c_ = ms[0].predict(Xa), ms[1].predict(Xa)
                that = (np.arctan2(s_, c_) / (2 * np.pi)) % 1
                e = circ(that, t)
                r2s = 1 - np.sum((s_ - np.sin(2 * np.pi * t)) ** 2) / np.sum((np.sin(2 * np.pi * t) - np.sin(2 * np.pi * t).mean()) ** 2)
                r2c = 1 - np.sum((c_ - np.cos(2 * np.pi * t)) ** 2) / np.sum((np.cos(2 * np.pi * t) - np.cos(2 * np.pi * t).mean()) ** 2)
                bs = np.random.default_rng(9); med = []; q90 = []
                for _ in range(200):
                    ii = bs.integers(0, len(e), len(e)); med.append(np.median(e[ii])); q90.append(np.quantile(e[ii], 0.9))
                rr[split] = dict(R2_sin=r2s, R2_cos=r2c, med_err=float(np.median(e)), med_ci=[float(np.quantile(med, .025)), float(np.quantile(med, .975))],
                                 q90_err=float(np.quantile(e, .9)), q90_ci=[float(np.quantile(q90, .025)), float(np.quantile(q90, .975))],
                                 w50=float(2 * np.median(e)), w90=float(2 * np.quantile(e, .9)), n=len(e))
            out['control_regress' if ctl else 'real_regress'] = rr
        out['secs'] = time.time() - t0
    print(json.dumps(out))

if __name__ == '__main__': main()
