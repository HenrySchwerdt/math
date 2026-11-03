"""F3: exponent accounting (units of log_p). Ambient group order N = p^g (g>=1), base size s, relation length m.
Supply s^m/N >= s  =>  s = p^{g/(m-1)}.  Costs: unknowns/linear algebra (sparse, Wiedemann) ~ m s^2;
generic list-merge relation finder (enumerate all closed m-tuples by meet-in-the-middle) ~ s^{ceil(m/2)}.
Algebraic finders (Cantor/Groebner) are NOT modelled here: they change only the finder term, never s or s^2.
Prints min over m of max(linalg, finder) per g, and the floor from linalg alone (2g/(m-1))."""
from math import ceil
for g in (1, 2, 3, 4):
    best = None
    rows = []
    for m in range(g+1, 60):
        e_s = g/(m-1)
        la = 2*e_s
        fin = ceil(m/2)*e_s
        tot = max(la, fin, e_s)
        rows.append((m, round(e_s, 4), round(la, 4), round(fin, 4), round(tot, 4)))
        if best is None or tot < best[-1]: best = rows[-1]
    print('g=%d  best (m, exp s, exp linalg, exp finder, total) = %s' % (g, best))
    print('     m=2,3,4,5,8,16,59 :', [r for r in rows if r[0] in (2, 3, 4, 5, 8, 16, 59)])
