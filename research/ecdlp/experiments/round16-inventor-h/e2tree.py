import numpy as np, json, sys, heapq, subprocess, math
def feats(x, p):
    cols=[((x>>b)&1) for b in range(32)]
    cols+= [(x*16 < p*i) .astype(np.uint8) for i in range(1,16)]  # x < p*i/16
    return np.stack(cols,1).astype(np.float32)
def ent(c):
    n=c.sum(-1,keepdims=True); q=np.where(c>0,c/np.maximum(n,1),1.0); return -(c*np.log2(q)).sum(-1)
def best_split(X,Y,idx):
    Yi=Y[idx]; ones=X[idx].T@Yi; tot=Yi.sum(0)[None,:]; zeros=tot-ones
    gain=ent(tot)[0]-ent(ones)-ent(zeros)  # total weighted entropy reduction (bits*samples)
    f=int(np.argmax(gain)); return f,float(gain[f])
def build(X,y,C,nodes):
    Y=np.eye(C,dtype=np.float32)[y]; N=len(y)
    tree={}  # node -> dict
    idx=np.arange(N); heap=[]; cnt=1
    tree[0]=dict(idx=idx,leaf=True)
    f,g=best_split(X,Y,idx); heapq.heappush(heap,(-g,0,f))
    while heap and cnt+2<=nodes:
        ng,nid,f=heapq.heappop(heap)
        if -ng<=1e-9: break
        idx=tree[nid]['idx']; m=X[idx,f]>0.5; l,rr=idx[~m],idx[m]
        if len(l)==0 or len(rr)==0: continue
        tree[nid].update(leaf=False,f=f,l=cnt,r=cnt+1); tree[nid].pop('idx')
        for ch,ii in ((cnt,l),(cnt+1,rr)):
            tree[ch]=dict(idx=ii,leaf=True)
            if len(ii)>1:
                ff,gg=best_split(X,Y,ii); heapq.heappush(heap,(-gg,ch,ff))
        cnt+=2
    for n,d in tree.items():
        if d['leaf']: d['cls']=int(np.argmax(np.bincount(y[d['idx']],minlength=C))) if len(d['idx']) else 0
    return tree,cnt
def depth(tree,n=0):
    d=tree[n]; return 0 if d['leaf'] else 1+max(depth(tree,d['l']),depth(tree,d['r']))
def predict(tree,X):
    out=np.zeros(len(X),dtype=np.int64)
    st=[(0,np.arange(len(X)))]
    while st:
        n,idx=st.pop(); d=tree[n]
        if d['leaf']: out[idx]=d['cls']; continue
        m=X[idx,d['f']]>0.5; st.append((d['l'],idx[~m])); st.append((d['r'],idx[m]))
    return out
def wilson(k,n,z=2.576):
    ph=k/n; den=1+z*z/n; c=ph+z*z/(2*n); s=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n)); return (c-s)/den,(c+s)/den
def run(c,planted=False):
    p,r=c['p'],c['r']; H=(r-1)//2; N=min(2**17,r//4)
    fn=f"/tmp/claude-0/e2_{c['bits']}_{c['seed']}.bin"
    subprocess.run(['./e2gen',*map(str,[p,c['a'],c['b'],r,c['Px'],c['Py'],2*N,fn])],check=True)
    D=np.fromfile(fn,dtype=np.uint32).reshape(-1,5).astype(np.int64); kp=D[:,0]; xs=D[:,1:4]
    if planted:  # control: replace low 2 bits of x0 by top 2 bits of k'
        top=((kp-1)*4)//H; xs[:,0]=(xs[:,0]&~3)|top
    X=np.concatenate([feats(xs[:,j],p) for j in range(3)],1)
    tr=D[:,4]==0; te=~tr
    labs={'L1_top4':((kp-1)*16)//H,'L2_mod16':kp%16}
    res={}
    for ln,y in labs.items():
        y=np.clip(y,0,15)
        for nodes in (15,255,4095):
            tree,cnt=build(X[tr],y[tr],16,nodes); pr=predict(tree,X[te]); k=int((pr==y[te]).sum()); n=int(te.sum())
            trk=float((predict(tree,X[tr])==y[tr]).mean()); lo,hi=wilson(k,n)
            res[f"{ln}/{nodes}"]=dict(nodes=cnt,depth=depth(tree),train_acc=trk,test_acc=k/n,n=n,wilson99=[lo,hi],chance=1/16,leak=bool(lo>1/16+0.005))
    return res
if __name__=='__main__':
    curves=json.load(open('curves.json')); out=[]
    sel=[c for c in curves if c['bits']==int(sys.argv[1])]
    for c in sel:
        for planted in (False,True) if c['seed']==0 else (False,):
            r=run(c,planted); out.append(dict(bits=c['bits'],seed=c['seed'],planted=planted,res=r))
            print(c['bits'],c['seed'],planted,{k:(round(v['test_acc'],4),v['leak']) for k,v in r.items()},flush=True)
    json.dump(out,open(f"out_e2_{sys.argv[1]}.json",'w'))
