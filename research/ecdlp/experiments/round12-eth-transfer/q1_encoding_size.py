"""E1: CNF size n(ell) of existing lab encodings of [k]P=Q (no solving), fit, extrapolation and ETH crossover test.
Usage: python3 q1_encoding_size.py   (seed 12121; deterministic)"""
import sys, os, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(EXP, 'lib')); sys.path.insert(0, os.path.join(EXP, 'round10-frontier-b'))
sys.path.insert(0, os.path.join(EXP, 'round11-frontier-d')); os.chdir(os.path.join(EXP, 'round11-frontier-d'))
from toyec import Curve, is_prime
import sat_ecdlp as S10
import sat_ladder as S11
from eth_params import f as eth_f, params as eth_params   # same directory
sys.path.insert(0, HERE)

def affine_instance(rng, ell):
    # prime-order curve with bitlength(r)=ell : p in [2^(ell-1), 2^ell) gives r ~ p (+-2 sqrt p); filter on exact bitlength
    while True:
        E, P, N, S = S10.find_instance(rng, ell)
        if N.bit_length() == ell: return E, P, N, S

def affine_size(ell, rng):
    E, P, N, S = affine_instance(rng, ell)
    k = rng.randrange(1, N); Q = E.mul(k, P)
    if Q is None: return None
    C, kb = S10.encode(E, P, Q, S, ell)     # may raise on exceptional values; then skip
    return dict(ell=ell, p=E.p, r=N, vars=C.n, clauses=len(C.cl))

def ladder_size(n, rng):
    inst = S11.gen_instance(rng, n)
    C, kb = S11.encode_ladder(inst, False)
    return dict(ell=n, p=inst['p'], r=inst['r'], vars=C.n, clauses=len(C.cl))

def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return a, my - a * mx

def fit_ci(rows, rng):
    xs = [math.log2(r['ell']) for r in rows]; ys = [math.log2(r['vars']) for r in rows]
    a, b = ols(xs, ys); bs = []
    for _ in range(2000):
        idx = [rng.randrange(len(rows)) for _ in rows]
        if len(set(xs[i] for i in idx)) < 2: continue
        bs.append(ols([xs[i] for i in idx], [ys[i] for i in idx])[0])
    bs.sort(); return a, b, bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))]

def main():
    rng = random.Random(12121); out = {}
    aff = []
    for ell in range(5, 17):
        for rep in range(3):
            for _ in range(20):
                try:
                    r = affine_size(ell, rng)
                except Exception as e:
                    r = None
                if r: aff.append(r); break
    lad = []
    for n in range(5, 13):
        for rep in range(3): lad.append(ladder_size(n, rng))
    out['affine_rows'] = aff; out['ladder_rows'] = lad
    frng = random.Random(7)
    for name, rows in (('affine', aff), ('ladder', lad)):
        a, b, lo, hi = fit_ci(rows, frng)
        out[name + '_fit'] = dict(exponent=a, ci95=[lo, hi], log2_c=b, c=2 ** b, n_points=len(rows))
    # extrapolation and crossover tests (C = 1: most favourable constant; polynomial factors dropped)
    ext = []
    for key in ('affine', 'ladder'):
        fit = out[key + '_fit']
        for ell in (64, 160, 256, 384, 521):
            N = fit['c'] * ell ** fit['exponent']
            lhs = N / math.sqrt(math.log(N))               # C=1 headline form n/sqrt(ln n)
            lam, nu, r, Q, R, ok, ff = eth_f(math.log2(N))
            ext.append(dict(encoding=key, ell=ell, n_vars=N, n_over_ell=N / ell,
                            headline_exponent_C1=lhs, rho_exponent=ell / 2,
                            headline_beats_rho=lhs < ell / 2,
                            sqrtln_n_over_2=math.sqrt(math.log(N)) / 2,
                            paper_params_hypotheses_ok=ok))
    out['extrapolation'] = ext
    # idealised best cases n = s*ell, s = 1,2,4 : need f(log2 n) < 1/(2 s)  (paper's explicit parameters)
    ideal = []
    for s in (1, 2, 4, 16):
        # least log2 ell s.t. hypotheses hold and n*f(log2 n) < ell/2 where n = s*ell
        lo_ = None; lg = 10.0
        while lg < 1e14:
            lam, nu, r, Q, R, ok, ff = eth_f(lg + math.log2(s))
            if ok and ff < 1.0 / (2 * s): lo_ = lg; break
            lg *= 1.002
        ideal.append(dict(s=s, least_log2_ell=lo_))
    out['idealised_n_equals_s_times_ell'] = ideal
    json.dump(out, open(os.path.join(HERE, 'out_q1.json'), 'w'), indent=1)
    for k in ('affine_fit', 'ladder_fit'): print(k, json.dumps(out[k]))
    for r in ext: print(json.dumps(r))
    print(json.dumps(ideal))
    print('affine_rows', [(r['ell'], r['vars']) for r in aff])
    print('ladder_rows', [(r['ell'], r['vars']) for r in lad])

if __name__ == '__main__':
    main()
