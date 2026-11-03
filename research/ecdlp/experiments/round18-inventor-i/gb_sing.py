"""Usage: gb_sing.py M D -- same system as gb.py, solved with Singular 4.4.1 std (grevlex, char p) via subprocess. Prints one JSON line.
SINGULAR env var = path to the Singular binary (pip wheel passagemath-singular 10.8.13, sage_wheels/bin/Singular)."""
import sys, json, time, random, os, subprocess, re
from sympy import symbols, expand
from lib18 import *
M, D = int(sys.argv[1]), int(sys.argv[2]); SG = os.environ['SINGULAR']
rng = random.Random(1800 + 7 * D)
while True:
    p = (rng.randrange(D ** 5 // 2, D ** 5) // D) * D + 1
    if is_prime(p): break
assert p < 2 ** 31
a, b = rng.randrange(1, p), rng.randrange(1, p); E = EC(a, b, p)
fac = [q for q in range(2, D + 1) if D % q == 0 and is_prime(q)]
while True:
    zeta = pow(rng.randrange(2, p), (p - 1) // D, p)
    if all(pow(zeta, D // q, p) != 1 for q in fac): break
while True:
    g = rng.randrange(1, p); xs = [g * pow(zeta, i, p) % p for i in range(D)]
    cls = [(x, sqrt_mod(x ** 3 + a * x + b, p)) for x in xs]; cls = [c for c in cls if c[1]]
    if len(cls) >= 2: break
R = None
for q in [rng.choice(cls) for _ in range(M)]: R = E.add(R, q)
if R is None: print(json.dumps(dict(skip=True))); sys.exit()
cc = pow(xs[0], D, p)
X = symbols('x1:%d' % (M + 1)); U, T = symbols('U T')
def S3s(u, v, w): return expand((u - v) ** 2 * w ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w + (u * v - a) ** 2 - 4 * b * (u + v))
if M == 2: F = [S3s(X[0], X[1], R[0])]; V = list(X)
elif M == 3: F = [S3s(X[0], X[1], U), S3s(U, X[2], R[0])]; V = list(X) + [U]
else: F = [S3s(X[0], X[1], U), S3s(X[2], X[3], T), S3s(U, T, R[0])]; V = list(X) + [U, T]
F += [x ** D - cc for x in X]
f2s = lambda e: str(e).replace('**', '^')
scr = f"ring r={p},({','.join(map(str, V))}),dp;\nideal I={','.join(f2s(f) for f in F)};\nsystem(\"--ticks-per-sec\",1000);\nint t=rtimer;\nideal G=std(I);\nint dt=rtimer-t;\nprint(\"RES \"+string(dt)+\" \"+string(size(G))+\" \"+string(vdim(G))+\" \"+string(deg(G[size(G)])));\nquit;\n"
t0 = time.time()
r = subprocess.run([SG, '-q'], input=scr, capture_output=True, text=True)
m = re.search(r'RES (\d+) (\d+) (-?\d+) (\d+)', r.stdout)
print(json.dumps(dict(m=M, d=D, p=p, nclasses=len(cls), sing_ms=int(m.group(1)), basis_size=int(m.group(2)), vdim=int(m.group(3)), wall_s=time.time() - t0)), flush=True)
