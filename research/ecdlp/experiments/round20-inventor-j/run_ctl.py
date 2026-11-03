import sys, json, math, random, time
sys.path.insert(0, '.')
from pipelines import *
what = sys.argv[1]
if what == 'rho':      # rho control: ops vs r
    res = []
    for bits in (12, 16, 20, 24, 28):
        for s in range(30 if bits < 28 else 15):
            inst = Inst(bits, s); k, c = rho(inst, random.Random(s)); assert k == inst.k
            res.append(dict(bits=bits, r=inst.r, ops=c))
        print(bits, sum(x['ops'] for x in res if x['bits'] == bits) / len([x for x in res if x['bits'] == bits]), flush=True)
    json.dump(res, open('out/rho.json', 'w'))
elif what == 'kang':   # kangaroo ops vs w
    res = []
    for lw in (8, 12, 16, 20, 24):
        w = 1 << lw
        for s in range(60 if lw < 24 else 30):
            inst = Inst(28 if lw > 20 else 28, s % 20)   # r ~ 2^27: interval inside
            rng = random.Random(1000 + s)
            lo = rng.randrange(0, inst.r - w); kk = lo + rng.randrange(0, w + 1)
            Q = inst.ops.mul(kk, inst.P); inst.ops.count = 0
            k, c = kangaroo(inst.ops, inst.P, Q, lo, w, rng, inst.r)
            res.append(dict(lw=lw, w=w, ok=(k == kk), ops=c))
        rr = [x for x in res if x['lw'] == lw]
        print(lw, sum(x['ops'] for x in rr) / len(rr), sum(x['ok'] for x in rr) / len(rr), flush=True)
    json.dump(res, open('out/kang.json', 'w'))
