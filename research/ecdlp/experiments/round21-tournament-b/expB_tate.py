import sys, random, json, cmath, math
sys.path.insert(0,'.')
from common import *
from tate import phi_all
import numpy as np
from scipy.stats import chi2, norm
sys.setrecursionlimit(10000)

def liouville(n):
    lam=np.ones(n+1,dtype=np.int64); spf=list(range(n+1))
    for i in range(2,int(n**.5)+1):
        if spf[i]==i:
            for j in range(i*i,n+1,i):
                if spf[j]==j: spf[j]=i
    Om=[0]*(n+1)
    for k in range(2,n+1): Om[k]=Om[k//spf[k]]+1
    return np.array([(-1)**Om[k] for k in range(n+1)]),spf
def smooth_ind(n,B,spf):
    out=np.zeros(n+1,dtype=bool)
    for k in range(1,n+1):
        m=k; ok=True
        while m>1:
            if spf[m]>B: ok=False;break
            m//=spf[m]
        out[k]=ok
    return out
def wilson_half(n,z=2.576):
    return z*math.sqrt(0.25/n)
out=[]
specs=[(4096,6000),(6000,9000)]
curves=[]
for ci,(lo,hi) in enumerate(specs): curves+=find_curves(lo,hi,2,f'B{ci}')
for ci,(E,P,r) in enumerate(curves):
    p=E.p
    phi=phi_all(E,P,r)
    xs,ys=chain(E,P,r)
    ks=np.array([k for k in range(2,r) if phi[k] is not None])
    nbad=(r-2)-len(ks)
    lam,spf=liouville(r); sm=smooth_ind(r,int(round(r**(1/3))),spf)
    g=next(g for g in range(2,p) if all(pow(g,(p-1)//q,p)!=1 for q in set(f for f in range(2,p) if (p-1)%f==0 and all(f%t for t in range(2,int(f**.5)+1)))))
    zeta3=pow(g,(p-1)//3,p)
    for l in (2,3):
        e=np.array([ {1:0,zeta3:1,zeta3*zeta3%p:2}[pow(phi[k],(p-1)//l,p)] if l==3 else (0 if pow(phi[k],(p-1)//2,p)==1 else 1) for k in ks])
        n=len(ks)
        rec=dict(curve=ci,p=p,r=r,l=l,n=n,degenerate=nbad)
        # B1
        cnt=np.bincount(e,minlength=l); rec['B1_chi2_p']=float(chi2.sf(((cnt-n/l)**2/(n/l)).sum(),l-1))
        # B2
        w=np.exp(2j*np.pi*e/l)
        def maxF(w):
            seq=np.zeros(r,dtype=complex); seq[ks]=w
            F=np.abs(np.fft.fft(seq)); return F[1:].max()
        obs=maxF(w)
        rng=np.random.default_rng(ci*10+l)
        null=sorted(maxF(np.exp(2j*np.pi*rng.integers(0,l,n)/l)) for _ in range(200))
        rec['B2_max']=float(obs); rec['B2_null_median']=float(null[100]); rec['B2_null_q99']=float(null[198]); rec['B2_exceeds_q99']=bool(obs>null[198])
        # B3
        pv=[]
        for m in range(2,17):
            T=np.zeros((l,m))
            for ee,kk in zip(e,ks): T[ee,kk%m]+=1
            ex=T.sum(1,keepdims=True)*T.sum(0,keepdims=True)/T.sum()
            pv.append(float(chi2.sf(((T-ex)**2/ex).sum(),(l-1)*(m-1))))
        rec['B3_min_p']=min(pv); rec['B3_reject_bonf']=bool(min(pv)<0.01/15)
        # B4
        zs={}
        for name,feat in (('liouville',lam[ks].astype(float)),('smooth',sm[ks].astype(float)),('k_mod2',(ks%2).astype(float))):
            f=(feat-feat.mean())/(feat.std()+1e-12)
            for comp,sc in (('re',np.cos(2*np.pi*e/l)),('im',np.sin(2*np.pi*e/l))):
                if l==2 and comp=='im': continue
                s=(sc-sc.mean())/(sc.std()+1e-12)
                zs[f'{name}_{comp}']=float((f*s).mean()*math.sqrt(n))
        rec['B4_z']=zs; rec['B4_maxabs_z']=max(abs(v) for v in zs.values())
        # B5 predictor of [k>r/2]
        rng2=random.Random(ci*7+l)
        perm=list(range(n)); rng2.shuffle(perm)
        tr,te=perm[:n//2],perm[n//2:]
        y=(ks>r//2).astype(int)
        yp=(ys[ks]%2).astype(int); xp=(xs[ks]%2).astype(int)
        def acc(cell):
            tab={}
            for i in tr: tab.setdefault(cell[i],[0,0])[y[i]]+=1
            c=0
            for i in te:
                t=tab.get(cell[i],[0,0]); c+= (1 if t[1]>t[0] else 0)==y[i]
            return c/len(te)
        cells={'e':[int(v) for v in e],'e,ypar,xpar':[(int(a),int(b),int(c)) for a,b,c in zip(e,yp,xp)]}
        rec['B5']={nm:acc(c) for nm,c in cells.items()}
        # B6 planted
        rngp=np.random.default_rng(99+ci)
        leak=np.where(rngp.random(n)<0.45,1-y,y)  # advantage 0.05 downward: majority-flip detectable as anti-correlation
        cells['planted']=[(int(a),int(b)) for a,b in zip(e,leak)]
        rec['B5']['planted_control']=acc(cells['planted'])
        rec['B5_half_width99']=wilson_half(len(te)); rec['leak_bar_2r^-1/4']=2*r**-0.25
        out.append(rec)
        print(json.dumps(rec))
json.dump(out,open('expB_results.json','w'),indent=1)
