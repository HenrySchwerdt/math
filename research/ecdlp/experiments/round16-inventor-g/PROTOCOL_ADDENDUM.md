# Addendum (POST-HOC, written after E1 partial results were seen and BEFORE any E4 benchmark run)

Observation in E1 (pooled, bits 16-20): ywin ratio_tri = 1.43-1.45 (constant), xyl 1.14-1.24, box 1.04-1.07, other families 1.00 +- 0.05; quad and cov ratios 1.00 for all.
Hypothesis H4 (not pre-registered in PROTOCOL.md): a window of a function f of low degree gives a union of whole fibres; a fibre of f meets E in 3 deg f points which sum to O (Abel/linear equivalence;
for ywin f=y, deg 1: horizontal lines, 3 collinear points). This yields ~c*s zero-sum triples (LINEAR in s) on top of the random s^3/N, so the ratio is 1 + c N/s^2:
constant at s = 1.5 sqrt(p) but growing like p^{1/3} at s = 2.5 p^{1/3}; but fibres are disjoint, so the relation matrix is block diagonal with rank <= #fibres <= s/3.
E4 (g4_fibre.py BITS SEED; bits 14,16,18,20 (22 if time), seeds 1,2; families rand, ywin, lin = window of y - alpha x (not negation closed); sizings s=1.5 sqrt p and s=2.5 p^{1/3}; 3 reps):
 statistics tri0, line-type triples, residual ratio (tri0-line)/pred, #relations, #unknowns, #components, rank over GF(2^31-1).
Predictions H4: (a) residual ratio ~ 1 (0.8-1.25) for ywin/lin at both sizings; (b) ratio at s=2.5p^{1/3} grows with bits (slope CI > 0) for ywin and lin;
(c) rank/(nunk) stays < 0.5 and comps > nunk/3 for ywin/lin at s=2.5p^{1/3} at every size (cannot determine all logs), while the random control has rank ~ 0 relations;
(d) USABLE fails by the added criterion U4: rank >= nunk - O(1) (connectivity) is required to solve for the logs; failing U4 means not usable.
Same GROWTH decision rule as PROTOCOL.md applied at the s=2.5 p^{1/3} sizing; U4 added to USABLE.
