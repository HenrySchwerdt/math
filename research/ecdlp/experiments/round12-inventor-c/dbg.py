import random
from lib12 import *
from algos import *
E,P,n = find_prime_order_curve(16,1)
ks=[random.Random(i).randrange(1,n) for i in range(8)]
ops=Ops(E.p,E.a)
res,c,d=batch_rho(ops,P,[E.mul(x,P) for x in ks],n,random.Random(4),4)
print(ks,res)
