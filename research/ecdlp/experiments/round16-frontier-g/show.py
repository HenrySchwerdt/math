import json,sys,glob
from dsl import OPS
for f in sorted(glob.glob('out_eval_*.json')):
    for n,v in json.load(open(f))['results'].items():
        if n in('bsgs','rho_floyd','rho_dp','brute') and 'baselines' not in f: continue
        a=v['testA']; print(n,'beta %.3f ci99 [%.3f,%.3f]'%(a['beta'],*a['ci99']),'c/sqrt',[round(x,2) for x in a['cost_over_sqrt_r']],'succ',[round(x,2) for x in a['success'].values()],'B beta %.3f'%v['testB']['beta'],[round(x,2) for x in v['testB']['success'].values()])
        if '--prog' in sys.argv and n not in('bsgs','rho_floyd','rho_dp','brute'):
            for blk,nm in zip(v['prog'],('init','body')):
                print('  ',nm,[ (OPS[i[0]],)+tuple(i[1:]) for i in blk])
