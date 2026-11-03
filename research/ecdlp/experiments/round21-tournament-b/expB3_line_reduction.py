# POST-HOC (addendum): test the paper explanation  chi_2(f_{r,P}(R)) = const * chi_2(tangent line at Q0=((r-1)/2)P)(R)
import sys, json
sys.path.insert(0,'.')
from common import *
from tate import phi_all
import numpy as np
curves=[]
for ci,(lo,hi) in enumerate([(4096,6000),(6000,9000)]): curves+=find_curves(lo,hi,2,f'B{ci}')
out=[]
for ci,(E,P,r) in enumerate(curves):
    p=E.p; phi=phi_all(E,P,r); xs,ys=chain(E,P,r)
    h=(r-1)//2; x0,y0=int(xs[h]),int(ys[h]); m=(3*x0*x0+E.a)*pow(2*y0,-1,p)%p
    chi=lambda v: 1 if pow(v%p,(p-1)//2,p)==1 else -1
    prods=[]
    for k in range(2,r):
        if phi[k] is None: continue
        L=(int(ys[k])-y0-m*(int(xs[k])-x0))%p
        if L==0: continue
        prods.append(chi(phi[k])*chi(L))
    prods=np.array(prods)
    out.append(dict(r=r,tested=len(prods),frac_plus=float((prods==1).mean())))
    print(out[-1])
json.dump(out,open('expB3_results.json','w'))
