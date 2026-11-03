#!/usr/bin/env python3
"""Spot-check paper numbers against raw experiment outputs (round12-19). Prints PASS/FAIL per item."""
import re
E='research/ecdlp/experiments/'
def rd(p): return open(E+p).read()
checks=[
 ('D: D2a/rho 11,94,633,2533 at 16,20,24,28 bits','round13-inventor-d/analysis.txt',[r'coset 16 .* 11 0\.47',r'coset 20 .* 94 0\.46',r'coset 24 .* 633 0\.42',r'coset 28 .* 2533 0\.21']),
 ('D: exponent 0.99 [0.92,1.06] (pre-registered 16-24 coset)','round13-inventor-d/analysis.txt',[r'coset pre-registered 16-24: alpha_total=0\.989.*CI\[0\.921,1\.056\]']),
 ('D: D2b 1.075','round13-inventor-d/analysis.txt',[r'D2b.*alpha_total=1\.075']),
 ('F: exponent 0.651 [0.642,0.661]; 8.6x@16; 36x@30','round15-inventor-f/analysis.txt',[r'alpha=0\.651 \[0\.642, 0\.661\]',r'^16 .* 8\.6 ',r'^30 .* 36\.2 ']),
 ('I: beta 0.405[0.37,0.45]; wall 0.475[0.44,0.52]; tower 0.585[0.55,0.64]; slopes 0.203/0.595','round18-inventor-i/analysis.txt',[r'beta=0\.405 CI95 \[0\.37,0\.45\]',r'beta=0\.475 CI95 \[0\.44,0\.52\]',r'beta=0\.585 CI95 \[0\.55,0\.64\]',r'0\.2026',r'0\.5953']),
 ('G(inventor): ywin ratio 4.86..25.97, slope 0.29 [0.27,0.32]','round16-inventor-g/analysis.txt',[r'cbrt  ywin  bits 14 .* ratio 4\.86',r'cbrt  ywin  bits 22 .* ratio 25\.97',r'0\.2949.*0\.2652.*0\.3246']),
 ('A: 42.7x and 28.9x at 24 bits','round12-inventor-a/analysis.txt',[r'\| 24 \|.*42\.7 \| 28\.9']),
 ('B1: slopes aut 0.437 / 0.451; ratios 1.45 [1.14,1.88], 2.62 [2.15,3.17]','round12-inventor-b/analysis.txt',[r'aut\s+slope 0\.437',r'aut\s+slope 0\.451',r'1\.45 CI \[1\.14,1\.88\]',r'2\.62 CI \[2\.15,3\.17\]']),
 ('B2: overhead share 0.6->0.03; iso slope 1.864','round12-inventor-b/analysis.txt',[r'overhead share \[0\.6, 0\.42, 0\.14, 0\.08, 0\.03\]',r'slope 1\.864']),
]
bad=0
for name,f,pats in checks:
    t=rd(f)
    for p in pats:
        ok=re.search(p,t,re.M) is not None
        bad+=not ok
        print('PASS' if ok else 'FAIL',name,'|',p)
print('failures',bad)
