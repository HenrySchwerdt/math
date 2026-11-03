import sys, random, json, itertools
sys.path.insert(0,'.')
from common import *
from math import comb
import numpy as np
res=[]
curves=find_curves(4096,6000,4,'A')
for ci,(E,P,r) in enumerate(curves):
    xs,ys=chain(E,P,r)
    for d,sizes in ((2,(40,80,160)),(3,(12,24,40))):
        for s in sizes:
            ratios=[]
            for draw in range(5):
                rng=random.Random(f'A-{ci}-{d}-{s}-{draw}')
                B=rng.sample(range(1,r),s)           # logs of base points
                sums={}
                for ms in itertools.combinations_with_replacement(B,d):
                    g=sum(ms)%r
                    sums[g]=sums.get(g,0)+1
                obs=sum(c*(c-1)//2 for c in sums.values())
                M=comb(s+d-1,d)
                pred=comb(M,2)/r
                ratios.append(obs/pred)
            res.append(dict(curve=ci,p=E.p,r=r,d=d,s=s,mean_ratio=float(np.mean(ratios)),sd=float(np.std(ratios,ddof=1)),n=5,pred=pred))
tab={}
for x in res: tab.setdefault((x['d'],x['s']),[]).append(x['mean_ratio'])
for k,v in sorted(tab.items()):
    print('d=%d s=%d  mean obs/pred over 4 curves x5 draws = %.3f (min %.3f max %.3f)'%(k[0],k[1],np.mean(v),min(v),max(v)))
json.dump(res,open('expA_results.json','w'),indent=1)
