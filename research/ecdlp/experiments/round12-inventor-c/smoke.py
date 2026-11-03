import random, time
from lib12 import *
from algos import *
for bits in (16, 20, 24):
    E, P, n = find_prime_order_curve(bits, 1)
    print(bits, E.p, n, n.bit_length())
    k = random.Random(5).randrange(1, n); Q = E.mul(k, P)
    assert dlog_bsgs(E, P, Q, n) == k
    L = 2**max(1, round(n**0.5/16).bit_length()-1)
    for name, f in (('ref', rho_ref), ('neg', rho_neg)):
        ops = Ops(E.p, E.a); t=time.time()
        kk, c, info = f(ops, P, Q, n, random.Random(7), L)
        print(name, kk == k, c, round(c/n**0.5,2), time.time()-t)
    ops = Ops(E.p, E.a)
    tb = PreTable(ops, P, n, random.Random(3), int(2*n**(1/3))+1, int(n**(1/3))+1)
    kk, c, t = tb.query(Q, random.Random(9)); print('pre', kk == k, tb.pre_ops, len(tb.table), c, t)
    ks = [random.Random(i).randrange(1, n) for i in range(8)]
    ops = Ops(E.p, E.a)
    res, c, d = batch_rho(ops, P, [E.mul(x, P) for x in ks], n, random.Random(4), 4)
    print('batch', res == ks, c, c/8)
