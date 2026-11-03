import json, math
rows = [json.loads(l) for l in open('learn_out.jsonl')]
for kind in ['ecdlp', 'control_identity', 'control_xparity']:
    tot = 0; flags = []; maxgap = -9
    for d in rows:
        for lab, v in d[kind].items():
            thr = 4 * math.sqrt(0.25 / v['n_test'])
            for mdl in ('logreg', 'mlp'):
                tot += 1; gap = v[mdl] - v['majority_baseline']
                maxgap = max(maxgap, gap)
                if gap > thr: flags.append((d['p'], d['r'], lab, mdl, v[mdl], v['majority_baseline']))
    print(kind, 'tests', tot, 'flags', len(flags), 'max(acc-baseline)=%.4f' % maxgap)
    if kind != 'ecdlp': 
        print('   flagged labels (first 6):', flags[:6])
    else: print('  ', flags)
print([(d['p'], d['r']) for d in rows])
