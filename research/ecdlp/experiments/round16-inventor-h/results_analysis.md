```
## E3 B0 evalA
 bits 16: rho mean 8.18 CI95 [6.61,10.00] min succ 1.000 S~32 T~133 prep~2381
 bits 20: rho mean 9.92 CI95 [4.75,19.07] min succ 1.000 S~119 T~266 prep~25254
 bits 24: rho mean 4.38 CI95 [3.58,5.47] min succ 1.000 S~114 T~796 prep~70263
 bits 28: rho mean 4.23 CI95 [3.08,5.26] min succ 1.000 S~1187 T~1029 prep~530150
 bits 32: rho mean 4.53 CI95 [3.97,5.26] min succ 1.000 S~1638 T~4043 prep~4063460
 slope log2(rho) vs bits: -0.0733 CI95 [-0.1060,-0.0357]
## E3 B0 evalB
 bits 16: rho mean 7.40 CI95 [6.23,8.96] min succ 1.000 S~33 T~121 prep~2283
 bits 20: rho mean 9.31 CI95 [5.11,15.62] min succ 1.000 S~117 T~263 prep~26564
 bits 24: rho mean 5.10 CI95 [4.14,6.49] min succ 1.000 S~112 T~863 prep~66912
 bits 28: rho mean 4.60 CI95 [3.74,5.38] min succ 1.000 S~1173 T~1120 prep~532007
 bits 32: rho mean 4.68 CI95 [4.11,5.31] min succ 1.000 S~1640 T~4074 prep~4155597
 slope log2(rho) vs bits: -0.0585 CI95 [-0.0844,-0.0301]
## E3 H evalA
 bits 16: rho mean 6.64 CI95 [5.70,7.85] min succ 1.000 S~29 T~128 prep~4019
 bits 20: rho mean 4.25 CI95 [2.87,6.95] min succ 1.000 S~31 T~330 prep~10833
 bits 24: rho mean 5.11 CI95 [4.44,6.00] min succ 1.000 S~268 T~629 prep~131469
 bits 28: rho mean 4.39 CI95 [3.79,5.08] min succ 1.000 S~421 T~1360 prep~309939
 bits 32: rho mean 3.90 CI95 [3.32,4.58] min succ 1.000 S~1740 T~3954 prep~3576143
 slope log2(rho) vs bits: -0.0373 CI95 [-0.0631,-0.0123]
## E3 H evalB
 bits 16: rho mean 7.16 CI95 [5.61,9.00] min succ 1.000 S~31 T~120 prep~4037
 bits 20: rho mean 6.11 CI95 [4.09,8.43] min succ 1.000 S~29 T~393 prep~11120
 bits 24: rho mean 5.06 CI95 [4.32,5.96] min succ 1.000 S~267 T~622 prep~129383
 bits 28: rho mean 4.44 CI95 [3.94,5.01] min succ 1.000 S~428 T~1353 prep~315004
 bits 32: rho mean 3.99 CI95 [3.48,4.52] min succ 1.000 S~1710 T~4053 prep~3624882
 slope log2(rho) vs bits: -0.0537 CI95 [-0.0780,-0.0272]
## E3 ratio H/B0 (curve-level bootstrap, out of sample)
 evalA bits 16: H/B0 0.814 CI95 [0.625,1.071]
 evalA bits 20: H/B0 0.441 CI95 [0.191,1.152]
 evalA bits 24: H/B0 1.172 CI95 [0.896,1.505]
 evalA bits 28: H/B0 1.035 CI95 [0.800,1.392]
 evalA bits 32: H/B0 0.860 CI95 [0.693,1.058]
 evalB bits 16: H/B0 0.966 CI95 [0.700,1.309]
 evalB bits 20: H/B0 0.672 CI95 [0.338,1.325]
 evalB bits 24: H/B0 1.003 CI95 [0.747,1.302]
 evalB bits 28: H/B0 0.961 CI95 [0.786,1.227]
 evalB bits 32: H/B0 0.851 CI95 [0.703,1.016]
## E3 winners curse: train rho (min over candidates) vs evalA vs evalB, per curve
 16/0 B0: train 5.60 A 6.50 B 7.22 fam 0 | H: train 6.10 A 5.88 B 5.59 fam 2
 16/1 B0: train 8.04 A 9.38 B 8.48 fam 0 | H: train 5.11 A 6.99 B 8.80 fam 5
 16/2 B0: train 6.97 A 8.59 B 6.37 fam 0 | H: train 4.91 A 7.08 B 7.02 fam 4
 20/0 B0: train 12.72 A 18.87 B 15.49 fam 0 | H: train 3.44 A 3.15 B 3.99 fam 5
 20/1 B0: train 6.35 A 5.49 B 6.90 fam 0 | H: train 4.64 A 6.51 B 6.91 fam 4
 20/2 B0: train 6.09 A 5.22 B 5.12 fam 0 | H: train 2.86 A 3.02 B 7.22 fam 2
 24/0 B0: train 5.50 A 5.37 B 6.31 fam 0 | H: train 4.26 A 5.09 B 4.85 fam 0
 24/1 B0: train 3.30 A 3.85 B 4.44 fam 0 | H: train 2.82 A 5.33 B 4.63 fam 4
 24/2 B0: train 4.13 A 3.90 B 4.48 fam 0 | H: train 3.90 A 4.87 B 5.61 fam 4
 28/0 B0: train 4.87 A 4.77 B 5.19 fam 0 | H: train 3.81 A 3.99 B 4.20 fam 5
 28/1 B0: train 3.67 A 3.05 B 3.77 fam 0 | H: train 3.64 A 4.87 B 4.77 fam 5
 28/2 B0: train 5.64 A 4.86 B 4.80 fam 0 | H: train 3.64 A 4.27 B 4.32 fam 0
 32/0 B0: train 3.53 A 4.22 B 4.31 fam 0 | H: train 3.52 A 3.89 B 4.09 fam 4
 32/1 B0: train 4.07 A 4.92 B 4.87 fam 0 | H: train 3.23 A 3.39 B 3.63 fam 5
 32/2 B0: train 3.41 A 4.44 B 4.82 fam 0 | H: train 3.43 A 4.41 B 4.21 fam 4
## E3 H winner family counts
{2: 2, 5: 5, 4: 6, 0: 2}
## E3 train rho by family (median over candidates with succ>=0.98, all curves)
 fam 0: n=96 median 7.01 min 3.64
 fam 1: n=8 median 17.96 min 10.63
 fam 2: n=71 median 7.87 min 2.86
 fam 3: n=102 median 7.01 min 3.32
 fam 4: n=118 median 6.72 min 2.82
 fam 5: n=97 median 6.61 min 3.23
 fam 6: n=122 median 8.25 min 3.95
## E3 preprocessing ops / r^(2/3) (H eval A table)
 bits 16: 2.88
 bits 20: 1.21
 bits 24: 2.09
 bits 28: 0.98
 bits 32: 1.52
## E1 sorted x-table, giant steps
 S exp 0.33 bits 16: S~38 ops 387.1 probes_interp 888.7 binary 2328.4 rho_ops 106.623 rho_ops+probes 1152.33 ok 900/900 prep 48
 S exp 0.33 bits 20: S~93 ops 2134.6 probes_interp 6392.4 binary 14949.0 rho_ops 530.989 rho_ops+probes 8481.01 ok 900/900 prep 104
 S exp 0.33 bits 24: S~247 ops 15321.6 probes_interp 49041.6 binary 122581.0 rho_ops 3864.043 rho_ops+probes 68307.77 ok 900/900 prep 263
 S exp 0.33 bits 28: S~563 ops 80400.5 probes_interp 309133.0 binary 804014.7 rho_ops 20450.367 rho_ops+probes 479837.67 ok 900/900 prep 578
 S exp 0.33 bits 32: S~1487 ops 548645.7 probes_interp 2035533.3 binary 6035113.3 rho_ops 135968.000 rho_ops+probes 3025760.00 ok 900/900 prep 1504
  slope log2 rho_ops vs bits: 0.648
 S exp 0.50 bits 16: S~233 ops 99.6 probes_interp 189.9 binary 805.2 rho_ops 43.652 rho_ops+probes 363.80 ok 900/900 prep 248
 S exp 0.50 bits 20: S~892 ops 270.9 probes_interp 841.2 binary 2719.2 rho_ops 83.058 rho_ops+probes 1391.59 ok 900/900 prep 910
 S exp 0.50 bits 24: S~3874 ops 1041.5 probes_interp 4040.2 binary 12509.6 rho_ops 280.593 rho_ops+probes 6675.58 ok 900/900 prep 3896
 S exp 0.50 bits 28: S~13339 ops 3466.9 probes_interp 14997.5 binary 48550.0 rho_ops 902.180 rho_ops+probes 25612.97 ok 900/900 prep 13362
 S exp 0.50 bits 32: S~57385 ops 14278.0 probes_interp 63990.2 binary 228465.0 rho_ops 3558.020 rho_ops+probes 106944.97 ok 900/900 prep 57410
  slope log2 rho_ops vs bits: 0.403
 S exp 0.67 bits 16: S~1434 ops 51.9 probes_interp 37.1 binary 581.9 rho_ops 74.076 rho_ops+probes 214.66 ok 900/900 prep 1452
 S exp 0.67 bits 20: S~8613 ops 76.2 probes_interp 95.2 binary 1057.0 rho_ops 64.711 rho_ops+probes 322.14 ok 900/900 prep 8637
 S exp 0.67 bits 24: S~60863 ops 128.8 probes_interp 286.9 binary 2077.0 rho_ops 68.353 rho_ops+probes 704.90 ok 900/900 prep 60890
 S exp 0.67 bits 28: S~316532 ops 220.6 probes_interp 683.6 binary 4211.2 rho_ops 87.389 rho_ops+probes 1457.79 ok 900/900 prep 316561
 S exp 0.67 bits 32: S~2217431 ops 457.0 probes_interp 1811.1 binary 9787.3 rho_ops 141.167 rho_ops+probes 3466.69 ok 900/900 prep 2217468
  slope log2 rho_ops vs bits: 0.057
 S exp 0.00 bits 16: S~27222 ops 42.9 probes_interp 3.4 binary 659.1 rho_ops 965.660 rho_ops+probes 1121.90 ok 900/900 prep 27247
 S exp 0.00 bits 20: S~404386 ops 54.2 probes_interp 4.0 binary 1049.5 rho_ops 1526.100 rho_ops+probes 1752.97 ok 900/900 prep 404415
 S exp 0.00 bits 24: S~7518260 ops 67.3 probes_interp 4.0 binary 1571.7 rho_ops 2334.837 rho_ops+probes 2619.39 ok 900/900 prep 7518296
  slope log2 rho_ops vs bits: 0.159
## E2 decision tree held-out accuracy (chance 0.0625); leak = Wilson99 lower > 0.0675
 bits 16 seed 0 real: L1_top4/255:0.0649(d12), L1_top4/4095:0.0637(d18), L2_mod16/255:0.0595(d14), L2_mod16/4095:0.0593(d17)
 bits 16 seed 0 PLANTED: L1_top4/255:0.2513*(d14), L1_top4/4095:0.2506*(d16), L2_mod16/255:0.0590(d11), L2_mod16/4095:0.0615(d15)
 bits 16 seed 1 real: L1_top4/255:0.0624(d14), L1_top4/4095:0.0645(d17), L2_mod16/255:0.0630(d12), L2_mod16/4095:0.0640(d16)
 bits 16 seed 2 real: L1_top4/255:0.0630(d11), L1_top4/4095:0.0644(d15), L2_mod16/255:0.0612(d12), L2_mod16/4095:0.0614(d16)
 bits 20 seed 0 real: L1_top4/255:0.0635(d16), L1_top4/4095:0.0624(d19), L2_mod16/255:0.0616(d15), L2_mod16/4095:0.0633(d17)
 bits 20 seed 0 PLANTED: L1_top4/255:0.2508*(d15), L1_top4/4095:0.2497*(d19), L2_mod16/255:0.0614(d15), L2_mod16/4095:0.0627(d17)
 bits 20 seed 1 real: L1_top4/255:0.0628(d14), L1_top4/4095:0.0627(d17), L2_mod16/255:0.0635(d14), L2_mod16/4095:0.0639(d18)
 bits 20 seed 2 real: L1_top4/255:0.0625(d13), L1_top4/4095:0.0623(d19), L2_mod16/255:0.0624(d15), L2_mod16/4095:0.0628(d17)
 bits 24 seed 0 real: L1_top4/255:0.0633(d16), L1_top4/4095:0.0638(d17), L2_mod16/255:0.0627(d13), L2_mod16/4095:0.0623(d16)
 bits 24 seed 0 PLANTED: L1_top4/255:0.2500*(d16), L1_top4/4095:0.2499*(d20), L2_mod16/255:0.0627(d13), L2_mod16/4095:0.0625(d16)
 bits 24 seed 1 real: L1_top4/255:0.0613(d13), L1_top4/4095:0.0625(d17), L2_mod16/255:0.0615(d15), L2_mod16/4095:0.0611(d17)
 bits 24 seed 2 real: L1_top4/255:0.0620(d15), L1_top4/4095:0.0623(d15), L2_mod16/255:0.0630(d14), L2_mod16/4095:0.0625(d17)
 bits 28 seed 0 real: L1_top4/255:0.0622(d14), L1_top4/4095:0.0619(d16), L2_mod16/255:0.0616(d17), L2_mod16/4095:0.0622(d17)
 bits 28 seed 0 PLANTED: L1_top4/255:0.2507*(d14), L1_top4/4095:0.2509*(d19), L2_mod16/255:0.0616(d17), L2_mod16/4095:0.0628(d17)
 bits 28 seed 1 real: L1_top4/255:0.0621(d14), L1_top4/4095:0.0619(d17), L2_mod16/255:0.0626(d12), L2_mod16/4095:0.0623(d19)
 bits 28 seed 2 real: L1_top4/255:0.0624(d15), L1_top4/4095:0.0622(d17), L2_mod16/255:0.0622(d13), L2_mod16/4095:0.0622(d18)
 bits 32 seed 0 real: L1_top4/255:0.0632(d15), L1_top4/4095:0.0628(d16), L2_mod16/255:0.0609(d14), L2_mod16/4095:0.0613(d18)
 bits 32 seed 0 PLANTED: L1_top4/255:0.2503*(d16), L1_top4/4095:0.2501*(d19), L2_mod16/255:0.0628(d14), L2_mod16/4095:0.0620(d17)
 bits 32 seed 1 real: L1_top4/255:0.0609(d14), L1_top4/4095:0.0610(d16), L2_mod16/255:0.0625(d14), L2_mod16/4095:0.0628(d18)
 bits 32 seed 2 real: L1_top4/255:0.0635(d14), L1_top4/4095:0.0633(d16), L2_mod16/255:0.0626(d14), L2_mod16/4095:0.0636(d17)
real-curve leak flags by size: {16: 0, 20: 0, 24: 0, 28: 0, 32: 0}
## POST HOC (not pre-registered): slope over bits 24..32 only
 B0 evalA: slope 0.0071 CI95 [-0.0394,0.0507]
 B0 evalB: slope -0.0128 CI95 [-0.0645,0.0323]
 H evalA: slope -0.0486 CI95 [-0.0895,-0.0090]
 H evalB: slope -0.0422 CI95 [-0.0802,-0.0073]
```
