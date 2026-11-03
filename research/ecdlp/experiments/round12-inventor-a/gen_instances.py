import sys, json
from common import *
b = int(sys.argv[1])
with open(os.path.join(HERE, f'instances_{b}.jsonl'), 'w') as f:
    for s in seeds_for(b):
        d = gen_instance(b, s)
        assert d['r'] > 0 and is_prime(d['r'])
        f.write(json.dumps(d) + '\n')
print('done', b)
