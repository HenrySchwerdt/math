import random

def isprime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
def primerange(a,b): return [n for n in range(a,b) if isprime(n)]
def factorint(n):
    f={};d=2
    while d*d<=n:
        while n%d==0: f[d]=f.get(d,0)+1; n//=d
        d+=1
    if n>1: f[n]=f.get(n,0)+1
    return f

random.seed(1)
def count(p,a,b):
    sq={}
    for y in range(p): sq[y*y%p]=sq.get(y*y%p,0)+1
    return 1+sum(sq.get((x**3+a*x+b)%p,0) for x in range(p))
def order_mod(q,r):
    k=1;t=q%r
    while t!=1: t=t*q%r;k+=1
    return k
stats=[];tot=0;small=0;anom=0
for p in primerange(1000,3000):
    for _ in range(6):
        a,b=random.randrange(p),random.randrange(p)
        if (4*a**3+27*b*b)%p==0: continue
        N=count(p,a,b); r=max(factorint(N)); 
        if r<=5: continue
        k=order_mod(p,r) if r!=p else 0
        tot+=1; anom+= (N==p)
        if k and k<=6: small+=1
        stats.append((k/ r) if k else 0)
print("curves",tot,"anomalous",anom,"embdeg<=6:",small)
print("mean k/r (nonanomalous):",sum(stats)/len(stats),"min k/r",min(stats))
# Hom(Z/r -> F_q^*) count: |{x: x^r=1}| = gcd(r,q-1)
bad=0
for q in primerange(3,400):
    for r in primerange(2,200):
        # count elements of order dividing r in F_q^*
        c=sum(1 for x in range(1,q) if pow(x,r,q)==1)
        from math import gcd
        if c!=gcd(r,q-1): bad+=1
print("hom count mismatches",bad)
