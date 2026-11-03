# TUNING PILOT for C2/C3 (seed namespace 'pilot')
import random, sys, time, statistics as st
from lib12 import *
from algos import *
bits = int(sys.argv[1]); Qn = int(sys.argv[2])
E, P, n = find_prime_order_curve(bits, 'pilot')
c3 = n**(1/3)
for mf, lf in ((1,1),(2,1),(1,0.5),(0.5,2),(2,0.5)):
    ops=Ops(E.p,E.a); t=time.time()
    tb=PreTable(ops,P,n,random.Random('pilot-pre'),int(mf*c3)+1,max(2,int(lf*c3)))
    on=[]; 
    for i in range(Qn):
        rng=random.Random(f'pq-{i}'); k=rng.randrange(1,n); Q=E.mul(k,P)
        kk,c,r=tb.query(Q,rng); assert kk==k; on.append(c)
    print(bits,'m',mf,'L',lf,'pre',tb.pre_ops, 'dps',len(tb.table),'online mean',round(st.mean(on),1),'/n^1/3',round(st.mean(on)/c3,2), 'S*T^2/n', round(len(tb.table)*st.mean(on)**2/n,2), round(time.time()-t,1),'s')
