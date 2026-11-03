import math
def isprime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
def pf(n):
    f=set();d=2
    while d*d<=n:
        while n%d==0: f.add(d); n//=d
        d+=1
    if n>1: f.add(n)
    return f
def ordmod(q,r,M):
    t=1
    for k in range(1,M+1):
        t=t*q%r
        if t==1: return k
    return None
M=6
for p in [10007,20011,40009,80021]:
    s=math.isqrt(4*4*p)  # 4*sqrt(p)
    lim=2*math.isqrt(p)
    hits=0;tot=0
    for t in range(-lim,lim+1):
        N=p+1-t;tot+=1
        if any(r>4*math.sqrt(p) and ordmod(p,r,M) for r in pf(N)): hits+=1
    print(p,"traces",tot,"traces with prime factor r>4sqrt(p), ord_r(p)<=6:",hits,"bound M(M+1)=",M*(M+1))
