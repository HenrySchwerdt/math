"""Round 5 / ECDLP-13: structured factor bases on prime-field curves (toy). See PROTOCOL.md (written first)."""
import json, random, sys, time, math
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

MASTER = 20261103
T0 = time.time()

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

def prime_factors(n):
    f, d = [], 2
    while d * d <= n:
        if n % d == 0:
            f.append(d)
            while n % d == 0: n //= d
        d += 1
    if n > 1: f.append(n)
    return f

def find_prime(rng, k):
    lo, hi = int(0.9 * 2 ** k), int(1.1 * 2 ** k)
    while True:
        p = rng.randrange(lo, hi) | 1
        if not is_prime(p): continue
        s = math.isqrt(p)
        ds = [d for d in divisors(p - 1) if 0.8 * s <= d <= 1.25 * s]
        if ds: return p, rng.choice(ds)

def subgroup_gen(rng, p, h):
    pf = prime_factors(h)
    while True:
        u = rng.randrange(2, p - 1)
        g = pow(u, (p - 1) // h, p)
        if all(pow(g, h // q, p) != 1 for q in pf) and pow(g, h, p) == 1:
            return g

def build_curve(rng, p):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p: break
    E = Curve(a, b, p)
    sq = {}
    for y in range(p): sq.setdefault(y * y % p, []).append(y)
    ys = {}
    for x in range(p):
        r = sq.get((x ** 3 + a * x + b) % p)
        if r: ys[x] = r
    N = 1 + sum(len(v) for v in ys.values())
    return E, ys, N, sq

def points_of(xs, ys):
    V = []
    for x in xs:
        for y in ys[x]: V.append((x, y))
    return V

def pick_until(seq, ys, n):
    xs, cnt = [], 0
    for x in seq:
        if x in ys and x not in xs:
            xs.append(x); cnt += len(ys[x])
            if cnt >= n: break
    return xs

def sumset(E, V):
    reps, seen = [], set()
    for P in V:
        if P[0] not in seen: seen.add(P[0]); reps.append(P)
    mult = {}
    add = E.add
    for P1 in reps:
        for P2 in V:
            R = add(P1, P2)
            key = -1 if R is None else R[0]
            mult[key] = mult.get(key, 0) + 1
    M = len(reps) * len(V)
    return mult, M

def measure(E, V, Kx, label):
    mult, M = sumset(E, V)
    pi = len(mult) / Kx
    en = sum(m * m for m in mult.values()) / (M * M / Kx)
    return {'label': label, 'n': len(V), 'pi': pi, 'energy_ratio': en}

def chi_class(p, h, covered_x, ys):
    d = (p - 1) // h
    allc, cov = {}, {}
    for x in ys:
        if x: c = pow(x, h, p); allc[c] = allc.get(c, 0) + 1
    for x in covered_x:
        if x > 0: c = pow(x, h, p); cov[c] = cov.get(c, 0) + 1
    tot = sum(cov.values()); alln = sum(allc.values())
    chi, df = 0.0, -1
    for c, a in allc.items():
        e = tot * a / alln
        if e < 1: continue
        chi += (cov.get(c, 0) - e) ** 2 / e; df += 1
    return (chi - df) / math.sqrt(2 * df) if df > 0 else None, df, d

def scan_cost(E, H, Hset, ys, sq, p, h, Rs):
    a, b = E.a, E.b
    lg = math.log2(p); mulsq = 1.5 * lg
    ops_hash = ops_exp = 0.0; found = 0; verified = 0
    sols = []
    for R in Rs:
        X = R[0]; hit = False
        for x1 in H:
            ops_hash += 8 + mulsq
            ops_exp += 8 + mulsq
            c2 = (X - x1) ** 2 % p
            if c2 == 0: continue
            c1 = (-2 * X * X * x1 - 2 * X * (x1 * x1 + a) - 2 * a * x1 - 4 * b) % p
            c0 = (X * X * x1 * x1 - 2 * X * a * x1 - 4 * b * X + a * a - 4 * b * x1) % p
            disc = (c1 * c1 - 4 * c0 * c2) % p
            roots_y = sq.get(disc)
            if not roots_y: continue
            inv = pow(2 * c2, -1, p)
            for s in set(roots_y):
                x2 = (-c1 + s) * inv % p
                ops_exp += 1.5 * math.log2(h)
                if x2 in Hset and x2 in ys and x1 in ys:
                    P1 = (x1, ys[x1][0]); P2 = (x2, ys[x2][0])
                    ok = False
                    for Q in (E.add(P1, P2), E.add(P1, E.neg(P2))):
                        if Q is not None and Q[0] == X: ok = True
                    if ok: hit = True; verified += 1; sols.append((x1, x2))
        found += hit
    return ops_hash / len(Rs), ops_exp / len(Rs), found / len(Rs), verified, sols

def main():
    out = {'seed': MASTER, 'buckets': []}
    lines = []
    for k in (12, 14, 16, 18):
        rec = {'k': k, 'curves': []}
        for idx in range(3):
            rng = random.Random(f"{MASTER}-{k}-{idx}")
            p, h = find_prime(rng, k)
            g = subgroup_gen(rng, p, h)
            for cidx in range(2):
                E, ys, N, sq = build_curve(rng, p)
                Kx = len(ys) + 1
                H = [pow(g, i, p) for i in range(h)]
                Hset = set(H)
                nH = sum(len(ys[x]) for x in H if x in ys)
                fams = {}
                fams['F1_H'] = [x for x in H if x in ys]
                for ci in range(2):
                    a0 = rng.randrange(1, p)
                    fams[f'F1c_coset{ci}'] = [a0 * x % p for x in H if a0 * x % p in ys]
                fams['F4a_t2'] = pick_until([t * t % p for t in range(1, p)], ys, nH)
                fams['F4b_inv'] = pick_until([pow(t, -1, p) for t in range(1, p)], ys, nH)
                fams['SX'] = pick_until(range(p), ys, nH)
                xs_pts = list(ys)
                for ri in range(3):
                    rng.shuffle(xs_pts)
                    fams[f'RND{ri}'] = pick_until(xs_pts, ys, nH)
                res = {}
                for name, xs in fams.items():
                    V = points_of(xs, ys)
                    res[name] = measure(E, V, Kx, name)
                    if name == 'F1_H':
                        mult, _ = sumset(E, V)
                        zH = chi_class(p, h, [x for x in mult if x >= 0], ys)
                        zR = []
                        V2 = points_of(fams['RND0'], ys); m2, _ = sumset(E, V2)
                        zR.append(chi_class(p, h, [x for x in m2 if x >= 0], ys))
                        V3 = points_of(fams['RND1'], ys); m3, _ = sumset(E, V3)
                        zR.append(chi_class(p, h, [x for x in m3 if x >= 0], ys))
                        res['chi_class'] = {'z_H': zH[0], 'df': zH[1], 'classes': zH[2], 'z_RND_null': [z[0] for z in zR]}
                rnd = [res[f'RND{i}']['pi'] for i in range(3)]
                rnd_e = [res[f'RND{i}']['energy_ratio'] for i in range(3)]
                rpi = sum(rnd) / 3
                ratios = {nm: res[nm]['pi'] / rpi for nm in fams if not nm.startswith('RND')}
                nrat = {nm: res[nm]['n'] / nH for nm in fams}
                pn = {nm: (res[nm]['pi'] / rpi) / (nrat[nm] ** 2) for nm in fams if not nm.startswith('RND')}
                eratios = {nm: res[nm]['energy_ratio'] / (sum(rnd_e) / 3) for nm in fams if not nm.startswith('RND')}
                c = {'p': p, 'h': h, 'N': N, 'n_H': nH, 'analytic_pi_n2_over_2N': nH * nH / (2 * N),
                     'pi': {nm: res[nm]['pi'] for nm in fams}, 'pi_ratio_vs_RND': ratios, 'n_over_nH': nrat, 'pi_ratio_normalized_by_n2': pn,
                     'energy_ratio_vs_RND': eratios, 'chi_class': res['chi_class']}
                # Measurement 2 on first curve of first prime for each k
                if idx == 0 and cidx == 0:
                    pts = [(x, ys[x][0]) for x in rng.sample(list(ys), min(200, len(ys))) if ys[x][0] != 0]
                    oh, oe, fr, ver, sols = scan_cost(E, H, Hset, ys, sq, p, h, pts)
                    mult, _ = sumset(E, points_of(fams['F1_H'], ys))
                    agree = sum(1 for R in pts if R[0] in mult)
                    c['scan'] = {'n': nH, 'ops_per_R_hashmembership': oh, 'ops_per_R_expmembership': oe,
                                 'success_rate': fr, 'enum_coverage_on_same_R': agree / len(pts),
                                 'ops_per_found_relation_hash': oh / max(fr, 1e-9),
                                 'table_build_ops': nH * nH / 2, 'table_ops_per_R': 1,
                                 'ops_over_n': oh / nH, 'verified_solutions': ver}
                rec['curves'].append(c)
                print(k, p, h, N, nH, {a: round(b, 3) for a, b in pn.items()}, round(time.time() - T0, 1), flush=True)
        out['buckets'].append(rec)
    json.dump(out, open('results_20261103.json', 'w'), indent=1)

main()
