# TUNING PILOT (seed namespace 'pilot'; not part of the pre-registered benchmark)
import random, sys, time, statistics as st
from lib12 import *
from algos import *
bits = int(sys.argv[1]); T = int(sys.argv[2])
E, P, n = find_prime_order_curve(bits, 'pilot')
def Lfor(div): return 2**max(1, round(n**0.5/div).bit_length()-1)
for div in (4, 16, 64):
    for name, f in (('ref', rho_ref), ('neg', rho_neg)):
        cs=[]
        for t in range(T):
            rng=random.Random(f'pilot-{bits}-{t}'); k=rng.randrange(1,n); Q=E.mul(k,P)
            ops=Ops(E.p,E.a); kk,c,_=f(ops,P,Q,n,random.Random(f'w-{t}'),Lfor(div)); assert kk==k; cs.append(c)
        print(bits,name,'div',div,'L',Lfor(div),'mean/sqrt(n)',round(st.mean(cs)/n**.5,3))
