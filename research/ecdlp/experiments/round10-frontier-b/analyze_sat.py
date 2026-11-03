import json, math, glob, statistics as st
rows=[]
for f in glob.glob('sat_m*.jsonl'):
    for l in open(f):
        try: rows.append(json.loads(l))
        except: pass
by={}
for d in rows: by.setdefault(d['n'],[]).append(d)
xs=[];ys=[]
print('n  runs  r_med  conflicts(med)  secs(med)  rho_ops(med)  conflicts/rho  solved')
for n in sorted(by):
    v=by[n]; c=st.median(d['conflicts'] for d in v); s=st.median(d['secs'] for d in v); r=st.median(d['r'] for d in v); rho=st.median(d['rho_ops'] for d in v)
    print(n,len(v),r,int(c),round(s,1),rho,round(c/rho),sum(1 for d in v if d['res']), 'all correct' if all(d['correct'] for d in v if d['res']) else 'WRONG')
    xs.append(math.log(r)); ys.append(math.log(c))
mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
slope=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
print('log-log slope conflicts vs r: %.2f (rho: 0.5, brute: 1.0)'%slope)
nn=[n for n in sorted(by)]
# per-instance regression
X=[math.log(d['r']) for d in rows];Y=[math.log(d['conflicts']) for d in rows]
mx=sum(X)/len(X);my=sum(Y)/len(Y)
print('per-instance slope: %.2f'%(sum((a-mx)*(b-my) for a,b in zip(X,Y))/sum((a-mx)**2 for a in X)))
print('hint runs')
h={}
for l in open('sat_hint.jsonl'):
    try: d=json.loads(l)
    except: continue
    h.setdefault(d['t_unknown'],[]).append(d)
for t in sorted(h):
    print('t',t,'runs',len(h[t]),'median conflicts',int(st.median(d['conflicts'] for d in h[t])),'secs',round(st.median(d['secs'] for d in h[t]),1),'solved',sum(1 for d in h[t] if d['res']), '2^(t/2)=',round(2**(t/2),1),'2^t=',2**t)
