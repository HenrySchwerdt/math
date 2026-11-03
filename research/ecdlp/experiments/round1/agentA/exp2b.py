# EXP2b: lift-independence of Smart's psi on the anomalous curve (random x-lift x+p*s), seed fixed
import random
from exp2 import *
rng=random.Random(5); p,a,b=761,622,190; m=p*p
def rpt():
    while True:
        x=rng.randrange(p); r=(x**3+a*x+b)%p
        ys=[y for y in range(1,p) if y*y%p==r] if r else []
        if ys: return (x,ys[0])
P=rpt(); ok=0
def rl(Pt):  # random lift
    x,y=Pt; x2=(x+p*rng.randrange(p))%m
    f=(x2**3+a*x2+b)%m; y0=y
    t=((f-y0*y0)//p)*pow(2*y0,-1,p)%p
    return (x2,(y0+p*t)%m)
for _ in range(20):
    k=rng.randrange(1,p); R=None
    for _ in range(k): R=aff_add(R,P,a,p)
    c=lambda U:(smart_psi(rl(U),a,p))
    k_rec=c(R)*pow(c(P),-1,p)%p; ok+=(k_rec==k)
print("random x-lifts:",ok,"/20")
