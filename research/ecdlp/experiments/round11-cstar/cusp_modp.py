"""For primes p > 2N: is c_{N-1}(0) (cusp nodes 1/k^2; values k and k^2) nonzero mod p?
Lift argument (Theorem D) applies exactly to (p,N) pairs where it is nonzero. Stdlib, deterministic."""
def isprime(n):
    return n > 1 and all(n % q for q in range(2, int(n**0.5)+1))
def newton_mod(nodes, vals, p):
    c = list(vals); out = [c[0]]
    for lvl in range(1, len(nodes)):
        c = [(c[i+1]-c[i]) * pow(nodes[i+lvl]-nodes[i], -1, p) % p for i in range(len(c)-1)]
        out.append(c[0])
    return out
bad = []; tot = 0
for p in [q for q in range(5, 400) if isprime(q)]:
    for N in range(3, (p-1)//2 + 1):
        nodes = [pow(k*k, -1, p) for k in range(1, N+1)]
        c = newton_mod(nodes, list(range(1, N+1)), p)
        tot += 1
        if c[N-1] == 0: bad.append((p, N))
        c2 = newton_mod(nodes, [k*k % p for k in range(1, N+1)], p)
        assert all(c2[j] != 0 for j in range(N))
print("pairs (p,N), 3<=N<=(p-1)/2, p<400:", tot, " with c_{N-1}(0)=0 mod p (target k):", len(bad))
print("fraction", len(bad)/tot, " (random model sum 1/p ~", sum(1/p for p,N in [(p,N) for p in range(5,400) if isprime(p) for N in range(3,(p-1)//2+1)])/tot, ")")
print("bad pairs with N<=12:", [b for b in bad if b[1] <= 12])
print("bad pairs with N=(p-1)/2:", [b for b in bad if b[1] == (b[0]-1)//2])
print("target k^2: c_j(0) != 0 mod p for all j < N, all pairs: True (asserted)")
