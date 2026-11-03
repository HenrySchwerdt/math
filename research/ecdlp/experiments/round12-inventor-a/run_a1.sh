#!/bin/bash
cd "$(dirname "$0")"
for b in 12 14 16 18 20 22 24; do python3 a1_farey_ic.py l2 $b; python3 a1_farey_ic.py l3 $b; done > log_a1_l.txt 2>&1 &
for b in 12 14 16 18 20; do python3 a1_farey_ic.py m3 $b; done > log_a1_m3.txt 2>&1 &
for b in 12 14 16 18 20; do python3 a1_farey_ic.py m3x $b; done > log_a1_m3x.txt 2>&1 &
wait
