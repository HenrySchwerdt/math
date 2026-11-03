import sys, random
sys.path.insert(0,'/home/user/math/research/ecdlp/experiments/lib')
from toyec import Curve
from hyper2 import *
p=251; rng=random.Random(1)
while True:
    a,b=rng.randrange(p),rng.randrange(p)
    try: E=Curve(a,b,p)
    except ValueError: continue
    r=E.order()
    break
print(p,a,b,r)
c=1
F=pmul(pmul((1,0,1),(1,0,1),p),(1,0,1),p)  # placeholder (w^2+1)^3
# F(w)=f(w^2+c)
def f_of(t): return trim([b,a,0,1])  # not used
X=(c,0,1)
f=trim([b,a,0,1])
Fp=(0,)
F=()
pw=(1,)
for coef in f:
    F=padd(F,pscal(pw,coef,p),p); pw=pmul(pw,X,p)
print(F)
J=Genus2(F,p)
pts=E.points()[1:]
Q1,Q2=rng.sample(pts,2)
A=J.fibre(Q1[0],Q1[1],c);B=J.fibre(Q2[0],Q2[1],c)
S=J.add(A,B); Q3=E.add(Q1,Q2)
print(S, J.fibre(Q3[0],Q3[1],c))
