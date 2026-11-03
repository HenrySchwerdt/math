// E2 data: rows (kprime,x0,x1,x2) for k' on affine stride; x0=x(kP), x1=x(kP+P), x2=x(kP-P). usage: e2gen p a b r Px Py N2 out.bin
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint64_t u64; typedef int64_t i64;
static u64 p,A,r,Px,Py;
typedef struct { u64 x,y; int inf; } Pt;
static inline u64 mulm(u64 a,u64 b){return (a*b)%p;}
static u64 invm(u64 a){ i64 t=0,nt=1; i64 rr=(i64)p,nr=(i64)a; while(nr){ i64 q=rr/nr; i64 tmp=t-q*nt; t=nt; nt=tmp; tmp=rr-q*nr; rr=nr; nr=tmp;} if(t<0)t+=p; return (u64)t;}
static Pt add(Pt P,Pt Q){ if(P.inf)return Q; if(Q.inf)return P; u64 lam;
  if(P.x==Q.x){ if((P.y+Q.y)%p==0){Pt O={0,0,1};return O;} lam=mulm((3*mulm(P.x,P.x)+A)%p,invm((2*P.y)%p)); }
  else lam=mulm((Q.y+p-P.y)%p,invm((Q.x+p-P.x)%p));
  u64 x3=(mulm(lam,lam)+2*p-P.x-Q.x)%p; Pt R={x3,(mulm(lam,(P.x+p-x3)%p)+p-P.y)%p,0}; return R; }
static Pt mul(u64 k,Pt P){ Pt R={0,0,1}; while(k){ if(k&1)R=add(R,P); k>>=1; if(k)P=add(P,P);} return R; }
static u64 gcd(u64 a,u64 b){ while(b){u64 t=a%b;a=b;b=t;} return a; }
int main(int argc,char**argv){
  p=strtoull(argv[1],0,10);A=strtoull(argv[2],0,10);r=strtoull(argv[4],0,10);Px=strtoull(argv[5],0,10);Py=strtoull(argv[6],0,10);
  u64 N2=strtoull(argv[7],0,10); FILE*f=fopen(argv[8],"wb"); u64 H=(r-1)/2; Pt Pg={Px,Py,0}; Pt Pn=Pg; Pn.y=(p-Py)%p;
  u64 a=0x9E3779B97F4A7C15ULL%H|1; while(gcd(a,H)!=1) a+=2; u64 b=12345%H;
  if(N2>H) N2=H;
  for(u64 i=0;i<N2;i++){ u64 kp=1+(a%H*(i%H)+b)%H; Pt Q=mul(kp,Pg); Pt Q1=add(Q,Pg), Q2=add(Q,Pn);
    uint32_t row[5]={(uint32_t)kp,(uint32_t)Q.x,(uint32_t)Q1.x,(uint32_t)Q2.x,(uint32_t)(i>=N2/2)}; fwrite(row,4,5,f); }
  fclose(f); return 0; }
