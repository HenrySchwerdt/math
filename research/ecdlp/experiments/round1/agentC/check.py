import random, math
def add(P,Q,a,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2 and (y1+y2)%p==0: return None
    if P==Q: l=(3*x1*x1+a)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p
    return (x3,(l*(x1-x3)-y1)%p)
def mul(k,P,a,p):
    R=None
    while k:
        if k&1:R=add(R,P,a,p)
        P=add(P,P,a,p);k>>=1
    return R
def order(P,a,p):
    R=P;n=1
    while R is not None: R=add(R,P,a,p);n+=1
    return n
random.seed(1)
tests=0;bad=0
for p in [5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199]:
    for _ in range(4):
        a=random.randrange(p);b=random.randrange(p)
        if (4*a**3+27*b**2)%p==0: continue
        pts=[(x,y) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b)%p==0]
        if not pts: continue
        P=random.choice(pts); r=order(P,a,p)
        k0=random.randrange(r); Q=mul(k0,P,a,p)
        sols=[k for k in range(3*r+2) if mul(k,P,a,p)==Q]
        exp=[k for k in range(3*r+2) if k%r==k0]
        tests+=1; bad+= sols!=exp
        assert r<=p+1+2*math.isqrt(p)+1
print("ECDLP solution-set = k0 + r*Z tests:",tests,"failures:",bad)
# SLP counting: programs of length L: prod_{i=1}^L 4 i^2 = 4^L (L!)^2
for bits in [64,128,160,256,384,521]:
    L=0;lg=0.0
    while lg<bits:
        L+=1;lg+=2+2*math.log2(L)
    print("bits",bits,"min L with 4^L (L!)^2 >= 2^bits:",L,"; vs bits/ (2*log2 bits)=",round(bits/(2*math.log2(bits)),1))
# double-and-add op count
for bits in [160,256]:
    k=(1<<bits)-1
    print("worst-case double-and-add ops for",bits,"bit k:",(bits-1)+(bits-1))
