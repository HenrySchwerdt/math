import json,numpy as np
rng=np.random.default_rng(17)
BITS=[24,28,32]
cur={(c['bits'],c['seed']):c for c in json.load(open('curves.json'))+json.load(open('curves_confirm.json'))}
def load(b,s):
    f=f'out_e3_{b}_{s}.json' if s<3 else f'out_e3c_{b}_{s}.json'; return json.load(open(f))
def per_curve(m,w,b,s,B=2000):
    d=load(b,s)[m]; r=cur[(b,s)]['r']
    es=[d['evalA']] if w=='A' else d['evalB']; acc=np.zeros(B)
    for e in es:
        Ts=np.array(e['Ts'],float); idx=rng.integers(0,len(Ts),(B,len(Ts))); acc+=e['S']*Ts[idx].mean(1)**2/r/len(es)
    return acc
out=[]; P=lambda *a:(print(*a),out.append(' '.join(map(str,a))))
def study(seeds,tag):
    P('##',tag); ms={}
    for m in('B0','H'):
        for w in 'AB':
            ms[(m,w)]={b:np.take_along_axis(np.stack([per_curve(m,w,b,s) for s in seeds],1),rng.integers(0,len(seeds),(2000,len(seeds))),1).mean(1) for b in BITS}
            sl=np.array([np.polyfit(BITS,np.log2([ms[(m,w)][b][i] for b in BITS]),1)[0] for i in range(2000)])
            P(f' {m} eval{w}: rho '+', '.join(f'{b}:{ms[(m,w)][b].mean():.2f}' for b in BITS)+f'  slope {np.median(sl):.4f} CI95 [{np.percentile(sl,2.5):.4f},{np.percentile(sl,97.5):.4f}]')
    for w in 'AB':
        P(f' H/B0 eval{w}: '+', '.join(f'{b}: {np.median(ms[("H",w)][b]/ms[("B0",w)][b]):.3f} [{np.percentile(ms[("H",w)][b]/ms[("B0",w)][b],2.5):.3f},{np.percentile(ms[("H",w)][b]/ms[("B0",w)][b],97.5):.3f}]' for b in BITS))
    for b in BITS:
        sc=[min(load(b,s)['H']['evalA']['succ'],*[e['succ'] for e in load(b,s)['H']['evalB']]) for s in seeds]; P(f'  min H success bits {b}: {min(sc):.3f}')
study([3,4,5],'FRESH curves seeds 3-5 (confirmatory)')
study([0,1,2,3,4,5],'POOLED seeds 0-5')
open('results_confirm.md','w').write('```\n'+'\n'.join(out)+'\n```\n')
