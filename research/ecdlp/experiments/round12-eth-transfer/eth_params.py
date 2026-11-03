"""E2: explicit-constant cost model of the source paper's counting algorithm (preprint, OpenAI,
'The Exponential Time Hypothesis is False', 25 Oct 2026; external, NOT peer reviewed, NOT verified by us).

We instantiate ONLY the paper's own displayed parameter choice (Lemma 4.8, eq. 4.17, beta = 1 = most favourable)
and its own cost decomposition (eq. 2.11):
    cost = sum_{j<=q} C(n,j) 2^j  *  (2D+1)^{2 tau n}  *  r 2^{2n/r}      (times poly(n))
with  lambda = ceil(log2 n), nu = ceil(log2 lambda), r = floor(sqrt(lambda)/nu^2), Q = floor(lambda/(128 nu)),
R = (beta+3) ceil(sqrt(lambda)), tau = 1/(r lambda), D = r^(2Q), q = floor(3 n R / Q).
f(lambda) := log2(cost)/n = (3R/Q) log2(2eQ/(3R)) + 2 tau (2Q log2 r + 1) + 2/r
(polynomial factors dropped, which FAVOURS the algorithm). Hidden constants of the paper's O() are replaced by
these displayed values. Numerical hypotheses we can check: r>=2, R>=32, 6R<=Q.
Usage: python3 eth_params.py
"""
import math, json

def params(lam_real, beta=1):
    lam = math.ceil(lam_real)
    nu = math.ceil(math.log2(lam)) if lam > 1 else 1
    r = math.floor(math.sqrt(lam) / nu ** 2)
    Q = math.floor(lam / (128 * nu))
    R = (beta + 3) * math.ceil(math.sqrt(lam))
    ok = (r >= 2 and Q >= 1 and R >= 32 and 6 * R <= Q)
    return lam, nu, r, Q, R, ok

def f(lam_real, beta=1):
    lam, nu, r, Q, R, ok = params(lam_real, beta)
    if r < 1 or Q < 1:
        return lam, nu, r, Q, R, ok, float('inf')
    tau = 1.0 / (r * lam)
    log2D = 2 * Q * math.log2(r) if r > 1 else 0.0
    a = 3.0 * R / Q
    t1 = a * math.log2(2 * math.e / a) if a < 2 * math.e else float('inf')
    t2 = 2 * tau * (log2D + 1)
    t3 = 2.0 / r
    return lam, nu, r, Q, R, ok, t1 + t2 + t3

def first_lambda(pred, lo=2.0, hi=1e40):
    lam = lo
    while lam < hi:
        if pred(lam):
            return lam
        lam *= 1.0005
    return None

if __name__ == '__main__':
    out = {}
    out['first_log2n_numerical_hypotheses_hold'] = first_lambda(lambda l: params(l)[5])
    for thr in (1.0, 0.5, 0.25, 0.1):
        out['first_log2n_with_hyp_and_f_below_%s' % thr] = first_lambda(lambda l: params(l)[5] and f(l)[6] < thr)
    rows = []
    for lam in (50, 1e3, 1e5, 1e6, 1e8, 1e10, 1e12, 1e15, 1e20, 1e30):
        lam_i, nu, r, Q, R, ok, ff = f(lam)
        rows.append(dict(log2n=lam, nu=nu, r=r, Q=Q, R=R, hypotheses_ok=ok, f=ff))
    out['table'] = rows
    print(json.dumps(out, indent=1, default=str))
