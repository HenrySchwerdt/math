"""T1: do field-additive / field-multiplicative coincidences of x(jP) track index relations?"""
import sys, random
sys.path.insert(0, '../lib')
from toyec import Curve, is_prime

def nextprime(n):
    while not is_prime(n): n += 1
    return n

def seq_curve(p, rnd, M):
    while True:
        a = rnd.randrange(1, p); b = rnd.randrange(1, p)
        try: E = Curve(a, b, p)
        except ValueError: continue
        while True:
            x = rnd.randrange(p); rhs = (x**3+a*x+b) % p
            if pow(rhs, (p-1)//2, p) == 1 and p % 4 == 3:
                y = pow(rhs, (p+1)//4, p)
                if y: break
        P = (x, y); xs = [None]; R = None
        for j in range(1, M+1):
            R = E.add(R, P)
            if R is None: break
            xs.append(R[0])
        else:
            return xs

def stats(xs, p, M):
    """returns dict of counts: A_total, A_Iplus, Mu_total, Mu_Iplus, (also index multiplicative)."""
    out = {}
    for name in ('A', 'M'):
        d = {}
        for a in range(1, M+1):
            xa = xs[a]
            for b in range(a, M+1):
                v = (xa + xs[b]) % p if name == 'A' else xa*xs[b] % p
                d.setdefault(v, []).append((a, b))
        tot = ip = im = 0
        for lst in d.values():
            L = len(lst)
            if L < 2: continue
            for i in range(L):
                a, b = lst[i]
                for j in range(i+1, L):
                    c, e = lst[j]
                    tot += 1
                    if a+b == c+e: ip += 1
                    if a*b == c*e: im += 1
        out[name] = (tot, ip, im)
    return out

def fmt(o):
    return ' '.join(f"{k}:tot={v[0]},I+={v[1]},I*={v[2]}" for k, v in o.items())

if __name__ == '__main__':
    seed = int(sys.argv[1]); M = int(sys.argv[2]); p = nextprime(1 << 20)
    while p % 4 != 3: p = nextprime(p+1)
    rnd = random.Random(seed)
    xs = seq_curve(p, rnd, M)
    print(f'p={p} M={M} seed={seed}')
    real = stats(xs, p, M)
    print('REAL ', fmt(real), flush=True)
    nulls = {k: [[], [], []] for k in 'AM'}
    for t in range(12):
        perm = xs[1:]; rnd.shuffle(perm); ys = [None]+perm
        o = stats(ys, p, M)
        for k in 'AM':
            for i in range(3): nulls[k][i].append(o[k][i])
    import statistics as st
    for k in 'AM':
        for i, nm in enumerate(['tot', 'I+', 'I*']):
            mu = st.mean(nulls[k][i]); sd = st.pstdev(nulls[k][i]) or 1.0
            sd = max(sd, mu**0.5)  # Poisson floor
            print(f'{k} {nm}: real={real[k][i]} null_mean={mu:.1f} null_sd(floor Poisson)={sd:.1f} z={(real[k][i]-mu)/sd:.2f}')
    # positive controls
    for nm, f in [('linear c*j', lambda j: 12345*j % p), ('geometric 7^j', lambda j: pow(7, j, p))]:
        ys = [None]+[f(j) for j in range(1, M+1)]
        o = stats(ys, p, M)
        print('CTRL', nm, fmt(o))
