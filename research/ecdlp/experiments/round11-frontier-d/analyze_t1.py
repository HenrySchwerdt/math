import json, glob, math, random, statistics as st
def fit(pts):  # pts: list of (r, y)
    xs=[math.log(r) for r,_ in pts]; ys=[math.log(y) for _,y in pts]
    if len(set(xs))<2: return None
    mx,my=st.mean(xs),st.mean(ys); return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
def boot(pts, B=2000):
    rng=random.Random(7); byn={}
    for r,y,n in pts: byn.setdefault(n,[]).append((r,y))
    # resample instances within each n
    out=[]
    for _ in range(B):
        s=[]
        for n,v in byn.items(): s+= [rng.choice(v) for _ in v]
        f=fit(s)
        if f is not None: out.append(f)
    out.sort(); return out[int(.025*len(out))], out[int(.975*len(out))]
for f in sorted(glob.glob('out_*.jsonl')):
    if 't2' in f: continue
    R=[json.loads(l) for l in open(f)]
    cens=sum(1 for d in R if d.get('censored')); solved=[d for d in R if d['sat']]
    ns=sorted({d['n'] for d in R})
    per={n:[(d['secs'],d['conflicts'],bool(d.get('censored')),d.get('key_ok')) for d in R if d['n']==n] for n in ns}
    print('==',f,'runs',len(R),'censored',cens,'wrong keys',sum(1 for d in R if d['sat'] and not d['key_ok']))
    for n in ns:
        v=[d for d in R if d['n']==n]; print('  n=%d vars~%d  secs=%s  conf=%s' % (n, v[0].get('vars',0), [('>' if d.get('censored') else '')+str(d['secs']) for d in v], [d['conflicts'] for d in v]))
    for metric in ('conflicts','secs'):
        pts=[(d['r'], (d[metric] or 0), d['n']) for d in R if d[metric]]
        if len({p[2] for p in pts})>=2:
            e=fit([(r,y) for r,y,_ in pts]); lo,hi=boot(pts); print('  %s exponent %.2f  95%%CI [%.2f, %.2f] (censored counted at cap; <=%d sizes)' % (metric,e,lo,hi,len({p[2] for p in pts})))
