#!/bin/bash
cd "$(dirname "$0")"
rm -f out_*.jsonl
python3 sat_ladder.py run instances_run.jsonl glucose4 120 out_ladder_glucose4.jsonl > log_ladder_g.txt 2>&1
python3 sat_ladder.py run instances_run.jsonl cadical195 120 out_ladder_cadical.jsonl > log_ladder_c.txt 2>&1
python3 sat_ladder.py run instances_run.jsonl cms 120 out_ladder_cms_xor.jsonl --xor > log_ladder_x.txt 2>&1
python3 sat_affine_cmp.py run aff_instances.jsonl glucose4 120 out_affine_glucose4.jsonl > log_aff_g.txt 2>&1
python3 sat_affine_cmp.py run aff_instances.jsonl cadical195 120 out_affine_cadical.jsonl > log_aff_c.txt 2>&1
python3 sat_affine_cmp.py run aff_instances.jsonl cms 120 out_affine_cms_xor.jsonl --xor > log_aff_x.txt 2>&1
echo done > t1_done.flag
