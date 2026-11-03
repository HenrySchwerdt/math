# PROTOCOL ADDENDUM — written after expB_tate.py output was seen (post-hoc, labelled as such)

1. Experiment B2 was registered one-sided (observed max Fourier amplitude ABOVE the iid null 99% quantile). The observed maxima were far BELOW the null
   (max |F_a|^2/n ~ 4.0 vs null median ~ 7.7-8). This lower-tail deviation was not pre-registered; it is reported as a post-hoc observation.
2. `expB2_diag.py` (post-hoc): Var(|F_a|^2/n) ~ 1 with support edge ~4 = Sato-Tate moments (1,2), matching the lab's HYP-80158648 law for low-degree g.
3. `expB3_line_reduction.py` (post-hoc, hypothesis derived on paper AFTER seeing 2.): chi_2(f_{r,P}(R)) = c * chi_2(L(R)), L the tangent line at Q0 = ((r-1)/2)P
   (L passes through -2Q0 = P). Prediction: agreement fraction exactly 1.0 on all valid R.
4. `rho_control.py` pipeline calibrates the same-implementation rho cost (counted group additions, 3 per Floyd step); no I4 algorithm exists to compare.
