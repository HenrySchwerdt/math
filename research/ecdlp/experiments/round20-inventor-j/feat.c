// feat.c: read uint32 scalars on stdin; for each scalar s output raw features of R=sP (toy curve y^2=x^3+ax+b mod p, p<2^31)
// usage: feat p a b Px Py   (scalars on stdin, raw out on stdout: 22 uint32 per scalar)
// out: [s, Rx,Ry, (R+P)x,y, (R-P)x,y, (R+2P)x,y, (R-2P)x,y, (R+3P)x,y, (R-3P)x,y, (2R)x,y, leg(y),leg(x),leg(x+1),leg(x-Px),leg(y-Py)]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef int64_t i64; typedef uint64_t u64; typedef __int128 i128;
static i64 p,A,B;
typedef struct {i64 x,y; int inf;} pt;
static i64 inv(i64 a){ i64 t=0,nt=1,r=p,nr=((a%p)+p)%p; while(nr){i64 q=r/nr,tmp=t-q*nt;t=nt;nt=tmp;tmp=r-q*nr;r=nr;nr=tmp;} if(t<0)t+=p; return t;}
static pt add(pt P, pt Q){ if(P.inf)return Q; if(Q.inf)return P; i64 lam;
 if(P.x==Q.x){ if((P.y+Q.y)%p==0){pt o={0,0,1};return o;} lam=(i64)(((i128)((3*((i128)P.x*P.x%p)+A)%p))*inv(2*P.y%p)%p);}
 else lam=(i64)(((i128)(((Q.y-P.y)%p+p)%p))*inv(((Q.x-P.x)%p+p)%p)%p);
 i64 x3=(( (i128)lam*lam - P.x - Q.x)%p+p)%p; i64 y3=(((i128)lam*((P.x-x3+p)%p) - P.y)%p+p)%p; pt R={x3,y3,0}; return R;}
static pt neg(pt P){ if(P.inf)return P; pt R={P.x,(p-P.y)%p,0}; return R;}
static pt mul(u64 k, pt P){ pt R={0,0,1}; while(k){ if(k&1)R=add(R,P); k>>=1; if(k)P=add(P,P);} return R;}
static i64 pw(i64 b,i64 e){ i64 r=1; b%=p; if(b<0)b+=p; while(e){ if(e&1)r=(i128)r*b%p; b=(i128)b*b%p; e>>=1;} return r;}
static uint32_t leg(i64 a){ a%=p; if(a<0)a+=p; if(a==0) return 2; return pw(a,(p-1)/2)==1?1:0; }
int main(int argc,char**argv){ p=atoll(argv[1]);A=atoll(argv[2]);B=atoll(argv[3]); pt P={atoll(argv[4]),atoll(argv[5]),0}; (void)B;
 pt P2=add(P,P),P3=add(P2,P); pt sh[6]={P,neg(P),P2,neg(P2),P3,neg(P3)};
 uint32_t s; uint32_t out[22];
 while(fread(&s,4,1,stdin)==1){ pt R=mul(s,P); out[0]=s; out[1]=R.x; out[2]=R.y;
  for(int j=0;j<6;j++){ pt T=add(R,sh[j]); out[3+2*j]=T.inf?0:T.x; out[4+2*j]=T.inf?0:T.y; }
  pt D=add(R,R); out[15]=D.inf?0:D.x; out[16]=D.inf?0:D.y;
  out[17]=leg(R.y); out[18]=leg(R.x); out[19]=leg(R.x+1); out[20]=leg(R.x-P.x); out[21]=leg(R.y-P.y);
  fwrite(out,4,22,stdout);} return 0;}
