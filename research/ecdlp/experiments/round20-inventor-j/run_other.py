import sys, json, math, random, time
sys.path.insert(0, '.')
from pipelines import *
mode = sys.argv[1]
if mode == 'p0':
    out = []
    for bits in (12, 16, 20, 24):
        for eps in (0.5, 0.2, 0.1, 0.05):
            n = 200; ok = 0; ops = 0
            for s in range(n):
                inst = Inst(bits, s % 25); inst.rng.seed(s)
                kk = random.Random(s).randrange(1, inst.r); inst.k = kk; inst.Q = inst.ops.mul(kk, inst.P); inst.ops.count = 0; inst.seed = s
                lo, q = p0_binary(inst, eps); ok += (lo == kk or lo + 1 == kk or lo == kk - 0); ops += inst.ops.count
            out.append(dict(bits=bits, eps=eps, ok=ok, n=n, mean_ops=ops / n, pred=(0.5 + eps) ** math.log2(inst.r))); print(out[-1], flush=True)
    json.dump(out, open('out/p0.json', 'w'))
elif mode == 'p2':
    out = []
    for bits in (16, 20, 24, 28):
        for rr in (0.1, 0.02, 0.004):
            res = [p2_interval_kangaroo(Inst(bits, s), rr, random.Random(s)) for s in range(30)]
            out.append(dict(bits=bits, rho_rel=rr, ok=sum(x['ok'] for x in res), n=30, mean_ops=sum(x['ops'] for x in res) / 30, mean_w=sum(x['w'] for x in res) / 30, fallbacks=sum(x['fallback'] for x in res)))
            print(out[-1], flush=True)
    json.dump(out, open('out/p2.json', 'w'))
elif mode == 'p3':
    out = []
    for bits in (16, 20, 24, 28):
        for rr in (0.25, 0.1, 0.02):
            for sa in (True, False):
                res = [p3_iterative(Inst(bits, s), rr, sa, random.Random(s)) for s in range(30)]
                out.append(dict(bits=bits, rho_rel=rr, scale_aware=sa, ok=sum(x['ok'] for x in res), n=30, mean_ops=sum(x['ops'] for x in res) / 30,
                                mean_ops_feat=sum(x.get('ops_feat', x['ops']) for x in res) / 30, widths_example=res[0]['widths']))
                print(out[-1], flush=True)
    json.dump(out, open('out/p3.json', 'w'))
elif mode == 'p4':
    out = []
    for delta in (0.5, 0.25, 0.1):
        for nu in (1.0, 2.0):
            for bits in (16, 20, 24):
                res = [p4_close_scan(Inst(bits, s), delta, nu, random.Random(s)) for s in range(12)]
                out.append(dict(bits=bits, delta=delta, nu=nu, ok=sum(x['ok'] for x in res), n=12, mean_ops=sum(x['ops'] for x in res) / 12,
                                mean_ops_feat=sum(x.get('ops_feat', x['ops']) for x in res) / 12, widths=res[0]['widths']))
                print(out[-1], flush=True)
    json.dump(out, open('out/p4.json', 'w'))
elif mode == 'p4c':
    out = []
    for delta in (0.5, 0.2, 0.1):
        for nu in (1.0, 2.0, 4.0):
            for bits in (16, 20, 24, 28):
                res = [p4_close_scan(Inst(bits, s), delta, nu, random.Random(s)) for s in range(12)]
                out.append(dict(bits=bits, delta=delta, nu=nu, ok=sum(x['ok'] for x in res), n=12, mean_ops=sum(x['ops'] for x in res) / 12,
                                mean_ops_feat=sum(x.get('ops_feat', x['ops']) for x in res) / 12, widths=res[0]['widths']))
                print(out[-1], flush=True)
    json.dump(out, open('out/p4c.json', 'w'))
elif mode == 'p4b':
    out = []
    for delta in (0.2, 0.1):
        for nu in (4.0, 8.0, 16.0):
            bits = 20
            res = [p4_close_scan(Inst(bits, s), delta, nu, random.Random(s)) for s in range(12)]
            out.append(dict(bits=bits, delta=delta, nu=nu, ok=sum(x['ok'] for x in res), n=12, mean_ops=sum(x['ops'] for x in res) / 12,
                            mean_ops_feat=sum(x.get('ops_feat', x['ops']) for x in res) / 12, widths=res[0]['widths']))
            print(out[-1], flush=True)
    json.dump(out, open('out/p4b.json', 'w'))
elif mode == 'p3b':
    out = []
    for bits in (16, 20, 24, 28):
        for rr in (0.1, 0.02):
            res = [p3_iterative(Inst(bits, s), rr, True, random.Random(s), z=4.0) for s in range(30)]
            out.append(dict(bits=bits, rho_rel=rr, z=4.0, ok=sum(x['ok'] for x in res), n=30, mean_ops=sum(x['ops'] for x in res) / 30,
                            mean_ops_feat=sum(x.get('ops_feat', x['ops']) for x in res) / 30, widths_example=res[0]['widths']))
            print(out[-1], flush=True)
    json.dump(out, open('out/p3b.json', 'w'))
