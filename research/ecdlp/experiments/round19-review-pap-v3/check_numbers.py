#!/usr/bin/env python3
"""Mechanically check numbers in the v3 obstruction-map section against the cited HYP records."""
import re, glob, json, sys
ROOT='research/ecdlp/'
TEX=ROOT+'papers/PAP-ef6e2010-7950-47cf-bb75-05801891905b/main.tex'
tex=open(TEX).read()
start=tex.index(r'\section{Obstruction map'); end=tex.index(r'\section{Limitations}')
sec=tex[start:end]
def corpus(h8):
    t=''
    for f in glob.glob(ROOT+'hypotheses/HYP-%s*'%h8):
        t+=open(f).read()
    return t
def norm(s):
    s=s.replace('{,}','').replace('\\,','').replace('$','').replace('\\cdot10^','e').replace('--','-')
    s=re.sub(r'(\d),(\d{3})',r'\1\2',s)
    return s
def nums(s):
    s=norm(s)
    out=set()
    for m in re.finditer(r'(?<![\w.])-?\d+(?:\.\d+)?',s):
        out.add(m.group(0).lstrip('-'))
    return out
# split into subsections
parts=re.split(r'(?=\\subsection\{|\\paragraph\{Methodological|\\paragraph\{Reading)',sec)
total=0;bad=[]
for p in parts:
    title=p[:60].replace('\n',' ')
    hs=sorted(set(re.findall(r'HYP-([0-9a-f]{8})',p)))
    if not hs: continue
    # per-paragraph attribution: split at \\ (textbf blocks), each block checked against HYPs cited in that block, else the subsection
    blocks=re.split(r'\\\\\n',p)
    sub=set(hs)
    for b in blocks:
        bh=sorted(set(re.findall(r'HYP-([0-9a-f]{8})',b))) or sorted(sub)
        c=norm(corpus_text:=''.join(corpus(h) for h in bh))
        cn=nums(c)
        # strip cite keys/ids from block
        bb=re.sub(r'HYP-[0-9a-f]{8}|ECDLP-\d+|REV-[0-9a-f]{8}|RUN-[0-9a-f-]+|\\cite\{[^}]*\}|\\ref\{[^}]*\}|round~?\d+|Section~\S+','',b)
        for n in sorted(nums(bb)):
            total+=1
            if n not in cn: bad.append((title,bh,n))
print('numbers checked',total,'unmatched',len(bad))
cur=None
for t,bh,n in bad:
    if t!=cur: print('\n##',t,bh); cur=t
    print(n,end='  ')
print()
