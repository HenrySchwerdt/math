# Toy check for E3 (comparison BST over sorted x(kP)) and E0 (Legendre distinguisher carries no k-info).
import math, random
p = 10007
a, b = 2, 3
def inv(x): return pow(x, p-2, p)
def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1,y1),(x2,y2)=P,Q
    if x1==x2 and (y1+y2)%p==0: return None
    l = (3*x1*x1+a)*inv(2*y1)%p if P==Q else (y2-y1)*inv(x2-x1)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def sqrt_mod(n):
    n%=p
    if n==0: return 0
    if pow(n,(p-1)//2,p)!=1: return None
    for y in range(p):
        if y*y%p==n: return y
G=None
for x in range(p):
    y=sqrt_mod(x**3+a*x+b)
    if y is not None: G=(x,y); break
orbit=[None]; Q=None; k=0
while True:
    Q=add(Q,G); k+=1
    if Q is None: break
    orbit.append(Q)
r=k
N=min(300,(r-1)//2)
xs=[orbit[k][0] for k in range(1,N+1)]
assert len(set(xs))==N
table=sorted((x,k) for k,x in enumerate(xs,1))
sx=[t[0] for t in table]
def solve(u):
    lo,hi,depth=0,N-1,0
    while lo<hi:
        mid=(lo+hi)//2; depth+=1
        if u<=sx[mid]: hi=mid
        else: lo=mid+1
    return table[lo][1],depth
ok=all(solve(orbit[k][0])[0]==k for k in range(1,N+1))
maxd=max(solve(orbit[k][0])[1] for k in range(1,N+1))
print(f"r={r} N={N} bst_correct={ok} max_depth={maxd} ceil_log2N={math.ceil(math.log2(N))} leaves={N} arithmetic_nodes=0")
print("equality chain (Lean model, const+sub per test): max arithmetic nodes on a path =", 2*N, "; Theorem DT needs only L >=", round(math.log2((N+1)/9),2))
def is_xcoord(x): return pow((x**3+a*x+b)%p,(p-1)//2,p) in (0,1)
real=sum(is_xcoord(x) for x in xs)/N
rnd=sum(is_xcoord(x) for x in random.Random(1).sample(range(p),N))/N
print(f"curve-membership (Legendre) test pass rate: real={real:.3f} random_injection_into_Fp={rnd:.3f}; test output independent of k-labelling")
