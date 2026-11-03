"""E5: explicit complexity models (log2 of group-operation-equivalents / bit ops, poly factors dropped, which FAVOURS the
technique) for routes D (direct CNF), (a) index-calculus decomposition, (c) bit-decomposition system, vs Pollard rho.
Inputs: E1 fit (out_q1.json), E4 (N_dec ~ 45.5 (log2 p)^2), E2 paper parameters (eth_params.f).  L = log2 p ~ ell = log2 r.
Usage: python3 route_models.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from eth_params import f as eth_f

q1 = json.load(open(os.path.join(HERE, 'out_q1.json')))
fit = q1['affine_fit']; cD = fit['c']; aD = fit['exponent']; Ndec_c = 45.55

def model_exponent(N):
    lam, nu, r, Q, R, ok, ff = eth_f(math.log2(N))
    return N * (ff if ok and ff < 1 else 1.0), ok, ff     # f:=1 (exhaustive search over all N variables) when the paper's regime is not reached

print('L=log2 p | rho log2 ops | n(ell)=N_D | model log2 time D | headline C=1 | brute force over k (2^ell) | N_dec(m=2) | model log2 T_dec | needed log2 T_dec for beating rho (m>=3 base case)')
rows = []
for L in (64, 128, 256, 384, 521):
    rho = 0.5 * L + math.log2(math.sqrt(math.pi / 4))
    N = cD * L ** aD
    expD, okD, ffD = model_exponent(N)
    head = N / math.sqrt(math.log(N))
    Nd = Ndec_c * L ** 2
    expA, okA, ffA = model_exponent(Nd)
    # route (a), m>=3: total = trials*T_dec + LA, trials = p^{1-(m-1)theta}; with LA = p^{2 theta}; beating rho needs T_dec <= p^{(m-1)theta-1/2}
    need = {m: ((m - 1) / (m + 1) - 0.5) * L for m in (3, 4, 5, 6)}   # theta = 1/(m+1)
    free = {m: 2.0 / (m + 1) * L for m in (2, 3, 4, 5, 6)}          # exponent if decomposition were free
    rows.append(dict(L=L, rho=rho, N_D=N, model_D=expD, headline_D_C1=head, brute_k=L, N_dec=Nd, model_dec=expA, need_log2Tdec=need, free_oracle_log2=free))
    print(L, round(rho, 1), '%.3g' % N, '%.3g' % expD, '%.3g' % head, L, '%.3g' % Nd, '%.3g' % expA, {k: round(v, 1) for k, v in need.items()}, {k: round(v, 1) for k, v in free.items()})
json.dump(rows, open(os.path.join(HERE, 'out_models.json'), 'w'), indent=1)
