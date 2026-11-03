import json,glob,numpy as np
rng=np.random.default_rng(16)
BITS=[16,20,24,28,32]; curves={(c['bits'],c['seed']):c for c in json.load(open('curves.json'))}
def rho_from(S,Ts,r): Ts=np.array(Ts,float); return S*Ts.mean()**2/r
def boot_rho(S,Ts,r,B=2000):
    Ts=np.array(Ts,float); idx=rng.integers(0,len(Ts),(B,len(Ts))); return S*Ts[idx].mean(1)**2/r
def slope(x,y): return np.polyfit(x,y,1)[0]
out=[]; P=lambda *a: (print(*a), out.append(' '.join(map(str,a))))
# ---------- E3
data={}
for b in BITS:
    for s in range(3): data[(b,s)]=json.load(open(f'out_e3_{b}_{s}.json'))
def eval_series(method,which):
    # returns per-curve bootstrap samples of rho per size: dict bits-> array (B,3)
    res={}; summ={}
    for b in BITS:
        per=[]; sc=[]
        for s in range(3):
            d=data[(b,s)][method]; r=curves[(b,s)]['r']
            if which=='A': e=d['evalA']; per.append(boot_rho(e['S'],e['Ts'],r)); sc.append((e['succ'],e['S'],np.mean(e['Ts']),e['prep']))
            else:
                Tcat=[]; Ss=[]; 
                bs=np.zeros(2000)
                for e in d['evalB']:
                    bs+=boot_rho(e['S'],e['Ts'],r)/3
                per.append(bs); sc.append((np.mean([e['succ'] for e in d['evalB']]),np.mean([e['S'] for e in d['evalB']]),np.mean([np.mean(e['Ts']) for e in d['evalB']]),np.mean([e['prep'] for e in d['evalB']])))
        res[b]=np.stack(per,1); summ[b]=sc
    return res,summ
def curvelevel(res):  # bootstrap over curves too: sample curve idx
    ms={}
    for b in BITS:
        a=res[b]; ci=rng.integers(0,3,(2000,3)); ms[b]=np.take_along_axis(a,ci,1).mean(1)
    return ms
def report(name,res,summ):
    ms=curvelevel(res); P(f'## {name}')
    for b in BITS:
        v=ms[b]; sc=summ[b]; P(f' bits {b}: rho mean {res[b].mean():.2f} CI95 [{np.percentile(v,2.5):.2f},{np.percentile(v,97.5):.2f}] min succ {min(x[0] for x in sc):.3f} S~{np.mean([x[1] for x in sc]):.0f} T~{np.mean([x[2] for x in sc]):.0f} prep~{np.mean([x[3] for x in sc]):.0f}')
    X=np.array(BITS,float); sl=np.array([slope(X,np.log2([ms[b][i] for b in BITS])) for i in range(2000)])
    P(f' slope log2(rho) vs bits: {slope(X,np.log2([res[b].mean() for b in BITS])):.4f} CI95 [{np.percentile(sl,2.5):.4f},{np.percentile(sl,97.5):.4f}]')
    return ms
allms={}
for m in ('B0','H'):
    for w in 'AB':
        res,summ=eval_series(m,w); allms[(m,w)]=(res,curvelevel(res)); report(f'E3 {m} eval{w}',res,summ)
P('## E3 ratio H/B0 (curve-level bootstrap, out of sample)')
for w in 'AB':
    for b in BITS:
        r=allms[('H',w)][1][b]/allms[('B0',w)][1][b]
        P(f' eval{w} bits {b}: H/B0 {np.median(r):.3f} CI95 [{np.percentile(r,2.5):.3f},{np.percentile(r,97.5):.3f}]')
P('## E3 winners curse: train rho (min over candidates) vs evalA vs evalB, per curve')
for b in BITS:
    for s in range(3):
        d=data[(b,s)]; row=[]
        for m in ('B0','H'):
            w=d[m]['winner']; tr=min(x['rho'] for x in d[m]['train'] if x['succ']>=0.98)
            row.append(f"{m}: train {tr:.2f} A {d[m]['evalA']['rho']:.2f} B {np.mean([e['rho'] for e in d[m]['evalB']]):.2f} fam {w['fam'] if m=='H' else 0}")
        P(f' {b}/{s}',' | '.join(row))
P('## E3 H winner family counts'); 
from collections import Counter
P(dict(Counter(data[k]['H']['winner']['fam'] for k in data)))
P('## E3 train rho by family (median over candidates with succ>=0.98, all curves)')
fam={}
for k,d in data.items():
    for x in d['H']['train']:
        if x['succ']>=0.98: fam.setdefault(x['c']['fam'],[]).append(x['rho'])
for f_,v in sorted(fam.items()): P(f' fam {f_}: n={len(v)} median {np.median(v):.2f} min {min(v):.2f}')
P('## E3 preprocessing ops / r^(2/3) (H eval A table)')
for b in BITS: P(f' bits {b}:',round(np.mean([data[(b,s)]['H']['evalA']['prep']/curves[(b,s)]['r']**(2/3) for s in range(3)]),2))
# ---------- E1
P('## E1 sorted x-table, giant steps')
for ex in ('0.33','0.50','0.67','0.00'):
    rows=[]
    for b in BITS:
        fs=[json.load(open(f)) for f in glob.glob(f'out_e1_{b}_*_{ex}.json')]
        if not fs: continue
        P(f' S exp {ex} bits {b}: S~{np.mean([f["S"] for f in fs]):.0f} ops {np.mean([f["mean_ops"] for f in fs]):.1f} probes_interp {np.mean([f["mean_probes_interp"] for f in fs]):.1f} binary {np.mean([f["mean_probes_binary"] for f in fs]):.1f} rho_ops {np.mean([f["rho_ops"] for f in fs]):.3f} rho_ops+probes {np.mean([f["rho_ops_plus_probes"] for f in fs]):.2f} ok {sum(f["ok"] for f in fs)}/{sum(f["nq"] for f in fs)} prep {np.mean([f["prep"] for f in fs]):.0f}')
        rows.append((b,np.mean([f["rho_ops"] for f in fs])))
    if len(rows)>2: P(f'  slope log2 rho_ops vs bits: {slope([a for a,_ in rows],np.log2([c for _,c in rows])):.3f}')
# ---------- E2
P('## E2 decision tree held-out accuracy (chance 0.0625); leak = Wilson99 lower > 0.0675')
for b in BITS:
    for e in json.load(open(f'out_e2_{b}.json')):
        tag='PLANTED' if e['planted'] else 'real'
        best=max(e['res'].items(),key=lambda kv:kv[1]['test_acc'])
        P(f" bits {b} seed {e['seed']} {tag}: "+', '.join(f"{k}:{v['test_acc']:.4f}{'*' if v['leak'] else ''}(d{v['depth']})" for k,v in e['res'].items() if k.endswith('/255') or k.endswith('/4095')))
real_leaks={b:[k for e in json.load(open(f'out_e2_{b}.json')) if not e['planted'] for k,v in e['res'].items() if v['leak']] for b in BITS}
P('real-curve leak flags by size:',{b:len(v) for b,v in real_leaks.items()})
open('results_analysis.md','w').write('```\n'+'\n'.join(out)+'\n```\n')
# ---------- post hoc (not pre-registered): slope restricted to bits >= 24, and full-range slope of median
P('## POST HOC (not pre-registered): slope over bits 24..32 only')
for m in ('B0','H'):
    for w in 'AB':
        ms=allms[(m,w)][1]; X=np.array([24,28,32],float)
        sl=np.array([slope(X,np.log2([ms[b][i] for b in (24,28,32)])) for i in range(2000)])
        P(f' {m} eval{w}: slope {np.percentile(sl,50):.4f} CI95 [{np.percentile(sl,2.5):.4f},{np.percentile(sl,97.5):.4f}]')
open('results_analysis.md','w').write('```\n'+'\n'.join(out)+'\n```\n')
