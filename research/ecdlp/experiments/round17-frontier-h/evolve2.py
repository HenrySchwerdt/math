"""Round 17 evolutionary search over the field-arithmetic DSL. Usage: evolve2.py TAG SEED GENS [seeded]
Time-sliced: SLICE_SECONDS env; checkpoint/resume. Training/validation curves only (held-out seeds never touched)."""
import sys, os, json, random, math, time, hashlib, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl2 import *
HERE = os.path.dirname(os.path.abspath(__file__))
POP, TOURN, ELITE = 100, 3, 6
TRAIN = [(tb, sd) for tb in (10, 11, 12) for sd in (500, 501)]
VALID = [(tb, sd) for tb in (10, 11, 12) for sd in (550, 551)]
MAXINIT, MAXBODY = 5, 10
PARSIMONY, CAPF, SHAPE, SLOPEW = 0.003, 12.0, 0.3, 1.0
W_OLD = [6, 6, 2, 2, 2, 1, 3, 4, 6, 6, 4, 2, 1, 3, 3, 2, 3, 2, 3]
W_NEW = [2, 1, 2, 3, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 3, 2, 2]   # FCTR..MSOLVE (17 entries)
WEIGHTS = W_OLD + W_NEW[:len(OPS) - 19]
_CTRL = {}
def ctrl_mean(c):
    key = (c['tb'], c['seed'])
    if key not in _CTRL:
        tot = 0.0
        for k, s in instances(c, 40, 77): tot += run(prog_rho_dp(), c, k, s, CAPF)[1]
        _CTRL[key] = tot / 40
    return _CTRL[key]

def rand_instr(rng, first_init=False):
    name = 'SETC' if (first_init and rng.random() < 0.6) else rng.choices(OPS, weights=WEIGHTS)[0]
    return (OPI[name],) + tuple(rng.randint(lo, hi) for lo, hi in RANGES[name])
def rand_prog(rng):
    return ([rand_instr(rng, j == 0) for j in range(rng.randint(1, 4))], [rand_instr(rng) for _ in range(rng.randint(2, 8))])
def mutate(rng, prog):
    init, body = [list(x) for x in prog[0]], [list(x) for x in prog[1]]
    for _ in range(rng.choice([1, 1, 2, 3])):
        blk, mx = (init, MAXINIT) if rng.random() < 0.3 else (body, MAXBODY)
        m = rng.random()
        if m < 0.45 and blk:
            j = rng.randrange(len(blk)); ins = list(blk[j]); nm = OPS[ins[0]]; f = rng.randrange(1, 5); lo, hi = RANGES[nm][f - 1]
            if hi > lo: ins[f] = min(hi, max(lo, ins[f] + rng.choice([-1, 1]))) if rng.random() < 0.5 else rng.randint(lo, hi)
            blk[j] = tuple(ins)
        elif m < 0.65 and blk: blk[rng.randrange(len(blk))] = rand_instr(rng)
        elif m < 0.85 and len(blk) < mx: blk.insert(rng.randint(0, len(blk)), rand_instr(rng))
        elif len(blk) > 1: blk.pop(rng.randrange(len(blk)))
    return ([tuple(x) for x in init], [tuple(x) for x in body])
def crossover(rng, a, b):
    def cut(x, y, mx):
        i, j = rng.randint(0, len(x)), rng.randint(0, len(y)); return (x[:i] + y[j:])[:mx]
    return (cut(a[0], b[0], MAXINIT), cut(a[1], b[1], MAXBODY))

def score(prog, curves, per, seed, quick=False):
    """fitness (minimised) = mean over sizes of cost/rho_dp-control-cost-on-same-curve + SLOPEW*(ratio_top - ratio_bottom)
    + parsimony.  Unsolved: cap-cost with shaping credit. Returns (fitness, success_rate, per-size ratios)."""
    by = {}; ok = 0; n = 0; hits = 0
    for ci, c in enumerate(curves):
        cm = ctrl_mean(c)
        for k, s in instances(c, per, seed * 31 + ci):
            res, cost, _ = run(prog, c, k, s, CAPF)
            if res == k: v = cost / cm
            else: v = CAPF * math.sqrt(c['r']) * (1 - SHAPE * min(1.0, run.last_hits / 5.0)) / cm
            by.setdefault(c['tb'], []).append(v); n += 1; ok += res == k; hits += run.last_hits
        if quick and ci == 1 and ok == 0 and hits == 0:
            return 99.0 + PARSIMONY * (len(prog[0]) + len(prog[1])), 0.0, {}
    ratios = {tb: sum(v) / len(v) for tb, v in by.items()}; ts = sorted(ratios)
    f = sum(ratios.values()) / len(ratios) + SLOPEW * (ratios[ts[-1]] - ratios[ts[0]]) + PARSIMONY * (len(prog[0]) + len(prog[1]))
    return f, ok / n, ratios

def main():
    h = hashlib.sha256(open(os.path.join(HERE, 'PROTOCOL.md'), 'rb').read()).hexdigest()
    assert h == open(os.path.join(HERE, 'PROTOCOL.sha256')).read().split()[0], 'protocol changed'
    tag, seed, gens = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); seeded = len(sys.argv) > 4 and sys.argv[4] == 'seeded'
    rng = random.Random(seed)
    train = [make_curve(tb, sd) for tb, sd in TRAIN]; valid = [make_curve(tb, sd) for tb, sd in VALID]
    pop = [rand_prog(rng) for _ in range(POP)]
    if seeded:
        hand = [prog_rho_dp(), prog_bsgs(), prog_ic_ms(), prog_rho_floyd_restart()]
        for i, hp in enumerate(hand): pop[i] = hp
        for i in range(4, 20): pop[i] = mutate(rng, hand[i % 4])
    hof = {}; log = []; g0 = 0; prior = 0.0
    ck = os.path.join(HERE, 'cache', f'ckpt_{tag}.pkl'); budget = float(os.environ.get('SLICE_SECONDS', '1e9'))
    if os.path.exists(ck): g0, pop, hof, log, st, prior = pickle.load(open(ck, 'rb')); rng.setstate(st)
    t_start = time.time(); t0 = t_start - prior
    for g in range(g0, gens):
        if os.environ.get('SLICE_SECONDS') and (time.time() - t_start) > budget:
            pickle.dump((g, pop, hof, log, rng.getstate(), time.time() - t0), open(ck, 'wb')); print('slice-saved', tag, g, flush=True); return
        fit = [score(p, train, 4, g * 1000 + seed, quick=True) for p in pop]
        order = sorted(range(POP), key=lambda i: fit[i][0])
        for i in order[:3]: hof[json.dumps(pop[i])] = pop[i]
        log.append(dict(gen=g, best=fit[order[0]][0], best_succ=fit[order[0]][1], median=fit[order[POP // 2]][0], t=round(time.time() - t0, 1)))
        if g % 5 == 0 or g == gens - 1: print(tag, log[-1], flush=True)
        new = [pop[i] for i in order[:ELITE]]
        while len(new) < POP:
            def tourn(): return min(rng.sample(range(POP), TOURN), key=lambda i: fit[i][0])
            ch = crossover(rng, pop[tourn()], pop[tourn()]) if rng.random() < 0.3 else pop[tourn()]
            new.append(mutate(rng, ch) if rng.random() < 0.9 else ch)
        pop = new
    vs = []
    for p in hof.values():
        a = score(p, valid, 10, 99 + seed); vs.append((a[0], a[1], a[2], p))
    vs.sort(key=lambda x: x[0])
    top = [dict(val_score=v, val_succ=s, val_ratios=rt, prog=p) for v, s, rt, p in vs[:5]]
    json.dump(dict(protocol_sha256=h, tag=tag, seed=seed, gens=gens, seeded=seeded, pop=POP, log=log, champions=top, elapsed=round(time.time() - t0, 1)),
              open(os.path.join(HERE, f'out_evolve_{tag}.json'), 'w'))
    print('champion', tag, top[0]['val_score'], top[0]['val_succ'], flush=True)
if __name__ == '__main__': main()
