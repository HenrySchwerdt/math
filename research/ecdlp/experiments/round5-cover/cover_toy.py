#!/usr/bin/env python3
"""Toy numerics for RUN-6a3e20d9 (ECDLP-15). Stdlib only, seeded.
E: y^2=f(x) over F_p, cover C_d: y^2=f(t^d) (fibre product of x:E->P^1 and t->t^d).
Reports: genus (Riemann-Hurwitz), #C(F_p), trace check for d=2, fraction of E(F_p)
fibres splitting completely (relation count) vs factor-base size, and a table of
cost exponents (c=1, illustrative only) for L_{q^g}(1/2) and L_{q^g}(1/3).
"""
import random, math, json, sys
random.seed(20261103)

def legendre_table(p):
    sq = [0]*p
    for y in range(p): sq[y*y % p] += 1   # number of y with y^2 = v
    return sq

def run(p, d):
    sq = legendre_table(p)
    while True:
        a,b,c = (random.randrange(p) for _ in range(3))
        f = lambda x: (x*x*x + a*x*x + b*x + c) % p
        # squarefree cubic with f(0)!=0
        if c == 0: continue
        disc_ok = len({x for x in range(p) if f(x)==0}) == len([x for x in range(p) if f(x)==0])
        # crude squarefree test via gcd of f,f' is skipped; check repeated roots by brute force
        roots = [x for x in range(p) if f(x)==0]
        # discriminant of cubic x^3+ax^2+bx+c
        D = (18*a*b*c - 4*a**3*c + a*a*b*b - 4*b**3 - 27*c*c) % p
        if D == 0: continue
        break
    nE = 1 + sum(sq[f(x)] for x in range(p))             # y^2=f(x) + infinity
    # E2: v^2 = u f(u), quartic monic => 2 points at infinity
    nE2 = 2 + sum(sq[(u*f(u)) % p] for u in range(p))
    # C_d affine points
    nCaff = sum(sq[f(pow(t,d,p))] for t in range(p))
    # points at infinity of smooth model: deg 3d; odd d: 1, even d: 2 (monic)
    ninf = 1 if (3*d) % 2 == 1 else 2
    nC = nCaff + ninf
    g = (3*d-1)//2 if d % 2 else (3*d-2)//2
    # fibres of pi over affine P=(x0,y0), x0!=0: {(t,y0): t^d=x0}
    dth = {}
    for t in range(1,p):
        dth.setdefault(pow(t,d,p), []).append(t)
    full = 0; Eaff = 0
    for x0 in range(1,p):
        for _ in range(sq_count(sq, f(x0))):
            Eaff += 1
            if len(dth.get(x0, [])) == d: full += 1
    out = dict(p=p,d=d,f=[1,a,b,c],genus=g,nE=nE,nE2=nE2,nC=nC,
               trace_check=(nC == nE+nE2-(p+1)) if d==2 else None,
               E_aff_pts_x_nonzero=Eaff, fully_split_fibres=full,
               split_fraction=round(full/max(Eaff,1),4), factor_base_size_C=nC,
               relations_over_unknowns=round(full/nC,4))
    return out

def sq_count(sq, v): return sq[v]

def regime_table():
    rows=[]
    for bits in (64,256,2048):
        L = bits*math.log(2)           # log q in nats
        for name,g in (("g=L/8",L/8),("g=L",L),("g=4L",4*L),("g=L^2",L*L)):
            N = g*L
            e12 = math.sqrt(N*math.log(N))         # c=1, L(1/2)
            e13 = N**(1/3)*math.log(N)**(2/3)      # c=1, L(1/3)
            rows.append(dict(bits=bits,g=name,exp_L12_over_halfL=round(e12/(L/2),2),
                             exp_L13_over_halfL=round(e13/(L/2),2)))
    return rows

if __name__ == "__main__":
    res = []
    for p in (1021, 4093, 10009):          # 1021, 4093 =1 mod 12? (checked below)
        for d in (2,3,4,6):
            if (p-1) % d == 0:
                res.append(run(p,d))
    for r in res: print(json.dumps(r))
    print("REGIME (ratio exponent / (log q /2); >1 means cost > sqrt(q); c=1 illustrative)")
    for r in regime_table(): print(json.dumps(r))
