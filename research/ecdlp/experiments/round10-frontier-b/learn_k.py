"""F-B2: can a learner predict bits of k from (x(kP), y(kP)) on held-out k? Seeded, numpy only."""
import sys, json, random, math
import numpy as np
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime
from sat_ecdlp import find_instance

def feats(p, pts):
    m = p.bit_length(); X = np.array([q[0] for q in pts]); Y = np.array([q[1] for q in pts])
    B = [((X >> i) & 1) for i in range(m)] + [((Y >> i) & 1) for i in range(m)]
    F = [np.cos(2 * np.pi * j * X / p) for j in range(1, 9)] + [np.sin(2 * np.pi * j * X / p) for j in range(1, 9)] \
      + [np.cos(2 * np.pi * j * Y / p) for j in range(1, 9)] + [np.sin(2 * np.pi * j * Y / p) for j in range(1, 9)]
    return np.column_stack(B + F).astype(np.float64)

def logreg(Xtr, ytr, Xte, rng, it=300, lr=0.5, l2=1e-3):
    w = np.zeros(Xtr.shape[1]); b = 0.0
    for _ in range(it):
        z = Xtr @ w + b; pr = 1 / (1 + np.exp(-z)); g = pr - ytr
        w -= lr * (Xtr.T @ g / len(ytr) + l2 * w); b -= lr * g.mean()
    return (Xte @ w + b)

def mlp(Xtr, ytr, Xte, rng, h=64, ep=300, lr=0.05, l2=1e-4):
    d = Xtr.shape[1]
    W1 = rng.normal(0, 1 / math.sqrt(d), (d, h)); b1 = np.zeros(h)
    W2 = rng.normal(0, 1 / math.sqrt(h), h); b2 = 0.0
    n = len(ytr)
    for e in range(ep):
        idx = rng.permutation(n)
        for s in range(0, n, 128):
            i = idx[s:s + 128]; A = np.tanh(Xtr[i] @ W1 + b1); z = A @ W2 + b2
            pr = 1 / (1 + np.exp(-z)); g = (pr - ytr[i]) / len(i)
            gA = np.outer(g, W2) * (1 - A * A)
            W2 -= lr * (A.T @ g + l2 * W2); b2 -= lr * g.sum()
            W1 -= lr * (Xtr[i].T @ gA + l2 * W1); b1 -= lr * gA.sum(0)
    return np.tanh(Xte @ W1 + b1) @ W2 + b2

def knn_label(Xtr_raw, ytr, Xte_raw, kk=15):  # nearest neighbours in coordinate space (circular distance on x,y)
    p = None
    out = []
    return out

def acc_ci(correct, n):
    a = correct / n; se = math.sqrt(0.25 / n); return a, 1.96 * se

def experiment(kind, p, E, P, r, seed, nbits=None):
    rng = np.random.default_rng(seed)
    ks = np.arange(1, r)
    if kind == 'ecdlp':
        pts = {int(k): E.mul(int(k), P) for k in ks}
    elif kind == 'control_identity':   # leak control: coordinates = (k, k') trivially encoding k
        pts = {int(k): (int(k) % p, int(k) * 7 % p) for k in ks}
    elif kind == 'control_xparity':     # planted dependency of label on ecdlp coordinates handled below
        pts = {int(k): E.mul(int(k), P) for k in ks}
    perm = rng.permutation(len(ks)); ntr = int(0.7 * len(ks))
    tr, te = ks[perm[:ntr]], ks[perm[ntr:]]
    Ptr = [pts[int(k)] for k in tr]; Pte = [pts[int(k)] for k in te]
    Xtr, Xte = feats(p, Ptr), feats(p, Pte)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9; Xtr = (Xtr - mu) / sd; Xte = (Xte - mu) / sd
    labels = {}
    nb = r.bit_length()
    for j in range(nb): labels['bit%d' % j] = lambda k, j=j: (k >> j) & 1
    labels['k<r/2'] = lambda k: int(k < r / 2)
    labels['k%3==0'] = lambda k: int(k % 3 == 0)
    labels['lowerhalf_of_canon'] = lambda k: int(min(k, r - k) < r / 4)  # sign-invariant label (x determines it)
    if kind == 'control_xparity':
        labels = {'xbit0': None}
    res = {}
    for name, f in labels.items():
        if kind == 'control_xparity':
            ytr = np.array([(q[0] & 1) for q in Ptr], float); yte = np.array([(q[0] & 1) for q in Pte], float)
        else:
            ytr = np.array([f(int(k)) for k in tr], float); yte = np.array([f(int(k)) for k in te], float)
        base = max(yte.mean(), 1 - yte.mean())
        row = {'majority_baseline': round(float(base), 4)}
        for mname, mf in (('logreg', logreg), ('mlp', mlp)):
            sc = mf(Xtr, ytr, Xte, rng)
            pred = (sc > 0).astype(float); a = float((pred == yte).mean())
            row[mname] = round(a, 4)
        row['n_test'] = len(yte)
        res[name] = row
    return res

if __name__ == '__main__':
    seed = int(sys.argv[1]); m = int(sys.argv[2]); kinds = sys.argv[3].split(',')
    rng = random.Random(seed)
    E, P, r, S = find_instance(rng, m)
    out = {'seed': seed, 'p': E.p, 'a': E.a, 'b': E.b, 'r': r}
    for kind in kinds:
        out[kind] = experiment(kind, E.p, E, P, r, seed)
    print(json.dumps(out))
