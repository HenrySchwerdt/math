"""Held-out evaluation per PROTOCOL.md. Usage: evaluate.py TAG...   (TAG like random_s0 or 'baselines')
Writes out_eval_<TAG>.json. Champions' test curves (seeds >=200) first touched here."""
import sys, os, json, math, random, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import *
HERE = os.path.dirname(os.path.abspath(__file__))
TESTA = [(tb, sd) for tb in (13, 14, 15, 16) for sd in (200, 201, 202)]
TESTB = [(tb, sd) for tb in (10, 11, 12) for sd in (210, 211, 212)]
NINST = 60

def measure(prog, spec):
    """per size: list of (cost, solved, r) over all instances"""
    res = {}
    for tb, sd in spec:
        c = make_curve(tb, sd)
        for k, s in instances(c, NINST, 5):
            out, cost, _ = run(prog, c, k, s)
            res.setdefault(tb, []).append((cost, out == k, c['r']))
    return res

def slope(sizes, means_r, means_c):
    xs = [math.log(x) for x in means_r]; ys = [math.log(y) for y in means_c]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)

def summarize(res, B=2000):
    sizes = sorted(res)
    mr = [sum(t[2] for t in res[s]) / len(res[s]) for s in sizes]
    mc = [sum(t[0] for t in res[s]) / len(res[s]) for s in sizes]
    succ = {s: sum(t[1] for t in res[s]) / len(res[s]) for s in sizes}
    beta = slope(sizes, mr, mc)
    rng = random.Random(12345); bs = []
    for _ in range(B):
        mcb = []
        for s in sizes:
            L = res[s]; mcb.append(sum(L[rng.randrange(len(L))][0] for _ in L) / len(L))
        bs.append(slope(sizes, mr, mcb))
    bs.sort()
    return dict(sizes=sizes, mean_r=mr, mean_cost=mc, cost_over_sqrt_r=[c / math.sqrt(r) for c, r in zip(mc, mr)],
                success=succ, beta=beta, ci95=[bs[int(.025 * B)], bs[int(.975 * B) - 1]], ci99=[bs[int(.005 * B)], bs[int(.995 * B) - 1]])

def main():
    h = hashlib.sha256(open(os.path.join(HERE, 'PROTOCOL.md'), 'rb').read()).hexdigest()
    assert h == open(os.path.join(HERE, 'PROTOCOL.sha256')).read().split()[0]
    for tag in sys.argv[1:]:
        if tag == 'baselines':
            progs = {n: f() for n, f in BASELINES.items()}
        else:
            ch = json.load(open(os.path.join(HERE, f'out_evolve_{tag}.json')))['champions'][0]['prog']
            progs = {tag: ([tuple(x) for x in ch[0]], [tuple(x) for x in ch[1]])}
        out = {}
        for n, p in progs.items():
            a = summarize(measure(p, TESTA)); b = summarize(measure(p, TESTB), B=500)
            ok_succ = all(v >= 0.9 for v in a['success'].values())
            out[n] = dict(prog=p, testA=a, testB=b, crit1_success_ge_0p9=ok_succ, crit2_upper99_lt_0p5=a['ci99'][1] < 0.5)
            print(n, 'A beta %.3f ci99 [%.3f,%.3f]' % (a['beta'], *a['ci99']), 'succ', {k: round(v, 2) for k, v in a['success'].items()},
                  'c/sqrt', [round(x, 2) for x in a['cost_over_sqrt_r']], '| B beta %.3f succ' % b['beta'], {k: round(v, 2) for k, v in b['success'].items()}, flush=True)
        json.dump(dict(protocol_sha256=h, results=out), open(os.path.join(HERE, f'out_eval_{tag}.json'), 'w'))
main()
