"""A1: Farey-height factor-base index calculus with meet-in-the-middle relation search.
Usage: a1_farey_ic.py MODE bits   (MODE in l2,l3,m3,m3x : l-sums collisions; m3 = pair/single union (3-term);
m3x = same with small-integer-x base control)"""
import sys, time, json
from math import gcd
from common import *

def modinv_arr(a, p):
    res = np.ones_like(a); base = a % p; e = p - 2
    while e:
        if e & 1: res = res * base % p
        base = base * base % p; e >>= 1
    return res

def fb_farey(inst, s, kind='farey'):
    p, a, b = inst['p'], inst['a'], inst['b']
    xs = np.arange(p, dtype=np.int64)
    sq = np.zeros(p, dtype=bool); sq[(xs * xs) % p] = True
    X, Y, seen, fops = [], [], set(), 0
    def tryx(x):
        nonlocal fops
        v = (x ** 3 + a * x + b) % p; fops += 3
        if v and sq[v] and x not in seen:
            y = pow(v, (p + 1) // 4, p); fops += p.bit_length()
            y = min(y, p - y); seen.add(x); X.append(x); Y.append(y)
    h = 0
    while len(X) < s:
        h += 1
        if kind == 'smallx':
            tryx(h - 1); continue
        for v in range(1, h + 1):
            us = range(-h, h + 1) if v == h else (-h, h)
            for u in us:
                if gcd(abs(u), v) != 1: continue
                tryx(u * pow(v, -1, p) % p); fops += 2
                if len(X) >= s: break
            if len(X) >= s: break
    return np.array(X, dtype=np.int64), np.array(Y, dtype=np.int64), fops, h

def add_arr(x1, y1, x2, y2, p):
    dx = (x2 - x1) % p; ok = dx != 0
    dxs = np.where(ok, dx, 1)
    lam = (y2 - y1) % p * modinv_arr(dxs, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3, ok

def build_table(X, Y, p, mode):
    """returns x,y,idx(T,L),sg(T,L) of signed sums and #adds"""
    s = len(X); adds = 0
    I, J = np.triu_indices(s, 1)
    xs, ys, idxs, sgs = [], [], [], []
    pair = None
    for sg in (1, -1):
        x3, y3, ok = add_arr(X[I], Y[I], X[J], (sg * Y[J]) % p, p); adds += len(I)
        idx = np.stack([I, J], 1)[ok]; sgm = np.stack([np.ones(len(I), np.int8), np.full(len(I), sg, np.int8)], 1)[ok]
        xs.append(x3[ok]); ys.append(y3[ok]); idxs.append(idx); sgs.append(sgm)
    px, py = np.concatenate(xs), np.concatenate(ys)
    pidx, psg = np.concatenate(idxs), np.concatenate(sgs)
    if mode == 'l2':
        return px, py, pidx, psg, adds
    if mode == 'm3':
        n1 = len(X)
        ix = np.stack([np.arange(n1), np.full(n1, -1)], 1); sx = np.stack([np.ones(n1, np.int8), np.zeros(n1, np.int8)], 1)
        return (np.concatenate([px, X]), np.concatenate([py, Y]), np.concatenate([pidx, ix]),
                np.concatenate([psg, sx]), adds)
    # l3: pair sum + P_k, k > j
    xs, ys, idxs, sgs = [], [], [], []
    for k in range(s):
        sel = np.nonzero(pidx[:, 1] < k)[0]
        for sg in (1, -1):
            x3, y3, ok = add_arr(px[sel], py[sel], np.full(len(sel), X[k]), np.full(len(sel), (sg * Y[k]) % p), p); adds += len(sel)
            kk = np.stack([np.full(len(sel), k), np.full(len(sel), -1)], 1)
            idx = np.concatenate([pidx[sel], kk[:, :1]], 1)[ok]
            sgm = np.concatenate([psg[sel], np.full((len(sel), 1), sg, np.int8)], 1)[ok]
            xs.append(x3[ok]); ys.append(y3[ok]); idxs.append(idx); sgs.append(sgm)
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(idxs), np.concatenate(sgs), adds

def row_from(idx, sg, mult, d):
    for i, g in zip(idx, sg):
        if i >= 0 and g != 0:
            d[int(i)] = d.get(int(i), 0) + mult * int(g)

def solve_k(rows, trows, n_fb, r):
    """rows: list of dict col->coef (homog). trows: list of (dict, a, b) meaning sum - b*k = a. returns (k,mulmods)"""
    allrows = [(d, 0, 0) for d in rows] + list(trows)
    # prune rows having a column of count 1
    while True:
        cnt = {}
        for d, _, _ in allrows:
            for c in d: cnt[c] = cnt.get(c, 0) + 1
        keep = [t for t in allrows if all(cnt[c] > 1 for c in t[0])]
        if len(keep) == len(allrows): break
        allrows = keep
    if sum(1 for t in allrows if t[2]) < 2: return None, 0
    cols = sorted({c for d, _, _ in allrows for c in d}); cm = {c: i for i, c in enumerate(cols)}
    n = len(cols) + 1
    if len(allrows) > 3 * n + 50:
        trs = [t for t in allrows if t[2]]; hs = [t for t in allrows if not t[2]]
        allrows = hs[:3 * n] + trs
    A = np.zeros((len(allrows), n + 1), dtype=np.int64)
    for ri, (d, a, bb) in enumerate(allrows):
        for c, v in d.items(): A[ri, cm[c]] = v % r
        A[ri, n - 1] = (-bb) % r; A[ri, n] = a % r
    mm = 0; piv = 0; lead = {}
    for c in range(n):
        nzr = np.nonzero(A[piv:, c])[0]
        if len(nzr) == 0: continue
        q = piv + nzr[0]
        if q != piv: A[[piv, q]] = A[[q, piv]]
        A[piv, c:] = A[piv, c:] * pow(int(A[piv, c]), -1, r) % r
        f = A[piv + 1:, c]; nz = np.nonzero(f)[0] + piv + 1
        if len(nz):
            A[nz, c:] = (A[nz, c:] - A[nz, c][:, None] * A[piv, c:]) % r
            mm += len(nz) * (n + 1 - c)
        lead[c] = piv; piv += 1
        if piv == A.shape[0]: break
    if (n - 1) in lead:
        row = A[lead[n - 1]]
        if not row[:n - 1].any(): return int(row[n]), mm
    return None, mm

def run(inst, mode, c0=1.0):
    p, r, a, b = inst['p'], inst['r'], inst['a'], inst['b']
    P, Q = inst['P'], inst['Q']
    L = {'l2': 2, 'l3': 3, 'm3': 1.5, 'm3x': 1.5}[mode]
    tmode = 'm3' if mode == 'm3x' else mode
    kind = 'smallx' if mode == 'm3x' else 'farey'
    expo = 1.0 / (2 * L - 1) if L >= 2 else 0.5
    s = max(8, int(c0 * p ** expo)); total_adds = 0; tot_f = 0; tot_mm = 0; t0 = time.time(); attempts = 0
    rng = random.Random(inst['seed'] * 7 + 3)
    while True:
        attempts += 1
        X, Y, fops, H = fb_farey(inst, s, kind); tot_f += fops
        px, py, idx, sg, adds = build_table(X, Y, p, tmode); total_adds += adds
        order = np.argsort(px, kind='stable'); sx = px[order]
        # collisions
        rows = []
        brk = np.nonzero(np.diff(sx) != 0)[0] + 1
        starts = np.concatenate([[0], brk]); ends = np.concatenate([brk, [len(sx)]])
        for st, en in zip(starts, ends):
            if en - st < 2: continue
            if len(rows) >= 3 * len(X) + 60: break
            a0 = order[st]
            for q in order[st + 1:en]:
                eps = 1 if py[a0] == py[q] else -1 if (py[a0] + py[q]) % p == 0 else 0
                if eps == 0: continue
                d = {}; row_from(idx[a0], sg[a0], 1, d); row_from(idx[q], sg[q], -eps, d)
                d = {c: v for c, v in d.items() if v % r}
                if d: rows.append(d)
        # target decompositions
        C = CC(a, b, p)
        Mpts = []; trows = []; tries = 0
        while len(trows) < 4 and tries < 40:
            tries += 1
            new = []
            for _ in range(48):
                aa, bb = rng.randrange(1, r), rng.randrange(1, r)
                Rm = C.add(C.mul(aa, P), C.mul(bb, Q)); new.append((Rm, aa, bb))
            allm = Mpts + new
            cand = []
            for u in new:
                for v in allm:
                    if u is v: continue
                    if u[0][0] == v[0][0]: continue
                    cand.append((u, v))
            if not cand: Mpts += new; continue
            x1 = np.array([u[0][0] for u, v in cand]); y1 = np.array([u[0][1] for u, v in cand])
            x2 = np.array([v[0][0] for u, v in cand]); y2 = np.array([v[0][1] for u, v in cand])
            rx, ry, ok = add_arr(x1, y1, x2, y2, p); C.n += len(cand)
            pos = np.searchsorted(sx, rx); pos = np.minimum(pos, len(sx) - 1)
            for ci in np.nonzero(ok & (sx[pos] == rx))[0]:
                q = order[pos[ci]]
                eps = 1 if py[q] == ry[ci] else -1 if (py[q] + ry[ci]) % p == 0 else 0
                if eps == 0: continue
                u, v = cand[ci]
                # R = eps * table entry q ; R = aa+bb combos : a + b k = eps * sum L
                d = {}; row_from(idx[q], sg[q], eps, d)
                trows.append((d, (u[1] + v[1]) % r, (u[2] + v[2]) % r))
            Mpts += new
        total_adds += C.n
        k, mm = solve_k(rows, trows, len(X), r); tot_mm += mm
        if k is not None and E_check(inst, k):
            return dict(k=k, adds=total_adds, fops=tot_f, mulmods=tot_mm, s=len(X), H=H, table=len(sx),
                        rels=len(rows), trel=len(trows), attempts=attempts, secs=time.time() - t0)
        if attempts >= 8: return dict(k=None, adds=total_adds, fops=tot_f, mulmods=tot_mm, s=len(X), attempts=attempts)
        s = int(s * 1.25) + 1

def E_check(inst, k):
    E = Curve(inst['a'], inst['b'], inst['p'])
    return E.mul(k, inst['P']) == inst['Q']

if __name__ == '__main__':
    mode, b = sys.argv[1], int(sys.argv[2])
    out = open(os.path.join(HERE, f'out_a1_{mode}_{b}.jsonl'), 'w')
    for line in open(os.path.join(HERE, f'instances_{b}.jsonl')):
        inst = json.loads(line); inst['P'] = tuple(inst['P']); inst['Q'] = tuple(inst['Q'])
        res = run(inst, mode); res.update(bits=b, seed=inst['seed'], r=inst['r'], true_k=inst['k'], mode=mode)
        res['correct'] = res['k'] == inst['k'] or (res['k'] is not None and E_check(inst, res['k']))
        out.write(json.dumps(res) + '\n'); out.flush()
        print(mode, b, inst['seed'], res['correct'], res['adds'], res.get('s'), round(res.get('secs', 0), 1), flush=True)
