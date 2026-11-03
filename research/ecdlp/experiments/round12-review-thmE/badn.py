"""Bad_N for target k (p>2N, p | numerator of the cusp divided difference c_{N-1}(0)); also checks target k^2 value = +-(N!)^2
and psi_m(cusp)=m for m<=60 via the division-polynomial recursion on integers (x=y=1,A=B=0)."""
from fractions import Fraction
from sympy import factorint, primerange
def dd(ys,fs):
    cur=list(fs)
    for lev in range(1,len(ys)):
        cur=[(cur[i+1]-cur[i])/(ys[i+lev]-ys[i]) for i in range(len(cur)-1)]
    return cur[0]
for N in range(3,19):
    ys=[Fraction(1,k*k) for k in range(1,N+1)]
    ck=dd(ys,[Fraction(k) for k in range(1,N+1)]); ck2=dd(ys,[Fraction(k*k) for k in range(1,N+1)])
    f=factorint(abs(ck.numerator)); bad=sorted(q for q in f if q>2*N)
    fd=factorint(ck.denominator)
    assert ck2==(-1)**(N-1)*Fraction(__import__('math').factorial(N))**2
    assert (ck>0)==((N-1)%2==0) and ck!=0
    print(f"N={N}: c_(N-1)(0) target k = {ck}  num primes {sorted(f)}  Bad_N={bad}  (denominator primes {sorted(fd)} all <=2N-1: {all(q<=2*N-1 for q in fd)})  k^2 target = (-1)^(N-1)(N!)^2 OK")
ps={0:0,1:1,2:2,3:3,4:4}
for m in range(5,61):
    if m%2: n=(m-1)//2; ps[m]=ps[n+2]*ps[n]**3-ps[n-1]*ps[n+1]**3
    else: n=m//2; num=ps[n]*(ps[n+2]*ps[n-1]**2-ps[n-2]*ps[n+1]**2); assert num%2==0; ps[m]=num//2
print("psi_m(cusp,x=y=1)=m for m<=60:", all(ps[m]==m for m in range(1,61)))
