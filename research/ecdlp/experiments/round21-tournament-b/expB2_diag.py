# POST-HOC diagnostic (not pre-registered; see PROTOCOL_ADDENDUM.md): why is the Fourier max of s_k below the iid null?
import sys, json
sys.path.insert(0,'.')
from common import *
from tate import phi_all
import numpy as np
curves=[]
for ci,(lo,hi) in enumerate([(4096,6000),(6000,9000)]): curves+=find_curves(lo,hi,2,f'B{ci}')
res=[]
for ci,(E,P,r) in enumerate(curves):
    p=E.p; phi=phi_all(E,P,r)
    s=np.zeros(r); 
    for k in range(2,r):
        if phi[k] is not None: s[k]=1 if pow(phi[k],(p-1)//2,p)==1 else -1
    n=int((s!=0).sum())
    F=np.fft.fft(s); P2=np.abs(F[1:])**2/n
    C=np.fft.ifft(np.abs(F)**2).real            # cyclic autocorrelation, lag tau
    maxC=np.abs(C[1:]).max()/np.sqrt(n)
    rng=np.random.default_rng(ci)
    nulls=[]; nullv=[]
    for _ in range(100):
        t=np.zeros(r); idx=s!=0; t[idx]=rng.choice([-1,1],idx.sum())
        Ft=np.fft.fft(t); Ct=np.fft.ifft(np.abs(Ft)**2).real
        nulls.append(np.abs(Ct[1:]).max()/np.sqrt(n)); nullv.append((np.abs(Ft[1:])**2/n).var())
    # symmetry s_{r-k} vs s_k
    sym=float(np.mean([s[k]*s[r-k] for k in range(2,r-1) if s[k]*s[r-k]!=0]))
    res.append(dict(r=r,var_P2_over_n=float(P2.var()),null_var_median=float(np.median(nullv)),maxC_over_sqrt_n=float(maxC),null_maxC_median=float(np.median(nulls)),null_maxC_q01=float(np.quantile(nulls,0.01)),mean_s_k_s_rmk=sym))
    print(json.dumps(res[-1]))
json.dump(res,open('expB2_diag_results.json','w'),indent=1)
