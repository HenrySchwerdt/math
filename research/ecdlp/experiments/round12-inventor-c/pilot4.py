# TUNING PILOT for C1b (seed namespace 'pilot')
import random, sys, statistics as st
from lib12 import *
from algos import rho_neg, rho_ref
from algos2 import rho_neg_w
bits=int(sys.argv[1]); T=int(sys.argv[2])
E,P,n=find_prime_order_curve(bits,'pilot')
L=2**max(1,round(n**.5/16).bit_length()-1)
for name,f,kw in (('C1 frozen',rho_neg,{}),('C1b W=16 cap20',rho_neg_w,{}),('C1b W=16 cap4',rho_neg_w,{'maxfac':4}),('C1b W=32 cap4',rho_neg_w,{'W':32,'maxfac':4}),('ref',rho_ref,{})):
    cs=[];cap=[]
    for t in range(T):
        rng=random.Random(f'pilot-{bits}-{t}');k=rng.randrange(1,n);Q=E.mul(k,P)
        ops=Ops(E.p,E.a);kk,c,info=f(ops,P,Q,n,random.Random(f'w-{t}'),L,**kw);assert kk==k;cs.append(c)
        if not isinstance(info,int): cap.append(info[1]['capped'])
    print(bits,name,'mean/sqrt n',round(st.mean(cs)/n**.5,2),'capped/run',round(st.mean(cap),2) if cap else '-',flush=True)
