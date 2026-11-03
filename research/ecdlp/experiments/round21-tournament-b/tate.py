import numpy as np
from common import chain

def phi_all(E, P, r, as_list=True):
    """Phi[k] = f_{r,P}(kP) (normalised Miller function) for k=0..r-1; -1 where undefined/tangent-degenerate (k=0,1 and flagged)."""
    p, a = E.p, E.a
    xs, ys = chain(E, P, r)
    inv = np.zeros(p, dtype=np.int64)
    for i in range(1, p): inv[i] = pow(i, -1, p)
    xR, yR = xs.copy(), ys.copy()
    valid = np.ones(r, dtype=bool); valid[0] = False; valid[1] = False
    m = np.zeros(r, dtype=np.int64)
    idx = np.where(valid)[0]
    m[idx] = (3 * xR[idx] * xR[idx] + a) % p * inv[(2 * yR[idx]) % p] % p
    num = np.ones(r, dtype=np.int64); den = np.ones(r, dtype=np.int64)
    nz = np.zeros(r, dtype=np.int64); dz = np.zeros(r, dtype=np.int64); bad = np.zeros(r, dtype=bool)
    x1, y1 = int(xs[1]), int(ys[1])
    for j in range(1, r):
        # numerator: line through jP and P
        if j == r - 1:
            na = (xR - x1) % p; nb = np.ones(r, dtype=np.int64)
        else:
            xj, yj = int(xs[j]), int(ys[j])
            if j == 1:
                lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
            else:
                lam = (yj - y1) * pow(xj - x1, -1, p) % p
            na = (yR - yj - lam * (xR - xj)) % p
            nb = (m - lam) % p
        z = (na == 0)
        z2 = z & (nb == 0)
        bad |= z2
        nz += z
        num = num * np.where(z, nb, na) % p
        if j + 1 <= r - 1:
            da = (xR - int(xs[j + 1])) % p
            zd = (da == 0)
            dz += zd
            den = den * np.where(zd, 1, da) % p
    bad |= (nz != dz)
    phi = num * inv[den % p] % p
    out = phi.copy(); out[~valid | bad] = -1
    return [None if v < 0 else v for v in out.tolist()] if as_list else (out, int((valid & bad).sum()))
