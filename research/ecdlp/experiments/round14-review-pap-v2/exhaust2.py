"""Exhaustive small-p check of Theorem D: |Z| vs |zeros of Num| vs w_N p^2, with Z computed from the group law
(independent of Num). Usage: exhaust2.py N p [p ...]"""
import sys, numpy as np
from sympy import Poly, ZZ
from symnum import divpolys, build, wN, x,y,A,B
def add_pt(P1,Q,a,p):
    """affine add; None = point at infinity"""
    if P1[0]==Q[0]:
        if (P1[1]+Q[1])%p==0: return None
        lam=(3*P1[0]**2+a)*pow(2*P1[1],-1,p)%p
    else: lam=(Q[1]-P1[1])*pow(Q[0]-P1[0],-1,p)%p
    x3=(lam*lam-P1[0]-Q[0])%p; return (x3,(lam*(P1[0]-x3)-P1[1])%p)
N=int(sys.argv[1]); primes=[int(a) for a in sys.argv[2:]]
ps=divpolys(2*N+1)
for target in ('k2','k'):
    W,terms=build(N,ps,target); Num=sum(terms[1:],terms[0])
    Nsub=Poly(Num.as_expr().subs(B,y**2-x**3-A*x),x,y,A,domain=ZZ)
    for p in primes:
        Av,xv,yv=np.meshgrid(np.arange(p),np.arange(p),np.arange(p),indexing='ij'); Av=Av.ravel().astype(np.int64);xv=xv.ravel().astype(np.int64);yv=yv.ravel().astype(np.int64)
        def pw(v,e):
            r=np.ones_like(v); b=v%p
            while e:
                if e&1: r=r*b%p
                b=b*b%p; e>>=1
            return r
        tot=np.zeros_like(Av)
        cache={}
        for (a,b,c),co in Nsub.terms():
            tot=(tot+(int(co)%p)*(pw(xv,a)*pw(yv,b)%p)*pw(Av,c))%p
        numzero=(tot==0)
        Wv=np.zeros_like(Av)  # evaluate W the same way
        Wsub=Poly(W.as_expr().subs(B,y**2-x**3-A*x),x,y,A,domain=ZZ)
        for (a,b,c),co in Wsub.terms():
            Wv=(Wv+(int(co)%p)*(pw(xv,a)*pw(yv,b)%p)*pw(Av,c))%p
        # group law, independent
        Zcnt=0; valid=0; subset_viol=0; Nz_valid=0; Wzero=0
        numz=numzero.reshape(-1); idx=0
        for a_ in range(p):
            for x_ in range(p):
                for y_ in range(p):
                    b_=(y_*y_-x_**3-a_*x_)%p
                    if (4*a_**3+27*b_*b_)%p==0: idx+=1; continue
                    pts=[(x_,y_)]; ok=True; cur=(x_,y_)
                    for k in range(2,N+1):
                        cur=add_pt(cur,(x_,y_),a_,p)
                        if cur is None: ok=False;break
                        pts.append(cur)
                    if ok:
                        xs=[q[0] for q in pts]
                        if len(set(xs))<N: ok=False
                    if not ok: idx+=1; continue
                    valid+=1
                    c=0
                    for i in range(N):
                        pr=1
                        for l in range(N):
                            if l!=i: pr=pr*(xs[i]-xs[l])%p
                        f=(i+1)**2 if target=='k2' else i+1
                        c=(c+f*pow(pr,-1,p))%p
                    if c==0:
                        Zcnt+=1
                        if not numz[idx]: subset_viol+=1
                    if Wv[idx]==0: Wzero+=1
                    idx+=1
        nz=int(numzero.sum())
        print(f"N={N} target={target} p={p}: valid triples={valid}/{p**3}  |Z|={Zcnt}  |Z|/p^2={Zcnt/p**2:.3f}  w_N={wN(N)}  zeros(Num) in F_p^3={nz} (={nz/p**2:.2f} p^2)  Z-not-in-zeros(Num)={subset_viol}  valid&W=0:{Wzero}  Num==0 identically: {nz==p**3}")
