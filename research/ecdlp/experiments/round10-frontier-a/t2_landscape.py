"""T2: random-energy-model test of the k-landscape (statistical-mechanics analogy)."""
import sys, random, math
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def setup(seed, p0=20011):
    rnd = random.Random(seed); p = p0
    while True:
        p += 1
        if not is_prime(p): continue
        for _ in range(80):
            a = rnd.randrange(1, p); b = rnd.randrange(1, p)
            try: E = Curve(a, b, p)
            except ValueError: continue
            N = E.order()
            if is_prime(N) and N != p: break
        else: continue
        break
    while True:
        x = rnd.randrange(p); rhs = (x**3+a*x+b) % p
        ys = [y for y in range(p) if y*y % p == rhs]
        if ys and ys[0]: P = (x, ys[0]); break
    xs = []; R = None
    for k in range(N):
        xs.append(-1 if R is None else R[0]); R = E.add(R, P)
    return p, N, xs, rnd

def pearson(u, v):
    n = len(u); mu = sum(u)/n; mv = sum(v)/n
    su = sum((a-mu)**2 for a in u); sv = sum((b-mv)**2 for b in v)
    return sum((a-mu)*(b-mv) for a, b in zip(u, v)) / math.sqrt(su*sv)

if __name__ == '__main__':
    seed = int(sys.argv[1])
    p, N, xs, rnd = setup(seed)
    print(f'seed={seed} p={p} N={N} 1/sqrt(N)={N**-0.5:.4f}')
    cyc = lambda a, b: min((a-b) % p, (b-a) % p)
    ham = lambda a, b: bin(a ^ b).count('1')
    for name, d in [('cyclic|dx|', cyc), ('hamming(x)', ham)]:
        for delta in (1, 2, 3, 4, 8, 64):
            cs = []
            for _ in range(5):
                kq = rnd.randrange(1, N); xq = xs[kq]
                H = [d(xs[j], xq) if xs[j] >= 0 else 0 for j in range(N)]
                cs.append(pearson(H[:N-delta], H[delta:]))
            print(f'  {name} delta={delta}: mean corr over 5 Q = {sum(cs)/5:+.4f}  max|c|={max(abs(c) for c in cs):.4f}  (5/sqrtN={5*N**-0.5:.4f})')
    # annealing vs random sampling
    nb = N.bit_length(); budget = int(10*math.sqrt(N))
    def run_search(kind, kq):
        xq = xs[kq]; target = lambda k: xs[k] == xq or xs[(-k) % N] == xq
        if kind == 'random':
            for t in range(budget):
                if target(rnd.randrange(N)): return True
            return False
        # annealing on bits, energy cyclic distance (normalized), restarts when stuck
        evals = 0
        while evals < budget:
            k = rnd.randrange(N); E0 = cyc(xs[k], xq); T = p/8; evals += 1
            if E0 == 0: return True
            for step in range(60):
                k2 = k ^ (1 << rnd.randrange(nb))
                if k2 >= N: continue
                E2 = cyc(xs[k2], xq); evals += 1
                if E2 == 0: return True
                if E2 <= E0 or rnd.random() < math.exp(-(E2-E0)/max(T, 1e-9)):
                    k, E0 = k2, E2
                T *= 0.93
                if evals >= budget: break
        return False
    trials = 400
    qs = [rnd.randrange(1, N) for _ in range(trials)]
    for kind in ('random', 'anneal'):
        s = sum(run_search(kind, q) for q in qs)
        print(f'  {kind}: success {s}/{trials} at budget {budget} evals (= 10 sqrt(N); N={N}); random-sampling expectation ~{2*budget/N*trials:.1f}')
    print(f'  rho reference ~ 1.25 sqrt(N) = {1.25*math.sqrt(N):.0f} evals for success prob ~1/2')
