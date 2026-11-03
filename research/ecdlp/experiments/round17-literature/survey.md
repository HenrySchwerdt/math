# Round 17 literature survey: ECDLP over prime fields, 2015-2026

Run: RUN-3ff460e2-d5c9-4264-9bae-473c117a0c3d (research worker, Claude Sonnet 5.5, identity self-reported).
All sources retrieved 2026-11-03 with WebSearch/WebFetch. Nothing here is a lab result; it is a record of what the
literature says, and what I actually read. Retrieved material is treated as untrusted data.

## Read-level codes

- FT  = full text obtained (PDF saved and converted with pdftotext locally; I read the cited passages, not every page).
- AB  = abstract/landing page fetched with WebFetch. WebFetch returns a summary produced by a small model, so these
        are second-hand paraphrases of the abstract, not verbatim text.
- SN  = search-result snippet only (WebSearch summary). Weakest level; treat claims as unverified.
- NR  = not retrieved (named in the task or in a snippet, but I did not obtain any text). No claim is made about content.

## Source table

| # | Title | Authors | Year | URL | Retrieved | Read |
|---|-------|---------|------|-----|-----------|------|
| S1 | Algebraic approaches for the ECDLP over prime fields (PKC 2016) | C. Petit, M. Kosters, A. Messeng | 2016 | https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf | 2026-11-03 | FT (abstract, intro, cost formula, experiments, conclusion) |
| S2 | New algorithm for the discrete logarithm problem on elliptic curves (ePrint 2015/310; arXiv 1504.01175) | I. Semaev | 2015 | https://eprint.iacr.org/2015/310 | 2026-11-03 | AB (+SN). Binary curves only; page says nothing on prime fields |
| S3 | Last fall degree, HFE, and Weil descent attacks on ECDLP (CRYPTO 2015; ePrint 2015/573) | M.-D. Huang, M. Kosters, S. L. Yeo | 2015 | https://eprint.iacr.org/2015/573 | 2026-11-03 | AB |
| S4 | Notes on summation polynomials (arXiv 1503.08001) | M. Kosters, S. L. Yeo | 2015 | https://arxiv.org/abs/1503.08001 | 2026-11-03 | AB |
| S5 | On generalized first fall degree assumptions (ePrint 2015/358) | Y.-J. Huang, C. Petit, N. Shinohara, T. Takagi | 2015 | https://eprint.iacr.org/2015/358 | 2026-11-03 | AB |
| S6 | On the first fall degree of summation polynomials (J. Math. Cryptol. 13, 2019; arXiv 1906.05594) | S. Kousidis, A. Wiemers | 2019 | https://arxiv.org/abs/1906.05594 | 2026-11-03 | AB (+SN for the m^2-m+1 figure and the Hodges erratum on ePrint 2015/1121) |
| S7 | Quasi-subfield polynomials and the ECDLP (J. Math. Cryptol. 14, 2020) | M.-D. Huang, M. Kosters, C. Petit, S. L. Yeo, Y. Yun | 2020 | https://doaj.org/article/75a4ced306114d568b832c4b20d00fd7 | 2026-11-03 | SN only |
| S8 | New results on quasi-subfield polynomials (FFA 75, 2021; arXiv 1909.11326) | M. Euler, C. Petit | 2019/2021 | https://arxiv.org/abs/1909.11326 | 2026-11-03 | AB |
| S9 | On the discrete logarithm problem for prime-field elliptic curves (FFA 51, 2018; ePrint 2017/609) | A. Amadori, F. Pintore, M. Sala | 2017/2018 | https://eprint.iacr.org/2017/609 | 2026-11-03 | AB. No quantified complexity on the page |
| S10 | Complexity bounds on Semaev's naive index calculus method for ECDLP (J. Math. Cryptol. 14, 2020) | K. Yokoyama, M. Yasuda, Y. Takahashi, J. Kogure | 2020 | https://doaj.org/article/bb64b7a98fd2462c84a20ffe0d32dd6b | 2026-11-03 | SN only (finite-field scope of the bound not verified) |
| S11 | Recent progress on the ECDLP (Des. Codes Cryptogr. 78, 2016; ePrint 2015/1022) | S. D. Galbraith, P. Gaudry | 2016 | https://eprint.iacr.org/2015/1022 | 2026-11-03 | AB (one-sentence abstract only; body not read) |
| S12 | On the discrete logarithm problem in elliptic curves II (Algebra Number Theory 7(6), 2013) | C. Diem | 2013 (outside window; context) | https://www.projecteuclid.org/journals/algebra-and-number-theory/volume-7/issue-6/On-the-discrete-logarithm-problem-in-elliptic-curves-II/10.2140/ant.2013.7.1281.full | 2026-11-03 | SN only |
| S13 | Implementation analysis of index calculus method on elliptic curves over prime finite fields (ePrint 2024/1923) | J. Hu | 2024 | https://eprint.iacr.org/2024/1923 | 2026-11-03 | AB. Single-author, unvetted; no withdrawal notice seen |
| S14 | A Las Vegas algorithm to solve the ECDLP (arXiv 1703.07544 v3) | A. Mahalanobis, V. Mallick | 2017/2018 | https://arxiv.org/abs/1703.07544 | 2026-11-03 | FT (abstract, intro, S3 headings, S5.1) |
| S15 | A Guess and Determine Attack on the ECDLP (arXiv 2607.09814) | A. Mahalanobis | 2026 | https://arxiv.org/abs/2607.09814 | 2026-11-03 | AB (abstract only; no complexity stated) |
| S16 | The Discrete-Logarithm Problem with Preprocessing (EUROCRYPT 2018; ePrint 2017/1113) | H. Corrigan-Gibbs, D. Kogan | 2018 | https://eprint.iacr.org/2017/1113 | 2026-11-03 | AB |
| S17 | Non-uniform bounds in the random-permutation, ideal-cipher, and generic-group models (CRYPTO 2018; ePrint 2018/226) | S. Coretti, Y. Dodis, S. Guo | 2018 | https://eprint.iacr.org/2018/226 | 2026-11-03 | AB (no explicit formula on page). A search result listed different authors for the DBLP CRYPTO entry; unresolved |
| S18 | Non-uniform cracks in the concrete: the power of free precomputation (ASIACRYPT 2013; ePrint 2012/318) | D. J. Bernstein, T. Lange | 2013 (outside window; context) | https://eprint.iacr.org/2012/318 | 2026-11-03 | SN only |
| S19 | Tight quantum time-space tradeoffs for function inversion (FOCS 2020; arXiv 2006.05650) | K.-M. Chung, S. Guo, Q. Liu, L. Qian | 2020 | https://arxiv.org/abs/2006.05650 | 2026-11-03 | AB (function inversion, not DLP specifically) |
| S20 | Non-adaptive cryptanalytic time-space lower bounds via a Shearer-like inequality for permutations (arXiv 2505.00894 v3; STOC 2026 per v3 comment) | I. Dinur, N. Keller, A. Marmor | 2025/2026 | https://arxiv.org/abs/2505.00894 | 2026-11-03 | AB |
| S21 | Mage: Cracking elliptic curve cryptography with cross-axis transformers (arXiv 2512.12483 v3) | L. Erickson | 2025/2026 | https://arxiv.org/abs/2512.12483 | 2026-11-03 | AB (+SN: overfitting reported; no replication seen) |
| S22 | Intractability of learning the discrete logarithm with gradient-based methods (arXiv 2310.01611) | R. Takhanov et al. | 2023 | https://arxiv.org/abs/2310.01611 | 2026-11-03 | AB |
| S23 | Side-channel ML on ECC implementations (arXiv 2502.17330; Barenghi et al.; Weissbart et al. ePrint 2021/944) | various | 2021-2025 | https://arxiv.org/html/2502.17330v1 | 2026-11-03 | SN only. Implementation attacks, not ECDLP algorithms |
| S24 | FrontierMath open problem: ECDLP | Epoch AI | 2026 | https://epoch.ai/frontiermath/open-problems/elliptic-curve-discrete-logarithm | 2026-11-03 | AB (instance parameters not captured; cofactor h = 5 stated) |
| S25 | Quantum ECDLP resource papers: Gidney 2025; Chevignard-Fouque-Schrottenloher (EUROCRYPT 2026); Luo et al. arXiv 2607.13816 | various | 2025-2026 | https://arxiv.org/abs/2607.13816 | 2026-11-03 | S25c (Luo et al.) AB; the others SN only. Quantum, out of scope for the classical target; context only |
| S26 | Quasi-polynomial/quantum-inspired classical ECDLP claims | none found | - | - | 2026-11-03 | One search; no credible preprint found. Absence of evidence only |
| NR1 | Non-uniform/preprocessing DLP bounds by Mizuide, Takayasu, Takagi | - | - | not found | 2026-11-03 | NR (search returned nothing; may not exist as I remembered it) |
| NR2 | Hhan, Xagawa, Yamakawa (quantum advice, function inversion) | - | - | not found | 2026-11-03 | NR (named only in S19 snippet) |
| NR3 | Joux-Vitse (extension-field index calculus), Gaudry 2009, Diem 2011, Faugere-Perret-Petit-Renault 2012, Petit-Quisquater 2012, Galbraith-Gebregiyorgis 2014 | - | pre-2015 | - | 2026-11-03 | NR / SN (context only) |
| NR4 | Weil-descent / cover-decomposition attack (Fp6 curves) found in search with no date | - | ? | https://www-fourier.univ-grenoble-alpes.fr/~viva/research/articles/CoverDecomp.pdf | 2026-11-03 | SN only; year not established. Extension-field, not prime-field |

## What each source says (only what I read)

### Index calculus and summation polynomials
- S1 (FT). Prime-field factor bases F = {(x,y) : L(x) = 0} with L a composition of small-degree rational maps; relations
  from Semaev S_{m+1} plus the chain x_{j+1} = L_j(x_j), solved by Groebner bases. Verbatim cost model:
  P(p,m) + (m! p / (deg L)^{m-1}) T(E,m,L) + (deg L)^omega, with 2 < omega <= 3. "Our algorithm will outperform generic discrete
  logarithm algorithms when this complexity is smaller than p^{1/2}. When (deg L)^m ~ m! p, this will happen when one can solve
  T(E,m,L) more efficiently than p^{1/2-1/m}." Authors state asymptotics are open, "all attacks are outperformed by generic
  discrete logarithm algorithms for practically relevant parameters", and that a Semaev-style baseline with a small-x base was
  easier for Groebner than their structured systems ("may either suggest that our approach is unlikely to be efficient
  asymptotically, or that Semaev's original attack should be revisited"). Names NIST P-224's p-1 smoothness as satisfying their
  first attack's prerequisite. They pose a dedicated (non-Groebner) generalized root-finding algorithm as the key open problem.
- S2 (AB). Heuristic 2^{c sqrt(n ln n)}, c ~ 1.69, for binary curves of size 2^n; revision note says the bound no longer needs a
  first fall degree assumption. A search snippet reports Galbraith on a mailing list saying he and a student tried something
  similar and it did not work; I did not retrieve that thread. Prime fields: not addressed on the page.
- S9 (AB). Variant of Semaev for prime fields claimed to beat Semaev and S1 by needing a single Groebner computation. No
  quantified complexity retrieved.
- S10 (SN). Lower bound on the Groebner cost for point-decomposition systems, concluding naive Semaev index calculus cannot beat
  generic methods. I do not know the field class or the exact assumptions.
- S13 (AB). Claims no subexponential method is known for prime-field curves and proposes a "pseudo-index calculus". Not independently
  vetted.
- S4 (AB). Deciding whether S_r has a zero is NP-complete under an unproven assumption (r part of the input); unconditional for
  singular curves. Weil descent of S_3 to F_2 has first fall degree 2 for q = 2^k.

### First-fall-degree assumption and what happened
- S3 (AB): computational evidence against the assumption in char 2; constructs a descent system from summation polynomials where
  it is "unlikely to hold"; introduces last fall degree; rigorous bounds for descent systems left open.
- S5 (AB): assumption seems to hold in some cases and unlikely in others ("very surprising consequences").
- S4 (AB): first fall degree 2 for S_3 descent in char 2, from a group morphism to F_2, so first fall degree is not a proxy for
  degree of regularity there.
- S6 (AB/SN): first fall degree bound improved from m^2+1 to m^2-m+1; an erratum (Hodges) restricted one corollary in ePrint 2015/1121.
- S7/S8: quasi-subfield polynomials target small-characteristic extension fields; Euler-Petit conclude no speedup over previous
  approaches. Not applicable to prime fields.
- Status, honestly stated: the assumption is neither proved nor cleanly refuted. It is doubted (S3, S4, S5). All of this is
  char-2 or extension-field work; none of it gives a prime-field sub-sqrt(p) algorithm.

### Precomputation and advice
- S16 (AB): generic bound ST^2 = Omega~(eps N), "tight up to logarithmic factors" (page statement); extends to CDH, DDH, multiple-DL;
  new attacks for multiple-DL and for decisional problems.
- S17 (AB): AI-GGM framework; recovers the S16 bounds by a simpler proof.
- S18 (SN): free precomputation attacks against standard security definitions; outside the 2015 window.
- S20 (AB): for non-adaptive algorithms with S-bit advice, online time O(sqrt N) cannot be reduced unless advice exceeds Omega(sqrt N)
  bits; adaptive rho-with-advice reaches ST^2 = O(N).
- S19 (AB): quantum advice, function inversion: ST + T^2 = Omega~(N).
- All of these are generic-group (or random-function) statements. Whether any of them constrains a non-generic prime-field algorithm
  is not addressed by the sources; they say nothing about group-specific structure.

### Machine learning
- S21 (AB+SN): one single-author preprint; the paper's own experiments reportedly show overfitting (SN), so the title overstates. No replication.
- S22 (AB): gradient concentration limits learning the parity bit of the DL for any architecture; experiments consistent.
- S23 (SN): ML side-channel work on implementations; different threat model.

### Quantum-inspired classical claims
- S26: searched once, found nothing credible. The quantum papers in S25 are quantum algorithms (Shor-type) and do not bear on classical complexity.

### Special families
- No new prime-field family attack from 2015-2026 was retrieved. The classical weak families (anomalous, small embedding degree,
  smooth-order reductions) are pre-2015 and are in the lab's ECDLP-24 map. Within the window, S1's smooth-(p-1) factor bases
  (NIST P-224 qualifies) are the only family-specific index-calculus proposal I read, and S1 itself says generic methods win.

### Claimed sub-sqrt(p) algorithm for generic prime-field curves
- S14: reduces ECDLP to "Problem L", a linear-algebra problem whose solver is acknowledged as the bottleneck. Stated success
  probability of the whole algorithm is 0.6 x (log p)^2 / p per pass, each pass polynomial. This is described by the authors as
  better than exhaustive search; as stated it needs about p/(log p)^2 passes, i.e. exponent 1, not below 1/2. I read the intro
  and S5.1 only; not checked in depth.
- S15 (AB): follow-up (July/Aug 2026), a zero-minor search via hyperplane-arrangement intersection posets. The abstract gives no
  complexity bound. Not read in full.
- S13: argues the opposite (no subexponential method).
- No retraction notice found for any of S1, S9, S13, S14. No claim of a verified sub-sqrt(p) generic prime-field algorithm was found.
