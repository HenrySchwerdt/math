"""T2c (post-hoc diagnosis of the T2 spectral flags on S and g; labelled post-hoc): proper null = cumulative sum of SHUFFLED d1 (same increment multiset)."""
import numpy as np, glob, json
rng = np.random.default_rng(5)
def mx(zz, n): return np.abs(np.fft.fft(zz))[1:].max() / np.sqrt(n)
for f in sorted(glob.glob('dump_*.npz')):
    D = np.load(f); p = int(D['p']); d1 = D['d1']; S = D['S']; g = D['g']; n = len(d1)
    # d1 as centred integers
    c = np.where(d1 > p // 2, d1 - p, d1)
    stat = lambda S_: mx(np.exp(2j * np.pi * (S_ % p) / p), n)
    # S here is sum_{i<k} c3 mod p, k=1..N-1 -> S_k ; control: cumsum of shuffled d1 prefix with same indexing
    obs_S = stat(S)
    null = []
    for _ in range(200):
        sh = rng.permutation(np.concatenate([[0], d1]))      # d1[0]=0 term is c(O); keep as first element convention approx
        null.append(stat(np.cumsum(sh)[1:n + 1] % p))
    null = np.array(null)
    # increment distribution: fraction within +-p/10 of 0, mean of centred
    out = dict(file=f, p=p, n=n, d1_mean_centered=round(float(c.mean()), 2), d1_std_centered=round(float(c.std()), 2), uniform_std=round(p / 12 ** 0.5, 2),
               frac_abs_lt_p10=round(float((np.abs(c) < p / 10).mean()), 3), frac_expected_uniform=0.2,
               S_stat=round(float(obs_S), 3), shufcum_null_mean=round(float(null.mean()), 3), shufcum_null_sd=round(float(null.std()), 3),
               z_vs_shufcum=round(float((obs_S - null.mean()) / null.std()), 2))
    # lag-1 autocorrelation of centred d1 and of d1 vs d1 shifted (order structure)
    out['d1_lag1_corr'] = round(float(np.corrcoef(c[:-1], c[1:])[0, 1]), 4); out['d1_lag2_corr'] = round(float(np.corrcoef(c[:-2], c[2:])[0, 1]), 4)
    # DFT of d1 itself on the orbit order (order structure of the increments) vs shuffled
    zd = np.exp(2j * np.pi * d1 / p); o = mx(zd, n); nl = np.array([mx(rng.permutation(zd), n) for _ in range(200)])
    out['d1_spec_z'] = round(float((o - nl.mean()) / nl.std()), 2)
    print(json.dumps(out))
