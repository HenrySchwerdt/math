import sys, json, os
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/round12-inventor-c')
sys.path.insert(0, '/home/user/math/research/ecdlp/experiments/lib')
from lib12 import find_prime_order_curve
out = []
for bits in (12, 16, 20, 24, 28):
    for seed in range(100, 112):   # 0-7 train, 8-11 held-out
        E, P, r = find_prime_order_curve(bits, seed)
        out.append(dict(bits=bits, seed=seed, p=E.p, a=E.a, b=E.b, r=r, Px=P[0], Py=P[1], role='train' if seed < 108 else 'heldout'))
    print(bits, flush=True)
json.dump(out, open('curves.json', 'w'), indent=1)
