import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'round12-inventor-c'))
from lib12 import find_prime_order_curve
out = []
for bits in (16, 20, 24, 28, 32):
    for seed in (0, 1, 2):
        E, P, r = find_prime_order_curve(bits, seed)
        out.append(dict(bits=bits, seed=seed, p=E.p, a=E.a, b=E.b, r=r, Px=P[0], Py=P[1]))
        print(bits, seed, E.p, r, flush=True)
json.dump(out, open('curves.json', 'w'), indent=1)
