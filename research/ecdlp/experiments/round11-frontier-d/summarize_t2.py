import json,sys
rows=[json.loads(l) for l in open('out_t2.jsonl') if l.startswith('{')]
tot=0; flags=[]
for d in rows:
    print('p=%d N=%d seed=%d checks=%s lam*N=%d' % (d['p'],d['N'],d['seed'],d['checks'],d['lambda_times_N_mod_p']))
    for name,s in d['seq'].items():
        an=s['anova_F_and_perm_p']; mp=min(v[1] for v in an.values()); tot+=1
        print('   %-8s BM %d/%d holo3=%s holo4=%s minANOVAp=%.5f (m=%s) spec_z=%.2f' % (name,s['BM_L'],s['BM_expect'],s['holo3'][0] if s['holo3'] else None,s['holo4'][0],mp,min(an,key=lambda m:an[m][1]),s['spectral_z']))
        if name not in('pos_lin','pos_kgk'):
            for m,v in an.items():
                if v[1]<0.001/42: flags.append((d['p'],d['seed'],name,m,v))
            if abs(s['spectral_z'])>4: flags.append((d['p'],d['seed'],name,'spec',s['spectral_z']))
    print('   polyfit', {D:[k for k,v in r.items() if v] for D,r in d['polyfit'].items()})
print('FLAGS',flags)
