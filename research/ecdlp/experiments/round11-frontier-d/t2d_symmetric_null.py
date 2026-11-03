"""T2d (post-hoc, explains the T2 spectral flags): g is odd, g((N-k)P) = -g(kP) (lift l(-R) = -l(R)), hence S_{N-k} = g(P) - S_k.
Null respecting this symmetry: uniform odd random g', S'_k = (k g(P) - g'_k)/N mod p. Compare max-DFT statistics of e(g/p), e(S/p)."""
import numpy as np, glob, json
rng = np.random.default_rng(5)
def mx(v, p): n = len(v); return np.abs(np.fft.fft(np.exp(2j * np.pi * v / p)))[1:].max() / np.sqrt(n)
for f in sorted(glob.glob('dump_*.npz')):
    D = np.load(f); p = int(D['p']); N = int(D['N']); g = D['g'].astype(np.int64); S = D['S'].astype(np.int64); n = N - 1
    gP = int(g[0]); Ninv = pow(N, -1, p); ks = np.arange(1, N, dtype=np.int64)
    odd_ok = bool(np.all((g + g[::-1]) % p == 0)); S_ok = bool(np.all((S + S[::-1] - gP) % p == 0)); form_ok = bool(np.all((ks * gP - N * S - g) % p == 0))
    sg, sS = [], []
    for _ in range(200):
        h = rng.integers(0, p, size=n // 2); gp = np.zeros(n, dtype=np.int64)
        gp[:n // 2] = h; gp[n - n // 2:] = (-h[::-1]) % p       # odd symmetry: index k and N-k (0-based k-1, N-k-1)
        if n % 2: gp[n // 2] = 0
        Sp = ((ks * gP - gp) % p) * Ninv % p
        sg.append(mx(gp, p)); sS.append(mx(Sp, p))
    og, oS = mx(g, p), mx(S, p)
    print(json.dumps(dict(file=f, p=p, odd_symmetry_holds=odd_ok, S_reflection_holds=S_ok, formula_holds=form_ok,
        g_stat=round(float(og), 3), g_null_mean=round(float(np.mean(sg)), 3), g_null_sd=round(float(np.std(sg)), 3), g_z=round(float((og - np.mean(sg)) / np.std(sg)), 2),
        S_stat=round(float(oS), 3), S_null_mean=round(float(np.mean(sS)), 3), S_null_sd=round(float(np.std(sS)), 3), S_z=round(float((oS - np.mean(sS)) / np.std(sS)), 2))))
