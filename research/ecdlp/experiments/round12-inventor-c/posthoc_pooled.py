"""POST-HOC exploratory (not pre-registered): pooled paired ratio ref/C1b over sizes 28..44, normalising each trial by sqrt(n);
and pooled ref ops/sqrt(n). Bootstrap over (size, trial) pairs, 4000 resamples, seed 5."""
import json, glob, random, statistics as st, math
ref = {(r['bits'], r['trial']): r for r in map(json.loads, open('out_ref.jsonl'))}
nw = {(r['bits'], r['trial']): r for r in (json.loads(l) for f in glob.glob('out_negw_*.jsonl') for l in open(f))}
for lo in (24, 28):
    keys = [k for k in nw if k in ref and k[0] >= lo]
    A = [ref[k]['ops'] / ref[k]['n']**.5 for k in keys]; B = [nw[k]['ops'] / nw[k]['n']**.5 for k in keys]
    rng = random.Random(5); rs = []
    for _ in range(4000):
        idx = [rng.randrange(len(keys)) for _ in keys]
        rs.append(st.mean(A[i] for i in idx) / st.mean(B[i] for i in idx))
    rs.sort()
    print(f'sizes >= {lo} bits, {len(keys)} paired trials: pooled ref/sqrt(n) = {st.mean(A):.3f}, C1b/sqrt(n) = {st.mean(B):.3f}, ratio = {st.mean(A)/st.mean(B):.3f} (95% CI {rs[100]:.3f}, {rs[3900]:.3f}); theory sqrt2 = 1.414')
