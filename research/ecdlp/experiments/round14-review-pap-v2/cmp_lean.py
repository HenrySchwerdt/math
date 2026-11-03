import re,sys
tex=open('research/ecdlp/papers/PAP-ef6e2010-7950-47cf-bb75-05801891905b/main.tex',encoding='utf8').read()
blocks=re.findall(r'\\begin\{lstlisting\}\n(.*?)\\end\{lstlisting\}',tex,re.S)
src={f:open(f,encoding='utf8').read() for f in ['MathResearch/ECDLP/CurveX.lean','MathResearch/ECDLP/LinearInterp.lean','MathResearch/ECDLP/PartialAgreement.lean','MathResearch/ECDLP/SLPBound.lean','MathResearch/ECDLP/RationalSLP.lean','MathResearch/ECDLP/DecisionTree.lean']}
norm=lambda s:re.sub(r'\s+',' ',s).strip()
for b in blocks:
    nb=norm(b); found=[f for f,s in src.items() if nb in norm(s.replace(':= by','').replace(':=','')) or nb in norm(s)]
    # statement ends before ':= by' 
    found=[]
    for f,s in src.items():
        ns=norm(s)
        if nb+' := by' in ns or nb+' :=' in ns: found.append(f)
    print(nb[:60],'->',found)
