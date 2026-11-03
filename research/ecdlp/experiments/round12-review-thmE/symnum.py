"""Independent symbolic recomputation of Num_N (Theorem D) for small N with sympy.
Checks: polynomiality, weighted homogeneity + weight, total degree after B-substitution vs w_N,
Num(tau0), Num == W*c_{N-1} numerically against the real group law, both targets."""
import sys, random
from sympy import symbols, Poly, ZZ, expand, div, cancel, Rational
x,y,A,B = symbols('x y A B')
def divpolys(M):
    ps = {0: Poly(0,x,y,A,B,domain=ZZ), 1: Poly(1,x,y,A,B,domain=ZZ), 2: Poly(2*y,x,y,A,B,domain=ZZ)}
    P=lambda e: Poly(e,x,y,A,B,domain=ZZ)
    ps[3]=P(3*x**4+6*A*x**2+12*B*x-A**2)
    ps[4]=P(4*y*(x**6+5*A*x**4+20*B*x**3-5*A**2*x**2-4*A*B*x-8*B**2-A**3))
    for m in range(5,M+1):
        if m%2:
            n=(m-1)//2; ps[m]=ps[n+2]*ps[n]**3-ps[n-1]*ps[n+1]**3
        else:
            n=m//2; num=ps[n]*(ps[n+2]*ps[n-1]**2-ps[n-2]*ps[n+1]**2)
            q,r=div(num,P(2*y)); assert r.is_zero; ps[m]=q
    return ps
def weight_of(poly):
    ws=set()
    for (a,b,c,d),co in poly.terms(): ws.add(2*a+3*b+4*c+6*d)
    return ws
def S2(N): return N*(N+1)*(2*N+1)//6
def wN(N): return (N-1)*(S2(N)-Rational(N+2,2))
def build(N, ps, target):
    th={m:ps[m]**2 for m in range(1,N+1)}
    # W = prod_{a<b} psi_{a+b} psi_{b-a}
    def pairprod(excl):
        r=Poly(1,x,y,A,B,domain=ZZ)
        for a in range(1,N+1):
            for b in range(a+1,N+1):
                if a==excl or b==excl: continue
                r=r*ps[a+b]*ps[b-a]
        return r
    W=pairprod(None)
    terms=[]
    for i in range(1,N+1):
        sign=(-1)**(N-1)
        t=Poly(1,x,y,A,B,domain=ZZ)
        for l in range(1,N+1):
            if l==i: continue
            if i-l<0: sign=-sign
            t=t*th[l]
        t=t*th[i]**(N-1)*pairprod(i)
        f=i*i if target=='k2' else i
        terms.append(t*(sign*f))
    return W,terms
if __name__=="__main__":
    Ns=[int(a) for a in sys.argv[1:]] or [3,4]
    ps=divpolys(2*max(Ns)+1)
    for N in Ns:
        for target in ('k2','k'):
            W,terms=build(N,ps,target)
            Num=sum(terms[1:],terms[0])
            wts=[weight_of(t) for t in terms]
            wall=weight_of(Num)
            expect=2*(N-1)*S2(N)-(N-1)*(N+2)
            # substitute B
            sub=lambda P: Poly(P.as_expr().subs(B,y**2-x**3-A*x),x,y,A,domain=ZZ)
            Ns_=sub(Num)
            print(f"N={N} target={target}: summand weights {[sorted(w) for w in wts]} Num weights {sorted(wall)} expected {expect}")
            print(f"   w_N={wN(N)} total degree of Num (after B-subst) = {Ns_.total_degree()}  (claimed bound {wN(N)}); #terms {len(Ns_.terms())}")
            val=Num.as_expr().subs({x:1,y:1,A:0,B:0}); Wv=W.as_expr().subs({x:1,y:1,A:0,B:0})
            print(f"   Num(tau0)={val}, W(tau0)={Wv}, ratio={Rational(val,Wv)}")
            # numeric check against group law mod big prime
            p=1000003; random.seed(5+N); ok=0
            def ev(P,Av,xv,yv):
                Bv=(yv*yv-xv**3-Av*xv)%p
                return sum(co*pow(xv,a,p)*pow(yv,b,p)*pow(Av,c,p)*pow(Bv,d,p) for (a,b,c,d),co in P.terms())%p
            for _ in range(5):
                Av,xv,yv=(random.randrange(p) for _ in range(3))
                Bv=(yv*yv-xv**3-Av*xv)%p
                def add(P1,Q):
                    if P1[0]==Q[0]: lam=(3*P1[0]**2+Av)*pow(2*P1[1],-1,p)%p
                    else: lam=(Q[1]-P1[1])*pow(Q[0]-P1[0],-1,p)%p
                    x3=(lam*lam-P1[0]-Q[0])%p; return (x3,(lam*(P1[0]-x3)-P1[1])%p)
                try:
                    pts={1:(xv,yv)}
                    for k in range(2,N+1): pts[k]=add(pts[k-1],(xv,yv))
                    xs=[pts[k][0] for k in range(1,N+1)]
                    c=0
                    for i in range(N):
                        pr=1
                        for l in range(N):
                            if l!=i: pr=pr*(xs[i]-xs[l])%p
                        f=(i+1)**2 if target=='k2' else i+1
                        c=(c+f*pow(pr,-1,p))%p
                    Wm=ev(W,Av,xv,yv); Nm=ev(Num,Av,xv,yv)
                    assert Nm==c*Wm%p, "MISMATCH"; ok+=1
                except (ZeroDivisionError,ValueError): pass
            print(f"   Num == W*c_(N-1) mod {p} at {ok} random points: OK")
