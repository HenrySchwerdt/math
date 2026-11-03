// E1: sorted x-table (interpolation search) + giant steps. usage: e1 p a b r Px Py bits out S_exponent_or_full
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef uint64_t u64; typedef int64_t i64;
static u64 p,A,B,r,Px,Py; static u64 OPS=0;
typedef struct { u64 x,y; int inf; } Pt;
static inline u64 mulm(u64 a,u64 b){return (a*b)%p;}
static u64 invm(u64 a){ i64 t=0,nt=1; i64 rr=(i64)p,nr=(i64)a; while(nr){ i64 q=rr/nr; i64 tmp=t-q*nt; t=nt; nt=tmp; tmp=rr-q*nr; rr=nr; nr=tmp;} if(t<0)t+=p; return (u64)t;}
static Pt add(Pt P,Pt Q){ OPS++; if(P.inf)return Q; if(Q.inf)return P; u64 lam;
  if(P.x==Q.x){ if((P.y+Q.y)%p==0){Pt O={0,0,1};return O;} lam=mulm((3*mulm(P.x,P.x)+A)%p,invm((2*P.y)%p)); }
  else lam=mulm((Q.y+p-P.y)%p,invm((Q.x+p-P.x)%p));
  u64 x3=(mulm(lam,lam)+2*p-P.x-Q.x)%p; Pt R={x3,(mulm(lam,(P.x+p-x3)%p)+p-P.y)%p,0}; return R; }
static Pt mul(u64 k,Pt P){ Pt R={0,0,1}; while(k){ if(k&1)R=add(R,P); k>>=1; if(k)P=add(P,P);} return R; }
static u64 st; static u64 rnd(void){ u64 z=(st+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31);}
typedef struct { uint32_t x,y; uint32_t j; } E;
static int cmp(const void*a,const void*b){ const E*x=a,*y=b; return x->x<y->x?-1:x->x>y->x; }
static E*tab; static u64 S;
static u64 probes;
// interpolation search for x; returns index or -1
static i64 isearch(u64 x){ i64 lo=0,hi=S-1; 
  while(lo<=hi){ probes++; if(tab[hi].x==tab[lo].x){ return tab[lo].x==x?lo:-1; }
    if(x<tab[lo].x||x>tab[hi].x) return -1;
    i64 mid=lo+(i64)((double)(x-tab[lo].x)/(double)(tab[hi].x-tab[lo].x)*(hi-lo));
    if(mid<lo)mid=lo; if(mid>hi)mid=hi; 
    if(tab[mid].x==x) return mid; if(tab[mid].x<x) lo=mid+1; else hi=mid-1; }
  return -1; }
static i64 bsearchx(u64 x){ i64 lo=0,hi=S-1; while(lo<=hi){ probes++; i64 mid=(lo+hi)/2; if(tab[mid].x==x)return mid; if(tab[mid].x<x)lo=mid+1; else hi=mid-1;} return -1; }
int main(int argc,char**argv){
  p=strtoull(argv[1],0,10);A=strtoull(argv[2],0,10);B=strtoull(argv[3],0,10);r=strtoull(argv[4],0,10);Px=strtoull(argv[5],0,10);Py=strtoull(argv[6],0,10);
  int bits=atoi(argv[7]); FILE*f=fopen(argv[8],"w"); double ex=atof(argv[9]); // ex<=0 => full table
  S = ex>0 ? (u64)ceil(pow((double)r,ex)) : (r-1)/2; if(S>(r-1)/2) S=(r-1)/2;
  tab=malloc(S*sizeof(E)); Pt Pg={Px,Py,0}; OPS=0; Pt R=Pg; // j=1..S
  for(u64 j=1;j<=S;j++){ tab[j-1]=(E){(uint32_t)R.x,(uint32_t)R.y,(uint32_t)j}; R=add(R,Pg); }
  u64 prep=OPS; qsort(tab,S,sizeof(E),cmp);
  u64 g=2*S+1; Pt G=mul(g,Pg); // stride point: setup counted in prep
  prep=OPS; int nq=300; st=0xE1E1ULL+p; double sops=0,spi=0,spb=0; int ok=0;
  for(int i=0;i<nq;i++){ u64 k=1+rnd()%(r-1); OPS=0; Pt Q=mul(k,Pg); OPS=0; Pt Rc=Q; u64 c=0; int found=0; u64 kk=0; probes=0; u64 pb=0;
    // table covers j in [-S,S]; k = c*g + s  with s in [-S,S] => Rc = Q - c*g*P = sP
    for(c=0;c<=r/g+2;c++){
      if(Rc.inf){ kk=(c*g)%r; found=1; break; }
      u64 pr0=probes; i64 idx=isearch(Rc.x); u64 pi_=probes-pr0; spi+=0; pb+=pi_;
      if(idx>=0){ u64 j=tab[idx].j; int same=(tab[idx].y==Rc.y); // Rc = +-jP
        u64 s = same? j : (r-j); kk=(c*g+s)%r; found=1; break; }
      // giant step: Rc <- Rc - G
      Pt nG=G; nG.y=(p-G.y)%p; Rc=add(Rc,nG); }
    spi+=pb; probes=0; for(u64 cc=0;cc<=c;cc++){} 
    if(found){ if(mul(kk,Pg).x==Q.x && mul(kk,Pg).y==Q.y) ok++; }
    sops+=OPS; }
  // binary-search probe cost for same visited sequence ~ log2 S per lookup; estimate: lookups = ops+1
  double mops=sops/nq, mpi=spi/nq;
  double lookups=mops+1; double mpb=lookups*ceil(log2((double)S+1));
  fprintf(f,"{\"bits\":%d,\"p\":%llu,\"r\":%llu,\"S\":%llu,\"ex\":%g,\"prep\":%llu,\"nq\":%d,\"ok\":%d,\"mean_ops\":%g,\"mean_probes_interp\":%g,\"mean_probes_binary\":%g,\"rho_ops\":%g,\"rho_ops_plus_probes\":%g}\n",
    bits,(unsigned long long)p,(unsigned long long)r,(unsigned long long)S,ex,(unsigned long long)prep,nq,ok,mops,mpi,mpb,
    (double)S*(mops+1)*(mops+1)/(double)r,(double)S*(mops+1+mpi)*(mops+1+mpi)/(double)r);
  fclose(f); return 0; }
