"""Frozen analysis per PROTOCOL.md. Prints Markdown tables. Bootstrap: 4000 resamples, seed 12345."""
import json, math, random, statistics as st, sys, collections
def load(f):
    try: return [json.loads(l) for l in open(f)]
    except FileNotFoundError: return []
def groupby(rows, key):
    d = collections.defaultdict(list)
    for r in rows: d[key(r)].append(r)
    return d
def fit(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    sxx = sum((x-mx)**2 for x in xs)
    e = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sxx
    return e, my - e*mx
def boot_fit(groups, B=4000, seed=12345):
    """groups: {x: [values]}; returns (e, lo, hi) of slope of log2(mean) vs x (x = log2 n)."""
    rng = random.Random(seed)
    xs = sorted(groups)
    e0, _ = fit(xs, [math.log2(st.mean(groups[x])) for x in xs])
    es = []
    for _ in range(B):
        ys = [math.log2(st.mean(rng.choices(groups[x], k=len(groups[x])))) for x in xs]
        es.append(fit(xs, ys)[0])
    es.sort()
    return e0, es[int(0.025*B)], es[int(0.975*B)]
def boot_ratio(a, b, B=4000, seed=7):
    """paired ratio mean(a)/mean(b), 95% CI; a,b lists aligned by trial index."""
    rng = random.Random(seed); n = len(a); rs = []
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        rs.append(st.mean(a[i] for i in idx)/st.mean(b[i] for i in idx))
    rs.sort()
    return st.mean(a)/st.mean(b), rs[int(0.025*B)], rs[int(0.975*B)]
def L2(n): return math.log2(n)

def main():
    ref, neg = load('out_ref.jsonl'), load('out_neg.jsonl')
    import glob
    negw = [json.loads(l) for f in sorted(glob.glob('out_negw_*.jsonl')) for l in open(f)]
    print('## Single-instance: reference rho vs C1 (frozen) and C1b (post-hoc amendment)\n')
    for name, rows in (('ref', ref), ('C1', neg), ('C1b', negw)):
        bad = [r for r in rows if not r['ok']]
        print(f'- {name}: {len(rows)} runs, incorrect outputs: {len(bad)}')
    gr, gn, gw = (groupby(x, lambda r: r['bits']) for x in (ref, neg, negw))
    def table(gc, label):
        print(f'\n| bits | n | trials | ref mean ops | ref/sqrt(n) | {label} mean ops | {label}/sqrt(n) | ratio ref/{label} (95% CI) | capped walks/run |\n|---|---|---|---|---|---|---|---|---|')
        for b in sorted(gr):
            if b not in gc or len(gc[b]) < len(gr[b]): 
                print(f'| {b} | {gr[b][0]["n"]} | - | {st.mean(r["ops"] for r in gr[b]):.0f} | {st.mean(r["ops"] for r in gr[b])/gr[b][0]["n"]**.5:.3f} | not completed (censored) | | | |'); continue
            a = [r['ops'] for r in sorted(gr[b], key=lambda r: r['trial'])]; c = [r['ops'] for r in sorted(gc[b], key=lambda r: r['trial'])]
            n = gr[b][0]['n']; R = boot_ratio(a, c)
            cap = st.mean(r['stats']['capped'] for r in gc[b])
            print(f'| {b} | {n} | {len(a)} | {st.mean(a):.0f} | {st.mean(a)/n**.5:.3f} | {st.mean(c):.0f} | {st.mean(c)/n**.5:.3f} | {R[0]:.3f} ({R[1]:.3f}, {R[2]:.3f}) | {cap:.2f} |')
    table(gn, 'C1'); table(gw, 'C1b')
    def fits(name, g, sizes):
        G = {L2(g[b][0]['n']): [r['ops'] for r in g[b]] for b in sizes}
        e, lo, hi = boot_fit(G); print(f'Fitted exponent {name} (sizes {sorted(sizes)}): ops ~ n^e, e = {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
    print()
    comm = [b for b in gn if len(gn[b]) == len(gr[b])]
    fits('ref', gr, comm); fits('C1', gn, comm)
    fits('ref', gr, list(gr)); fits('C1b', gw, [b for b in gw if len(gw[b]) == len(gr[b])])
    for name, g in (('C1', gn), ('C1b', gw)):
        gc = [r['stats'] for rows in g.values() for r in rows]
        print(f'{name} cycle statistics (sums over runs): repeats@2 %d, repeats@other %d, capped-walks %d' % (sum(s["cycle2"] for s in gc), sum(s["cycle4"] for s in gc), sum(s["capped"] for s in gc)))

    pre = load('out_pre.jsonl')
    if pre:
        print('\n## C2: preprocessed fixed-walk table\n')
        print(f'- {len(pre)} queries, incorrect: {sum(1 for r in pre if not r["ok"])}')
        gp = groupby(pre, lambda r: r['bits'])
        print('\n| bits | n | pre ops | pre/n^(2/3) | S (DPs) | S/n^(1/3) | online mean | online/n^(1/3) | online/sqrt(n) | ref mean | S*T^2/n | break-even #queries |\n|---|---|---|---|---|---|---|---|---|---|---|---|')
        Gon, Gtot = {}, {}
        for b in sorted(gp):
            n = gp[b][0]['n']; on = [r['online_ops'] for r in gp[b]]; S = gp[b][0]['S']; po = gp[b][0]['pre_ops']
            refm = st.mean(r['ops'] for r in gr[b]) if b in gr else float('nan')
            be = po/(refm-st.mean(on)) if refm == refm and refm > st.mean(on) else float('nan')
            print(f'| {b} | {n} | {po} | {po/n**(2/3):.3f} | {S} | {S/n**(1/3):.2f} | {st.mean(on):.1f} | {st.mean(on)/n**(1/3):.2f} | {st.mean(on)/n**.5:.4f} | {refm:.0f} | {S*st.mean(on)**2/n:.2f} | {be:.0f} |')
            Gon[L2(n)] = on; Gtot[L2(n)] = [po+x for x in on]
        e, lo, hi = boot_fit(Gon); print(f'\nOnline exponent e_on = {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
        e, lo, hi = boot_fit(Gtot); print(f'Single-query total (pre+online) exponent e_tot = {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
        xs = sorted(gp); ys = [gp[b][0]['S']*st.mean(r['online_ops'] for r in gp[b])**2/gp[b][0]['n'] for b in xs]
        print(f'Slope of log2(S*T^2/n) vs bits (0 = sits on ST^2 ~ N): {fit(xs, [math.log2(y) for y in ys])[0]:.3f}')
        sg = sorted(gp); print('Preprocessing exponent:', f'{fit([L2(gp[b][0]["n"]) for b in sg],[math.log2(gp[b][0]["pre_ops"]) for b in sg])[0]:.3f}', ' Memory(S) exponent:', f'{fit([L2(gp[b][0]["n"]) for b in sg],[math.log2(gp[b][0]["S"]) for b in sg])[0]:.3f}')
    bN, bM = load('out_batchN.jsonl'), load('out_batchM.jsonl')
    if bN:
        print('\n## C3: batch (M = 16 instances, shared DP set) vs reference per instance\n')
        print(f'- {len(bN)} batches, incorrect: {sum(1 for r in bN if not r["ok"])}')
        g = groupby(bN, lambda r: r['bits'])
        print('\n| bits | n | trials | batch total ops | per-instance | per-inst/sqrt(n) | ref mean ops | ref/per-instance (95% CI) | DPs stored |\n|---|---|---|---|---|---|---|---|---|')
        G = {}
        for b in sorted(g):
            n = g[b][0]['n']; pi = [r['per_instance'] for r in g[b]]
            refv = [r['ops'] for r in gr[b]] if b in gr else None
            ratio = st.mean(refv)/st.mean(pi) if refv else float('nan')
            # unpaired bootstrap CI for ratio of means
            rng = random.Random(99); rs = []
            if refv:
                for _ in range(4000):
                    rs.append(st.mean(rng.choices(refv, k=len(refv)))/st.mean(rng.choices(pi, k=len(pi))))
                rs.sort(); ci = (rs[100], rs[3900])
            else: ci = (float('nan'),)*2
            print(f'| {b} | {n} | {len(pi)} | {st.mean(r["ops"] for r in g[b]):.0f} | {st.mean(pi):.0f} | {st.mean(pi)/n**.5:.3f} | {st.mean(refv) if refv else float("nan"):.0f} | {ratio:.2f} ({ci[0]:.2f}, {ci[1]:.2f}) | {st.mean(r["dps"] for r in g[b]):.0f} |')
            G[L2(n)] = pi
        e, lo, hi = boot_fit(G); print(f'\nPer-instance cost exponent in n (M=16): e = {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
    if bM:
        print('\n## C3: M-sweep at 32 bits\n')
        print(f'- {len(bM)} batches, incorrect: {sum(1 for r in bM if not r["ok"])}')
        g = groupby(bM, lambda r: r['M']); G = {}
        print('\n| M | per-instance ops | total/sqrt(M n) | ref/per-instance |\n|---|---|---|---|')
        for M in sorted(g):
            n = g[M][0]['n']; pi = [r['per_instance'] for r in g[M]]
            refm = st.mean(r['ops'] for r in gr[32]) if 32 in gr else float('nan')
            print(f'| {M} | {st.mean(pi):.0f} | {st.mean(r["ops"] for r in g[M])/(M*n)**.5:.2f} | {refm/st.mean(pi):.2f} |')
            G[math.log2(M)] = pi
        # exponent in M for M>=2? use all M
        e, lo, hi = boot_fit(G); print(f'\nPer-instance cost vs M exponent (all M): {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
        G2 = {x: v for x, v in G.items() if x >= 1}
        e, lo, hi = boot_fit(G2); print(f'Per-instance cost vs M exponent (M >= 2): {e:.3f}  95% CI ({lo:.3f}, {hi:.3f})')
main()
