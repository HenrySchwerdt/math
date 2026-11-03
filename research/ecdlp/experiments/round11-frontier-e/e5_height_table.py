import math
print('Miller-height arithmetic: need T >= p^(2/rho) (natural-log canonical height), numerator bits ~ T/ln2')
print('heuristic count of E(Q) points with height<=T taken as T^(rho/2) (regulator/torsion constants set to 1)')
print('rho  | log2 p | log2 T needed | numerator bits = 2^(.) | ratio bits/log2(p)')
for lp in (64, 160, 256):
    for rho in (1, 2, 5, 10, 18, 29):
        lT = (2.0 / rho) * lp                    # log2 T
        bits_log2 = lT - math.log2(math.log(2))  # log2(T/ln2)
        print(f'{rho:3d}  | {lp:6d} | {lT:12.1f}  | 2^{bits_log2:10.1f}        | 2^{bits_log2 - math.log2(lp):.1f}')
print('Interpretation: rho=1 (e.g. multiples nP): T=p^2, numerators of 2^(2*lp) bits? (n~p => height n^2 h, bits ~ p^2)')
