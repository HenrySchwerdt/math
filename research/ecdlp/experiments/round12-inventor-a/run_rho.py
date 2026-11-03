import json
from common import *
out = open(os.path.join(HERE, 'out_rho.jsonl'), 'w')
for b in SIZES:
    for line in open(os.path.join(HERE, f'instances_{b}.jsonl')):
        d = json.loads(line); d['P'] = tuple(d['P']); d['Q'] = tuple(d['Q'])
        k, n = rho_dp(d, rng_seed=d['seed'])
        E = Curve(d['a'], d['b'], d['p'])
        ok = k is not None and E.mul(k, d['P']) == d['Q'] and dlog_bsgs(E, d['P'], d['Q'], d['r']) == k
        out.write(json.dumps(dict(bits=b, seed=d['seed'], r=d['r'], adds=n, correct=ok)) + '\n'); out.flush()
        print(b, d['seed'], ok, n, flush=True)
