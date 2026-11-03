"""Evolutionary search over DSL programs. Usage: evolve.py SEED GENS [seeded]  -> out_evolve_<tag>.json
Training/validation curves only; test curves (seeds >= 200) are never touched here."""
import sys, os, json, random, math, time, hashlib, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsl import *

HERE = os.path.dirname(os.path.abspath(__file__))
POP, TOURN, ELITE = 100, 3, 6
TRAIN = [(tb, sd) for tb in (10, 11, 12) for sd in (0, 1)]
VALID = [(tb, sd) for tb in (10, 11, 12) for sd in (150, 151)]
MAXINIT, MAXBODY = 5, 10
PARSIMONY = 0.003
CAPF = 12.0
SHAPE = 0.3

def rand_instr(rng, first_init=False):
    if first_init and rng.random() < 0.8: name = 'SETC'
    else:
        name = rng.choices(OPS, weights=[6, 6, 2, 2, 2, 1, 3, 4, 6, 6, 4, 2, 1, 3, 3, 2, 3, 2, 3])[0]
    rg = RANGES[name]
    return (OPI[name],) + tuple(rng.randint(lo, hi) for lo, hi in rg)

def rand_prog(rng):
    ni, nbd = rng.randint(1, 4), rng.randint(2, 8)
    return ([rand_instr(rng, j == 0) for j in range(ni)], [rand_instr(rng) for _ in range(nbd)])

def mutate(rng, prog):
    init, body = [list(x) for x in prog[0]], [list(x) for x in prog[1]]
    for _ in range(rng.choice([1, 1, 2, 3])):
        blk, mx = (init, MAXINIT) if rng.random() < 0.3 else (body, MAXBODY)
        m = rng.random()
        if m < 0.45 and blk:
            j = rng.randrange(len(blk)); ins = list(blk[j]); nm = OPS[ins[0]]
            f = rng.randrange(1, 5); lo, hi = RANGES[nm][f - 1]
            if hi > lo:
                ins[f] = min(hi, max(lo, ins[f] + rng.choice([-1, 1]))) if rng.random() < 0.5 else rng.randint(lo, hi)
            blk[j] = tuple(ins)
        elif m < 0.65 and blk:
            blk[rng.randrange(len(blk))] = rand_instr(rng)
        elif m < 0.85 and len(blk) < mx:
            blk.insert(rng.randint(0, len(blk)), rand_instr(rng))
        elif len(blk) > 1:
            blk.pop(rng.randrange(len(blk)))
    return ([tuple(x) for x in init], [tuple(x) for x in body])

def crossover(rng, a, b):
    def cut(x, y, mx):
        i, j = rng.randint(0, len(x)), rng.randint(0, len(y)); return (x[:i] + y[j:])[:mx]
    return (cut(a[0], b[0], MAXINIT), cut(a[1], b[1], MAXBODY))

def score(prog, curves, per, seed, quick=False):
    tot = 0.0; n = 0; ok = 0; hits = 0
    for ci, c in enumerate(curves):
        for k, s in instances(c, per, seed * 31 + ci):
            res, cost, _ = run(prog, c, k, s, CAPF)
            if res == k: tot += cost / math.sqrt(c['r'])
            else: tot += CAPF * (1 - SHAPE * min(1.0, run.last_hits / 5.0))   # shaping: credit for distinct-coefficient x-collisions
            n += 1; ok += res == k; hits += run.last_hits
        if quick and ci == 1 and ok == 0 and hits == 0: return CAPF + PARSIMONY * (len(prog[0]) + len(prog[1])), 0.0
    return tot / n + PARSIMONY * (len(prog[0]) + len(prog[1])), ok / n

def fitness(prog, curves, gen, seed):
    return score(prog, curves, 4, gen * 1000 + seed, quick=True)

def main():
    h = hashlib.sha256(open(os.path.join(HERE, 'PROTOCOL.md'), 'rb').read()).hexdigest()
    assert h == open(os.path.join(HERE, 'PROTOCOL.sha256')).read().split()[0], 'protocol changed'
    seed, gens = int(sys.argv[1]), int(sys.argv[2]); seeded = len(sys.argv) > 3 and sys.argv[3] == 'seeded'
    rng = random.Random(seed)
    train = [make_curve(tb, sd) for tb, sd in TRAIN]; valid = [make_curve(tb, sd) for tb, sd in VALID]
    pop = [rand_prog(rng) for _ in range(POP)]
    if seeded:
        hand = [prog_bsgs(), prog_rho_dp(), prog_rho_floyd_restart(), prog_brute()]
        for i, h in enumerate(hand): pop[i] = h
        for i in range(4, 4 + 16): pop[i] = mutate(rng, hand[i % 4])
    hof = {}; log = []; g0 = 0; prior = 0.0
    tag = f"{'seeded' if seeded else 'random'}_s{seed}"
    ck = os.path.join(HERE, f'ckpt_{tag}.pkl'); budget = float(os.environ.get('SLICE_SECONDS', '1e9'))
    if os.path.exists(ck):
        g0, pop, hof, log, st, prior = pickle.load(open(ck, 'rb')); rng.setstate(st)
    t_start = time.time(); t0 = t_start - prior
    for g in range(g0, gens):
        if os.environ.get('SLICE_SECONDS') and (time.time() - t_start) > budget:
            pickle.dump((g, pop, hof, log, rng.getstate(), time.time() - t0), open(ck, 'wb')); print('slice-saved', tag, g, flush=True); return
        fit = [fitness(p, train, g, seed) for p in pop]
        order = sorted(range(POP), key=lambda i: fit[i][0])
        for i in order[:3]: hof[json.dumps(pop[i])] = pop[i]
        log.append(dict(gen=g, best=fit[order[0]][0], best_succ=fit[order[0]][1], median=fit[order[POP // 2]][0], t=round(time.time() - t0, 1)))
        if g % 5 == 0 or g == gens - 1: print(seed, log[-1], flush=True)
        new = [pop[i] for i in order[:ELITE]]
        while len(new) < POP:
            def tourn(): return min(rng.sample(range(POP), TOURN), key=lambda i: fit[i][0])
            if rng.random() < 0.3: ch = crossover(rng, pop[tourn()], pop[tourn()])
            else: ch = pop[tourn()]
            new.append(mutate(rng, ch) if rng.random() < 0.9 else ch)
        pop = new
    # validation of hall of fame (fresh curves, fresh instances), 10 instances/curve
    cands = list(hof.values())
    vs = sorted(((score(p, valid, 10, 99 + seed)[0], score(p, valid, 10, 99 + seed)[1], p) for p in cands), key=lambda x: x[0])
    top = [dict(val_score=v, val_succ=s, prog=p) for v, s, p in vs[:5]]
    out = dict(protocol_sha256=h, seed=seed, gens=gens, seeded=seeded, pop=POP, log=log, champions=top, elapsed=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(HERE, f'out_evolve_{tag}.json'), 'w'))
    print('champion', tag, top[0]['val_score'], top[0]['val_succ'], flush=True)

if __name__ == '__main__':
    main()
