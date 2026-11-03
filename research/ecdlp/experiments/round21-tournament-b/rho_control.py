import sys, random, json
sys.path.insert(0,'.')
from common import *
import numpy as np
from math import sqrt
def rho_steps(E,P,r,Q,rng,nb=16):
    # r-adding walk with Floyd cycle detection, counts group additions; retries with new randomisation
    total=0
    while True:
        tbl=[(rng.randrange(r),rng.randrange(r)) for _ in range(nb)]
        pts=[E.add(E.mul(a,P),E.mul(b,Q)) for a,b in tbl]
        def step(R,a,b):
            if R is None: h=0
            else: h=R[0]%nb
            return E.add(R,pts[h]),(a+tbl[h][0])%r,(b+tbl[h][1])%r
        a0,b0=rng.randrange(r),rng.randrange(r)
        R0=E.add(E.mul(a0,P),E.mul(b0,Q)); 
        x=(R0,a0,b0); y=(R0,a0,b0)
        for it in range(1,20*int(sqrt(r))+100):
            x=step(*x); y=step(*step(*y)); total+=3
            if x[0]==y[0]:
                db=(y[2]-x[2])%r; da=(x[1]-y[1])%r
                if db!=0:
                    k=da*pow(db,-1,r)%r
                    if E.mul(k,P)==Q: return total
                break
res=[]
sizes=[(500,900),(1000,1800),(2000,3500),(4096,6000),(6000,9000),(9000,13000)]
for si,(lo,hi) in enumerate(sizes):
    for (E,P,r) in find_curves(lo,hi,1,f'rho{si}',need_1mod6=False):
        rng=random.Random(si)
        costs=[]
        for t in range(120):
            k=rng.randrange(1,r); Q=E.mul(k,P)
            costs.append(rho_steps(E,P,r,Q,rng))
        res.append((r,float(np.mean(costs))))
        print(res[-1],flush=True)
rs=np.array([a for a,_ in res]); cs=np.array([b for _,b in res])
A=np.vstack([np.sqrt(rs),np.ones_like(rs)]).T
(alpha,gamma),*_=np.linalg.lstsq(A,cs,rcond=None)
pred=A@np.array([alpha,gamma]); r2=1-((cs-pred)**2).sum()/((cs-cs.mean())**2).sum()
print(json.dumps(dict(alpha=alpha,gamma=gamma,R2=r2,n_curves=len(res),instances_per_curve=120)))
json.dump(dict(points=res,alpha=alpha,gamma=gamma,R2=r2),open('rho_control_results.json','w'))
