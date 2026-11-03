# TUNING PILOT for C3 (seed namespace 'pilot')
import random, sys, statistics as st
from lib12 import *
from algos import *
bits=int(sys.argv[1]); M=int(sys.argv[2]); T=int(sys.argv[3])
E,P,n=find_prime_order_curve(bits,'pilot')
for div in (2,8,32):
    L=2**max(1,round((n/(M+1))**.5/div).bit_length()-1); cs=[]
    for t in range(T):
        rng=random.Random(f'p3-{t}'); ks=[rng.randrange(1,n) for _ in range(M)]
        ops=Ops(E.p,E.a); res,c,d=batch_rho(ops,P,[E.mul(x,P) for x in ks],n,rng,L); assert res==ks; cs.append(c)
    print(bits,M,'div',div,'L',L,'total/sqrt(Mn)',round(st.mean(cs)/(M*n)**.5,2),'per-inst',round(st.mean(cs)/M))
