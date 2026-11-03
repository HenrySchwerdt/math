# tiny-curve check: Phi from dual-number Miller evaluation == brute-force normalised f_{r,P}
import sys; sys.path.insert(0,'.')
from common import *
from tate import phi_all
def brute_phi(E,P,r):
    p=E.p; a,b=E.a,E.b
    # local param t=x-xP at P; y(t) power series to order r+1 via Newton/iteration
    xP,yP=P; N=r+2
    def mul(A,B):
        C=[0]*N
        for i,ai in enumerate(A):
            if ai:
                for j,bj in enumerate(B):
                    if i+j<N: C[i+j]=(C[i+j]+ai*bj)%p
                    else: break
        return C
    # rhs series in t: (xP+t)^3+a(xP+t)+b
    X=[xP,1]+[0]*(N-2)
    rhs=[(c)%p for c in mul(mul(X,X),X)]
    rhs=[(rhs[i]+a*X[i])%p for i in range(N)]; rhs[0]=(rhs[0]+b)%p
    # sqrt series with y0=yP
    y=[yP]+[0]*(N-1)
    for n in range(1,N):
        s=mul(y,y)
        # coefficient n of y^2 = 2*y0*y_n + rest ; solve
        rest=s[n]
        y[n]=((rhs[n]-rest)*pow(2*yP,-1,p))%p
    # basis monomials x^i y^e, pole order 2i+3e<=r, e in {0,1}
    mons=[(i,e) for e in (0,1) for i in range(r) if 2*i+3*e<=r]
    mons.sort(key=lambda m:2*m[0]+3*m[1])
    assert len(mons)==r, (len(mons),r)
    pw=[[1]+[0]*(N-1)]
    for i in range(1,r+1): pw.append(mul(pw[-1],X))
    cols=[mul(pw[i],y) if e else pw[i] for (i,e) in mons]
    # need vanishing coefficients 0..r-1 -> r equations, r unknowns; f monic top => solve M c = -top col
    top=cols[-1]; 
    A=[[cols[j][i] for j in range(r-1)] for i in range(r)]
    rhsv=[(-top[i])%p for i in range(r)]
    # gaussian elimination mod p on r x (r-1) system (consistent)
    M=[A[i]+[rhsv[i]] for i in range(r)]
    row=0; piv=[]
    for c in range(r-1):
        pr=None
        for i in range(row,r):
            if M[i][c]%p: pr=i;break
        if pr is None: continue
        M[row],M[pr]=M[pr],M[row]
        inv=pow(M[row][c],-1,p); M[row]=[v*inv%p for v in M[row]]
        for i in range(r):
            if i!=row and M[i][c]:
                f=M[i][c]; M[i]=[(vi-f*vr)%p for vi,vr in zip(M[i],M[row])]
        piv.append(c); row+=1
    assert row==r-1,(row,r)
    coef=[0]*(r-1)
    for i,c in enumerate(piv): coef[c]=M[i][r-1]
    assert all(M[i][r-1]==0 for i in range(row,r))
    coef.append(1)
    def f(R):
        x,yv=R; return sum(c*pow(x,i,p)*(yv if e else 1) for c,(i,e) in zip(coef,mons))%p
    return f
ok=True; n=0
for seed in range(60):
    E,P,r=None,None,None
    found=find_curves(5,40,1,f'chk{seed}',need_1mod6=False) if False else None
    break
import random
rng=random.Random(5)
cnt=0
for p in [11,13,17,19,23,29,31,37,41,43]:
    for a in range(1,p):
        for b in range(1,p):
            try: E=Curve(a,b,p)
            except ValueError: continue
            r=E.order()
            if r<7 or not is_prime(r): continue
            P=E.points()[1]
            f=brute_phi(E,P,r)
            Ph=phi_all(E,P,r)
            xs,ys=chain(E,P,r)
            bad=0;tested=0
            for k in range(2,r):
                R=(int(xs[k]),int(ys[k]))
                v=Ph[k]
                if v is None: continue
                tested+=1
                if f(R)!=v: bad+=1
            print(p,a,b,r,'tested',tested,'mismatch',bad)
            cnt+=1
            if bad: ok=False
            break
        else: continue
        break
print('ALL OK' if ok else 'FAIL')
