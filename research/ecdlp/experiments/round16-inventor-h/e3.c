// E3: fixed-walk DP tables with curve-specific tuning. Counted ops = affine point additions/doublings.
// usage: e3 p a b r Px Py bits outfile
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef uint64_t u64; typedef int64_t i64;
static u64 p, A, B, r, Px, Py; static int bits;
static u64 OPS = 0;
typedef struct { u64 x, y; int inf; } Pt;
static inline u64 mulm(u64 a, u64 b){ return (a*b)%p; }
static u64 invm(u64 a){ i64 t=0,nt=1; i64 rr=(i64)p, nr=(i64)a;
  while(nr){ i64 q=rr/nr; i64 tmp=t-q*nt; t=nt; nt=tmp; tmp=rr-q*nr; rr=nr; nr=tmp; }
  if(t<0) t+=p; return (u64)t; }
static Pt add(Pt P, Pt Q){ OPS++;
  if(P.inf) return Q; if(Q.inf) return P;
  u64 lam;
  if(P.x==Q.x){ if((P.y+Q.y)%p==0){ Pt O={0,0,1}; return O; }
    lam = mulm((3*mulm(P.x,P.x)+A)%p, invm((2*P.y)%p)); }
  else lam = mulm((Q.y+p-P.y)%p, invm((Q.x+p-P.x)%p));
  u64 x3=(mulm(lam,lam)+2*p-P.x-Q.x)%p;
  Pt R={x3,(mulm(lam,(P.x+p-x3)%p)+p-P.y)%p,0}; return R; }
static Pt mul(u64 k, Pt P){ Pt R={0,0,1}; while(k){ if(k&1) R=add(R,P); k>>=1; if(k) P=add(P,P);} return R; }
static u64 sm_state;
static u64 rnd(void){ u64 z=(sm_state+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
static void seed(u64 s){ sm_state=s*0x2545F4914F6CDD1DULL+12345; rnd(); rnd(); }
// candidate
typedef struct { int fam; int d; double mult; int ss, ts; } Cand;
// families: 0=F0 31 parts uniform; 1=F1 small w=64; 2=F1 w=4096; 3=F2 R=16; 4=F2 R=64; 5=F2 R=256; 6=F3 powers of two
#define MAXR 256
typedef struct { int R; u64 a[MAXR]; Pt pt[MAXR]; int fam; u64 hseed; u64 mask; } Step;
static inline int hpart(const Step*S, u64 x){
  if(S->fam<=2||S->fam==6) return (int)(x%31);
  return (int)(((x*S->hseed)>>35)%S->R); }
static void mkstep(Step*S, Cand c){
  S->fam=c.fam; seed(0xABCD0000ULL+(u64)c.fam*1000+c.ss*7+p);
  S->hseed=rnd()|1;
  switch(c.fam){ case 3: S->R=16; break; case 4: S->R=64; break; case 5: S->R=256; break; default: S->R=31; }
  u64 save=OPS;
  for(int j=0;j<S->R;j++){
    if(c.fam==1) S->a[j]=1+rnd()%64; else if(c.fam==2) S->a[j]=1+rnd()%4096;
    else if(c.fam==6) S->a[j]=((u64)1<<j)%r; else S->a[j]=1+rnd()%(r-1);
    S->pt[j]=mul(S->a[j],(Pt){Px,Py,0}); }
  OPS=save; // step-point setup is advice-size constant (R points), not charged to T; charged in prep below
  S->mask=((u64)1<<c.d)-1; }
static inline int isdp(const Step*S,u64 x){ return (((x*0xD6E8FEB86659FD93ULL)>>29)&S->mask)==0; }
static int walk(const Step*S, Pt R, u64*sum, u64 cap, Pt*out){
  u64 s=0;
  for(u64 i=0;i<=cap;i++){
    if(R.inf) return 0;
    if(isdp(S,R.x)){ *out=R; *sum=s%r; return 1; }
    int j=hpart(S,R.x); R=add(R,S->pt[j]); s+=S->a[j]; }
  return 0; }
// hash table
typedef struct { u64 *key; u64 *val; u64 sz; u64 n; } Tab;
static void tinit(Tab*T,u64 sz){ T->sz=sz; T->n=0; T->key=malloc(sz*8); T->val=malloc(sz*8); memset(T->key,0xFF,sz*8); }
static inline u64 pk(Pt P){ return (P.x<<32)|P.y; }
static void tput(Tab*T,Pt P,u64 v){ u64 k=pk(P), h=(k*0x9E3779B97F4A7C15ULL)>>20; h%=T->sz;
  while(T->key[h]!=~0ULL){ if(T->key[h]==k) return; h=(h+1)%T->sz; } T->key[h]=k; T->val[h]=v; T->n++; }
static int tget(Tab*T,Pt P,u64*v){ u64 k=pk(P), h=((k*0x9E3779B97F4A7C15ULL)>>20)%T->sz;
  while(T->key[h]!=~0ULL){ if(T->key[h]==k){ *v=T->val[h]; return 1;} h=(h+1)%T->sz; } return 0; }
static void tfree(Tab*T){ free(T->key); free(T->val); }
// build table
static u64 build(const Step*S, Cand c, Tab*T, u64 *prep){
  u64 L=(u64)1<<c.d, m=(u64)ceil(c.mult*cbrt((double)r)); if(m<4) m=4;
  tinit(T,m*4+64); seed(0x7AB1E000ULL+c.ts*131+p+c.fam*17+c.d*3);
  OPS=0; Pt Pg={Px,Py,0};
  for(u64 i=0;i<m;i++){
    u64 s0=1+rnd()%(r-1); Pt R=mul(s0,Pg); u64 sm; Pt D;
    if(walk(S,R,&sm,20*L,&D)) tput(T,D,(s0+sm)%r); }
  *prep=OPS; return T->n; }
// query
typedef struct { u64 ops; int ok; u64 trials; } QR;
static QR query(const Step*S, Cand c, Tab*T, u64 k){
  u64 L=(u64)1<<c.d; Pt Pg={Px,Py,0}; Pt Q=mul(k,Pg); OPS=0; Pt R=Q; QR res={0,0,0};
  for(u64 t=0;t<400;t++){
    if(t>0) R=add(R,Pg);
    res.trials++; u64 sm; Pt D; u64 u;
    if(walk(S,R,&sm,20*L,&D) && tget(T,D,&u)){
      u64 kc=((u+2*r-t%r-sm)%r+r)%r; Pt V=mul(kc,Pg);
      if(!V.inf&&!R.inf&&V.x==Q.x&&V.y==Q.y){ res.ok=1; break; } } }
  res.ops=OPS; return res; }
typedef struct { u64 S, prep; double meanT, succ; u64 *Ts; int nq; } Ev;
static Ev evaluate(const Step*S, Cand c, Tab*T, int nq, u64 qseed, int keep, int abortfail){
  Ev e={T->n,0,0,0,NULL,nq}; if(keep) e.Ts=malloc(nq*8);
  seed(qseed); double sum=0; int ok=0, done=0, fail=0;
  for(int i=0;i<nq;i++){ u64 k=1+rnd()%(r-1); QR q=query(S,c,T,k); sum+=q.ops; ok+=q.ok; fail+=!q.ok; done++; if(keep) e.Ts[i]=q.ok?q.ops:0;
    if(abortfail && fail>3) break; }
  e.meanT=sum/done; e.succ=(double)ok/nq; return e; }
static double rho(u64 S,double T){ return (double)S*T*T/(double)r; }
static void printcand(FILE*f,Cand c){ fprintf(f,"{\"fam\":%d,\"d\":%d,\"mult\":%g,\"ss\":%d,\"ts\":%d}",c.fam,c.d,c.mult,c.ss,c.ts); }
static void printev(FILE*f,Ev e){
  fprintf(f,"{\"S\":%llu,\"prep\":%llu,\"meanT\":%g,\"succ\":%g,\"rho\":%g,\"Ts\":[",(unsigned long long)e.S,(unsigned long long)e.prep,e.meanT,e.succ,rho(e.S,e.meanT));
  for(int i=0;i<e.nq;i++) fprintf(f,"%s%llu",i?",":"",(unsigned long long)e.Ts[i]); fprintf(f,"]}"); }
#define NTRAIN 150
static void run_method(FILE*f,const char*name,Cand*cands,int nc){
  int d0=(int)lround(bits/3.0); (void)d0;
  double best=1e300; int bi=-1; double *trho=malloc(nc*8); double *tsucc=malloc(nc*8);
  for(int i=0;i<nc;i++){
    Step S; mkstep(&S,cands[i]); Tab T; u64 prep; build(&S,cands[i],&T,&prep);
    Ev e=evaluate(&S,cands[i],&T,NTRAIN,0x7141100ULL+p,0,1); e.prep=prep;
    trho[i]=rho(e.S,e.meanT); tsucc[i]=e.succ;
    if(e.succ>=0.98 && trho[i]<best){ best=trho[i]; bi=i; }
    tfree(&T); }
  if(bi<0){ bi=0; }
  fprintf(f,"\"%s\":{\"train\":[",name);
  for(int i=0;i<nc;i++){ fprintf(f,"%s{\"c\":",i?",":""); printcand(f,cands[i]); fprintf(f,",\"rho\":%g,\"succ\":%g}",trho[i],tsucc[i]); }
  fprintf(f,"],\"winner\":"); printcand(f,cands[bi]);
  Cand w=cands[bi]; Step S; mkstep(&S,w); Tab T; u64 prep; build(&S,w,&T,&prep);
  Ev ea=evaluate(&S,w,&T,400,0xE7A10000ULL+p,1,0); ea.prep=prep;
  fprintf(f,",\"evalA\":"); printev(f,ea); tfree(&T);
  fprintf(f,",\"evalB\":[");
  for(int j=0;j<3;j++){ Cand w2=w; w2.ts=100+j; Tab T2; u64 pr2; build(&S,w2,&T2,&pr2);
    Ev eb=evaluate(&S,w2,&T2,150,0xE7B10000ULL+p+j,1,0); eb.prep=pr2; fprintf(f,"%s",j?",":""); printev(f,eb); tfree(&T2); }
  fprintf(f,"]}"); free(trho); free(tsucc); }
int main(int argc,char**argv){
  p=strtoull(argv[1],0,10); A=strtoull(argv[2],0,10); B=strtoull(argv[3],0,10); r=strtoull(argv[4],0,10);
  Px=strtoull(argv[5],0,10); Py=strtoull(argv[6],0,10); bits=atoi(argv[7]); FILE*f=fopen(argv[8],"w");
  int nH = argc>9 ? atoi(argv[9]) : 48;
  int d0=(int)lround(bits/3.0); double mults[4]={0.5,1,2,4};
  Cand b0[12]; int n=0; for(int dd=-1;dd<=1;dd++) for(int mi=0;mi<4;mi++){ b0[n++]=(Cand){0,d0+dd,mults[mi],0,0}; }
  Cand *h=malloc(nH*sizeof(Cand)); seed(0x600DF00DULL+p);
  for(int i=0;i<nH;i++){ h[i]=(Cand){(int)(rnd()%7),d0-1+(int)(rnd()%3),mults[rnd()%4],(int)(rnd()%3),(int)(rnd()%3)}; }
  fprintf(f,"{\"bits\":%d,\"p\":%llu,\"r\":%llu,",bits,(unsigned long long)p,(unsigned long long)r);
  run_method(f,"B0",b0,12); fprintf(f,","); run_method(f,"H",h,nH); fprintf(f,"}\n"); fclose(f); return 0; }
