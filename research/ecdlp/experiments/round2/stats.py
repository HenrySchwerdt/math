"""Stdlib statistics helpers for round2 (chi-square sf, normal, KS) with self-test."""
import math


def gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a, x)."""
    if x <= 0:
        return 1.0
    lg = -x + a * math.log(x) - math.lgamma(a)
    if x < a + 1:
        term = 1.0 / a
        s = term
        n = a
        for _ in range(100000):
            n += 1
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-16:
                break
        return max(0.0, 1.0 - s * math.exp(lg))
    tiny = 1e-300
    b = x + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 100000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return math.exp(lg) * h


def chi2_sf(x, df):
    return gammaincc(df / 2.0, x / 2.0)


def norm_two_sided(z):
    return math.erfc(abs(z) / math.sqrt(2))


def max_exp_p(t, M):
    """P(max of M iid Exp(1) >= t)."""
    return -math.expm1(M * math.log1p(-math.exp(-t))) if t > 0 else 1.0


def ks_uniform(ps):
    """Return (D, asymptotic p-value) of the KS test of ps against U(0,1)."""
    xs = sorted(ps)
    n = len(xs)
    D = max(max((i + 1) / n - x, x - i / n) for i, x in enumerate(xs))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * D
    if lam < 1e-9:
        return D, 1.0
    q = 2 * sum((-1) ** (j - 1) * math.exp(-2 * j * j * lam * lam) for j in range(1, 200))
    return D, min(1.0, max(0.0, q))


def selftest():
    assert abs(chi2_sf(5.991464547, 2) - 0.05) < 1e-6
    assert abs(chi2_sf(3.841458821, 1) - 0.05) < 1e-6
    assert abs(chi2_sf(14.06714045, 7) - 0.05) < 1e-6
    assert abs(chi2_sf(12.5916, 6) - 0.05) < 1e-4
    assert abs(chi2_sf(1.0, 3) - 0.8012525) < 1e-6
    assert abs(chi2_sf(40.0, 3) - 1.0e-8) < 2e-9 or chi2_sf(40.0, 3) < 2e-8
    assert abs(norm_two_sided(1.959964) - 0.05) < 1e-6
    assert abs(max_exp_p(math.log(100), 1) - 0.01) < 1e-12
    return True


if __name__ == '__main__':
    print('stats selftest', selftest())
