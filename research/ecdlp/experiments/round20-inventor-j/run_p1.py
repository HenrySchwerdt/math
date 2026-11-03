import sys, json, math, random, time
sys.path.insert(0, '.')
from pipelines import *
mode = sys.argv[1]
if mode == 'calib':
    out = []
    for kappa in (2.0, 3.0):
        for nu in (0.5, 1, 1.5, 2, 3, 4):
            ok = 0; n = 30; ops = []
            for s in range(n):
                inst = Inst(20, 100 + s); res = p1_run(inst, 0.1, nu, kappa, random.Random(s)); ok += res['ok']; ops.append(res['ops'])
            out.append(dict(kappa=kappa, nu=nu, ok=ok, n=n, mean_ops=sum(ops) / n)); print(out[-1], flush=True)
    json.dump(out, open('out/p1_calib.json', 'w'))
elif mode == 'main':
    nu = float(sys.argv[2]); kappa = float(sys.argv[3]); eps = float(sys.argv[4]); res = []
    for bits in ((12, 16, 20, 24, 28) if len(sys.argv) < 6 else (int(sys.argv[5]),)):
        n = 20 if eps >= 0.1 else 8
        for s in range(n):
            inst = Inst(bits, s); t = time.time(); rr = p1_run(inst, eps, nu, kappa, random.Random(s)); rr.update(bits=bits, r=inst.r, eps=eps, secs=time.time() - t)
            res.append(rr)
        rows = [x for x in res if x['bits'] == bits]
        print(bits, eps, sum(x['ok'] for x in rows), len(rows), sum(x['ops'] for x in rows) / len(rows), sum(x['q'] for x in rows) / len(rows), rows[0]['widths'], flush=True)
    json.dump(res, open(f'out/p1_main_{eps}' + ('' if len(sys.argv) < 6 else '_b' + sys.argv[5]) + '.json', 'w'))
