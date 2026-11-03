"""Round 6 / ECDLP-18: index calculus on J_C for the genus-2 double cover C: y^2 = f(w^2+c) -> E.

Usage: python3 icj.py --bits 12 --curves 3 --out results_bits12.json [--variants A,B,Bhalf]
See PROTOCOL.md.  Synthetic toy curves only.
"""
import argparse, json, math, random, sys, time, heapq, os
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from toyec import Curve, dlog_bsgs, is_prime
from hyper2 import *
import hyper2

MASTER = 20261109


class CCurve(Curve):
    n_add = 0

    def add(self, P, Q):
        CCurve.n_add += 1
        return Curve.add(self, P, Q)


def prime_below(n):
    n -= 1
    while not is_prime(n):
        n -= 1
    return n


def poly_F(a, b, c, p):
    """F(w) = f(w^2 + c), f = x^3 + a x + b."""
    X = (c % p, 0, 1)
    F, pw = (), (1,)
    for coef in (b, a, 0, 1):
        F = padd(F, pscal(pw, coef, p), p)
        pw = pmul(pw, X, p)
    return F


def sq_tables(p):
    sq = np.zeros(p, dtype=bool)
    root = np.zeros(p, dtype=np.int64)
    ys = np.arange(p, dtype=np.int64)
    s = (ys * ys) % p
    sq[s[1:]] = True
    root[s[::-1]] = ys[::-1]          # some root of each square
    sq[0] = False
    return sq, root


def eval_poly_np(F, p, ws):
    acc = np.zeros_like(ws)
    for cf in reversed(F):
        acc = (acc * ws + cf) % p
    return acc


def count_C_Fp(F, p, sq):
    vals = eval_poly_np(F, p, np.arange(p, dtype=np.int64))
    zeros = int((vals == 0).sum())
    nsq = int(sq[vals].sum())
    return 2 + 2 * nsq + zeros, vals        # infinity: 2 points (monic, deg 6)


def count_C_Fp2(F, p, sq):
    nu = next(x for x in range(2, p) if not sq[x])
    tot = 0
    bs = np.arange(p, dtype=np.int64)
    blk = max(1, (1 << 20) // p)
    for a0 in range(0, p, blk):
        a = np.arange(a0, min(p, a0 + blk), dtype=np.int64)[:, None] * np.ones((1, p), dtype=np.int64)
        b = np.ones((a.shape[0], 1), dtype=np.int64) * bs[None, :]
        X = np.zeros_like(a); Y = np.zeros_like(a)
        for cf in reversed(F):
            X, Y = (X * a + nu * Y % p * b + cf) % p, (X * b + Y * a) % p
        N = (X * X - nu * Y % p * Y) % p
        # F(W)=X+Y*theta; norm = X^2 - nu Y^2
        zeros = int((N == 0).sum())
        tot += int(sq[N].sum()) * 2 + zeros
    return 2 + tot


def setup_curve(bits, idx, p):
    rng = random.Random(f"{MASTER}/{bits}/{idx}")
    sq, root = sq_tables(p)
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        try:
            E = CCurve(a, b, p)
        except ValueError:
            continue
        r = E.order()
        if r != p and is_prime(r) and r > 7:
            break
    tE = p + 1 - r
    for c in range(1, p):
        if (c ** 3 + a * c + b) % p == 0:
            continue
        F = poly_F(a, b, c, p)
        N1, vals = count_C_Fp(F, p, sq)
        S1 = p + 1 - N1
        tEp = S1 - tE
        m = p + 1 - tEp
        if math.gcd(r, m) == 1 and tEp * tEp <= 4 * p and m > 0:
            break
    return dict(rng=rng, E=E, a=a, b=b, r=r, c=c, F=F, N1=N1, m=m, tE=tE, tEp=tEp, S1=S1, vals=vals, sq=sq, root=root)


def lpoly_J(p, N1, N2):
    S1 = p + 1 - N1
    S2 = p * p + 1 - N2
    e2 = (S1 * S1 - S2) // 2
    assert (S1 * S1 - S2) % 2 == 0
    return 1 - S1 + e2 - p * S1 + p * p, (S1, e2)


# ---------------- elimination mod prime r ----------------

def solve_mod(rows, rhs, ncols, r, rng, dense_cols=1500, wmax=6):
    """Solve rows * x = rhs mod r (rows: list of dict col->val).  Returns dict with
    solutions for two different free-variable assignments, rank, #active columns, counted mults."""
    mult = 0
    rows = [dict(x) for x in rows]
    rhs = list(rhs)
    colrows = defaultdict(set)
    for i, row in enumerate(rows):
        for c in row:
            colrows[c].add(i)
    active_cols = {c for c in colrows}
    n_active = len(active_cols)
    heap = [(len(s), c) for c, s in colrows.items()]
    heapq.heapify(heap)
    alive = set(range(len(rows)))
    piv = []                                   # (col, rowdict(without col), rhs)
    inconsistent = False
    while heap:
        w, c = heapq.heappop(heap)
        cur = len(colrows.get(c, ()))
        if cur == 0 or cur != w:
            if cur:
                heapq.heappush(heap, (cur, c))
            continue
        if w > wmax or len(active_cols) - len(piv) <= dense_cols:
            heapq.heappush(heap, (w, c))
            break
        i = min(colrows[c], key=lambda j: len(rows[j]))
        prow = rows[i]
        inv = pow(prow[c], -1, r)
        prow = {k: v * inv % r for k, v in prow.items()}
        prhs = rhs[i] * inv % r
        mult += len(prow)
        for k in prow:
            colrows[k].discard(i)
        alive.discard(i)
        for j in list(colrows[c]):
            f = rows[j][c]
            rj = rows[j]
            for k, v in prow.items():
                nv = (rj.get(k, 0) - f * v) % r
                if nv:
                    if k not in rj:
                        colrows[k].add(j)
                    rj[k] = nv
                else:
                    if k in rj:
                        del rj[k]
                        colrows[k].discard(j)
            rhs[j] = (rhs[j] - f * prhs) % r
            mult += len(prow)
        colrows[c] = set()
        piv.append((c, {k: v for k, v in prow.items() if k != c}, prhs))
        for k in prow:
            if k != c and colrows[k]:
                heapq.heappush(heap, (len(colrows[k]), k))
    # dense core
    core_cols = sorted(c for c, s in colrows.items() if s)
    core_rows = [i for i in alive if rows[i]]
    cidx = {c: j for j, c in enumerate(core_cols)}
    nr, nc = len(core_rows), len(core_cols)
    M = np.zeros((nr, nc + 1), dtype=np.int64)
    for a_, i in enumerate(core_rows):
        for c, v in rows[i].items():
            M[a_, cidx[c]] = v
        M[a_, nc] = rhs[i]
    pcols = []
    row = 0
    for col in range(nc):
        if row >= nr:
            break
        nz = np.nonzero(M[row:, col])[0]
        if len(nz) == 0:
            continue
        k = row + nz[0]
        if k != row:
            M[[row, k]] = M[[k, row]]
        M[row] = M[row] * pow(int(M[row, col]), -1, r) % r
        below = np.nonzero(M[row + 1:, col])[0] + row + 1
        if len(below):
            fac = M[below, col].copy()
            M[below, :] = (M[below, :] - fac[:, None] * M[row][None, :]) % r
            mult += len(below) * (nc + 1 - col)
        pcols.append(col)
        row += 1
    rank_dense = len(pcols)
    for i in range(rank_dense, nr):
        if M[i, nc] % r:
            inconsistent = True
    # also rows beyond rank_dense that are all-zero but rhs nonzero already checked
    free_core = [c for j, c in enumerate(core_cols) if j not in set(pcols)]
    rank = len(piv) + rank_dense

    def back(assign_free):
        x = {}
        for c in free_core:
            x[c] = assign_free(c)
        for ri in range(rank_dense - 1, -1, -1):
            pc = pcols[ri]
            s = int(M[ri, nc])
            rowv = M[ri, pc + 1:nc]
            nzj = np.nonzero(rowv)[0]
            for j in nzj:
                s -= int(rowv[j]) * x[core_cols[pc + 1 + j]]
            x[core_cols[pc]] = s % r
        for c, prow, prhs in reversed(piv):
            s = prhs
            for k, v in prow.items():
                if k not in x:
                    x[k] = assign_free(k)
                s -= v * x[k]
            x[c] = s % r
        return x

    x1 = back(lambda c: 0)
    x2 = back(lambda c, _m={}: _m.setdefault(c, rng.randrange(r)))
    return dict(x1=x1, x2=x2, rank=rank, n_active=n_active, mult=mult, inconsistent=inconsistent,
                core=(nr, nc), sparse_pivots=len(piv))


# ---------------- the experiment on one curve ----------------

def run_curve(bits, idx, variants, tlimit):
    t_all = time.time()
    p = prime_below(1 << bits)
    S = setup_curve(bits, idx, p)
    rng, E, r, c, F = S['rng'], S['E'], S['r'], S['c'], S['F']
    J = Genus2(F, p)
    res = dict(bits=bits, idx=idx, p=p, a=S['a'], b=S['b'], r=r, c=c, F=list(F), N1=S['N1'], m=S['m'],
               tE=S['tE'], tEp=S['tEp'])
    sq, root, vals = S['sq'], S['root'], S['vals']
    # factor base: one orbit per w with F(w) square; canonical y
    ws = [int(w) for w in np.nonzero(sq[vals])[0]]
    ycan = {w: min(int(root[vals[w]]), p - int(root[vals[w]])) for w in ws}
    # ---- checks ----
    chk = {}
    t0 = time.time()
    if bits <= 14 and (idx == 0 or bits <= 12):
        N2 = count_C_Fp2(F, p, sq)
        JJ, (S1, e2) = lpoly_J(p, S['N1'], N2)
        chk['N2'] = N2
        chk['Lpoly_J_at_1'] = JJ
        chk['r_times_m'] = r * S['m']
        chk['Lpoly_ok'] = (JJ == r * S['m'])
    chk['count_time_s'] = round(time.time() - t0, 2)
    NJ = r * S['m']
    pts = E.points()[1:]
    P = rng.choice(pts)
    k_true = rng.randrange(1, r)
    Qp = E.mul(k_true, P)
    # group-law checks
    ok = dict(assoc=0, assoc_fail=0, assoc_degenerate=0, comm_fail=0, inv_fail=0, hom_fail=0, hom_n=0, order_fail=0, order_n=0)

    def rand_el():
        while True:
            w1, w2 = rng.sample(ws, 2)
            y1 = ycan[w1] if rng.random() < .5 else p - ycan[w1]
            y2 = ycan[w2] if rng.random() < .5 else p - ycan[w2]
            return J.pair((w1, y1), (w2, y2))
    for _ in range(500):
        A, B, C = rand_el(), rand_el(), rand_el()
        try:
            l = J.add(J.add(A, B), C); rr = J.add(A, J.add(B, C))
            ok['assoc'] += 1
            ok['assoc_fail'] += (l != rr)
            if J.add(A, B) != J.add(B, A):
                ok['comm_fail'] += 1
            if J.add(A, J.neg(A)) is not None:
                ok['inv_fail'] += 1
        except Degenerate:
            ok['assoc_degenerate'] += 1
    for _ in range(100):
        Q1, Q2 = rng.sample(pts, 2)
        Q3 = E.add(Q1, Q2)
        try:
            s = J.add(J.fibre(Q1[0], Q1[1], c), J.fibre(Q2[0], Q2[1], c))
            tgt = None if Q3 is None else J.fibre(Q3[0], Q3[1], c)
            ok['hom_n'] += 1
            ok['hom_fail'] += (s != tgt)
        except Degenerate:
            pass
    for _ in range(20):
        try:
            D = rand_el()
            ok['order_n'] += 1
            ok['order_fail'] += (J.mul(NJ, D) is not None)
        except Degenerate:
            pass
    piP = J.fibre(P[0], P[1], c)
    ok['r_piP_is_zero'] = J.mul(r, piP) is None
    ok['piP_nonzero'] = piP is not None
    res['checks'] = dict(chk, **ok)
    res['setup_time_s'] = round(time.time() - t_all, 2)

    # ---- baseline on E ----
    CCurve.n_add = 0
    t0 = time.time()
    kb = dlog_bsgs(E, P, Qp, r)
    res['bsgs'] = dict(k=kb, ok=(kb == k_true), ec_adds=CCurve.n_add, time_s=round(time.time() - t0, 4),
                       sqrt_r=round(math.sqrt(r), 1), rho_analytic=round(1.2533 * math.sqrt(r), 1))
    res['sqrt_p'] = round(math.sqrt(p), 2)
    res['n_orbits'] = len(ws)

    # ---- index calculus ----
    def run_variant(name):
        t0 = time.time()
        hyper2.OPS['cantor'] = 0
        CCurve.n_add = 0
        fb = ws
        if name == 'Bhalf':
            fb = sorted(rng.sample(ws, len(ws) // 2))
        fbset = set(fb)
        col = {w: i for i, w in enumerate(fb)}
        m_ = len(fb)
        NC, KC = m_, m_ + 1                     # columns for n and k

        def vec_point(w, y, d, mult=1):
            if y == ycan[w]:
                d[col[w]] = d.get(col[w], 0) + mult
            else:
                d[col[w]] = d.get(col[w], 0) - mult
                d[NC] = d.get(NC, 0) - mult

        def split(Z):
            u, v = Z
            u1, u0 = u[1], u[0]
            disc = (u1 * u1 - 4 * u0) % p
            if disc and not sq[disc]:
                return None
            s = int(root[disc]) if disc else 0
            h = pow(2, -1, p)
            w1 = (-u1 + s) * h % p
            w2 = (-u1 - s) * h % p
            out = []
            for w in (w1, w2):
                y = (v[0] + (v[1] if len(v) > 1 else 0) * w) % p
                out.append((w, y))
            return out
        # additive walk in E
        L = 32
        steps = []
        for _ in range(L):
            aj, bj = rng.randrange(r), rng.randrange(r)
            steps.append((aj, bj, E.add(E.mul(aj, P), E.mul(bj, Qp))))
        al, be = rng.randrange(r), rng.randrange(r)
        Qc = E.add(E.mul(al, P), E.mul(be, Qp))
        rows, rhs = [], []
        trials = 0
        seen_x = {}                 # x(Q') -> (alpha, beta, sign) first seen (variant A diagnostics)
        diag = dict(first_collision_ec=None, first_collision_trial=None, dedup_rows=[], dedup_rhs=[])

        def one_trial():
            nonlocal al, be, Qc, trials
            aj, bj, Tj = rng.choice(steps)
            al, be = (al + aj) % r, (be + bj) % r
            Qc = E.add(Qc, Tj)
            trials += 1
            if Qc is None:
                return
            S_el = J.fibre(Qc[0], Qc[1], c)
            row = {}
            if name == 'A':
                prev = seen_x.get(Qc[0])
                if prev is None:
                    seen_x[Qc[0]] = (al, be)
                    diag['_dedup_pending'] = True
                else:
                    diag['_dedup_pending'] = False
                    if diag['first_collision_ec'] is None and prev != (al, be):
                        diag['first_collision_ec'] = CCurve.n_add
                        diag['first_collision_trial'] = trials
            if name == 'A':
                Z = S_el
            else:
                wa, wb = rng.sample(fb, 2)
                ya = ycan[wa] if rng.random() < .5 else p - ycan[wa]
                yb = ycan[wb] if rng.random() < .5 else p - ycan[wb]
                H = J.pair((wa, ya), (wb, yb))
                try:
                    Z = J.add(S_el, H)
                except Degenerate:
                    return
                if Z is None:
                    return
                hv = {}
                vec_point(wa, ya, hv); vec_point(wb, yb, hv)
                hv[NC] = hv.get(NC, 0) + 1
                for k_, v_ in hv.items():
                    row[k_] = row.get(k_, 0) - v_
            pts_ = split(Z)
            if pts_ is None:
                return
            if any(w not in fbset for w, _ in pts_):
                return
            for w, y in pts_:
                vec_point(w, y, row)
            row[KC] = (row.get(KC, 0) - be) % r
            row = {k_: v_ % r for k_, v_ in row.items() if v_ % r}
            rows.append(row)
            rhs.append(al % r)
            if name == 'A' and diag.get('_dedup_pending'):
                diag['dedup_rows'].append(row)
                diag['dedup_rhs'].append(al % r)

        target = (m_ + 20) if name != 'A' else 3 * m_
        la_total = 0
        attempts = 0
        sol = None
        nrel_at_solve = 0
        while True:
            if time.time() - t_all > tlimit:
                return dict(variant=name, status='timeout', relations=len(rows), trials=trials,
                            cantor=hyper2.OPS['cantor'], ec=CCurve.n_add, la=la_total, time_s=round(time.time() - t0, 2))
            while len(rows) < target:
                one_trial()
                if name == 'A' and trials > 20 * target + 1000:
                    break
            attempts += 1
            tl = time.time()
            sol = solve_mod(rows, rhs, m_ + 2, r, rng)
            la_total += sol['mult']
            nrel_at_solve = len(rows)
            kc = sol['x1'].get(KC)
            det = (KC in sol['x1']) and sol['x1'][KC] == sol['x2'][KC] and not sol['inconsistent']
            if name == 'A' or det:
                break
            target = len(rows) + max(20, len(rows) // 10)
        info = dict(variant=name, relations=nrel_at_solve, trials=trials, attempts=attempts, cantor=hyper2.OPS['cantor'],
                    ec=CCurve.n_add + 0, la=la_total, rank=sol['rank'], unknowns_active=sol['n_active'],
                    deficiency=sol['n_active'] - sol['rank'], inconsistent=sol['inconsistent'], fb_orbits=m_,
                    core=sol['core'], sparse_pivots=sol['sparse_pivots'], time_s=round(time.time() - t0, 2))
        kdet = (KC in sol['x1']) and sol['x1'][KC] == sol['x2'][KC] and not sol['inconsistent']
        info['k_determined'] = bool(kdet)
        info['k_ic'] = sol['x1'].get(KC) if kdet else None
        info['k_correct'] = bool(kdet and sol['x1'][KC] == k_true and sol['x1'][KC] == kb)
        info['total'] = info['cantor'] + info['ec'] + info['la']
        if name == 'A':
            sd = solve_mod(diag['dedup_rows'], diag['dedup_rhs'], m_ + 2, r, rng)
            kd = (KC in sd['x1']) and sd['x1'][KC] == sd['x2'][KC] and not sd['inconsistent']
            info['dedup'] = dict(rows=len(diag['dedup_rows']), rank=sd['rank'], unknowns_active=sd['n_active'],
                                 k_determined=bool(kd), la=sd['mult'])
            info['first_collision_ec'] = diag['first_collision_ec']
            info['first_collision_trial'] = diag['first_collision_trial']
        if info['k_correct']:
            hyper2.OPS['cantor'] = 0
            try:
                info['verify_k_piP_eq_piQ'] = (J.mul(info['k_ic'], piP) == J.fibre(Qp[0], Qp[1], c))
            except Degenerate:
                info['verify_k_piP_eq_piQ'] = None
        return info
    res['variants'] = {}
    for v in variants:
        if v == 'Bhalf' and bits not in (10, 12):
            continue
        res['variants'][v] = run_variant(v)
        print(bits, idx, v, json.dumps({k: res['variants'][v].get(k) for k in
              ('relations', 'cantor', 'ec', 'la', 'total', 'rank', 'unknowns_active', 'k_determined', 'k_correct', 'status', 'time_s')}), flush=True)
    res['wall_time_s'] = round(time.time() - t_all, 2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bits', type=int, required=True)
    ap.add_argument('--curves', type=int, default=3)
    ap.add_argument('--variants', default='A,B,Bhalf')
    ap.add_argument('--first', type=int, default=0)
    ap.add_argument('--tlimit', type=float, default=270)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = []
    t0 = time.time()
    for idx in range(a.first, a.first + a.curves):
        if time.time() - t0 > a.tlimit * 0.8 and idx > a.first:
            print('time budget: stopping before curve', idx, flush=True)
            break
        out.append(run_curve(a.bits, idx, a.variants.split(','), a.tlimit - (time.time() - t0)))
    meta = dict(master_seed=MASTER, python=sys.version.split()[0], numpy=np.__version__, argv=sys.argv[1:])
    json.dump(dict(meta=meta, curves=out), open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
