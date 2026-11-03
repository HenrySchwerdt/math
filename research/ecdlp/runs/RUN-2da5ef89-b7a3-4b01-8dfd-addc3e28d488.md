# RUN-2da5ef89-b7a3-4b01-8dfd-addc3e28d488 — Revision 1 of technical report PAP-ef6e2010

Worker: research-worker, self-reported Claude Sonnet 5.5 (claude-sonnet-5-5); not verifiable from runtime metadata.
Task ECDLP-36 (TSK-befee0fc-1eb0-4d11-8632-310df4112388). Owned files: research/ecdlp/papers/PAP-ef6e2010-7950-47cf-bb75-05801891905b/{main.tex,refs.bib,main.pdf}. No commits, no sub-agents.

## Inputs
- Reviews: REV-15104e72-0b78-4895-8bd8-a4abcac85a25 (adversarial, accept, N1-N7) and REV-2b383b9b-7029-4706-95fe-ae74ee44a7ce (manuscript, revise, B1 blocking, N1-N10).
- Axiom evidence files (verified present and each containing the matching `#print axioms` line with exactly [propext, Classical.choice, Quot.sound]): Theorem B `...command-b585f279...` (degree_bound_short_weierstrass); Theorem C `...command-5da55f17...` (degree_bound_linear_short_weierstrass); Theorem D `...command-ca0a1a26...` (partial_agreement_degree_bound); all under RUN-62dbda7c-fe4f-4432-84a2-2068cd516355.
- New lab results: PRF-58cf340e (SLPBound.lean, build evidence 94bd6bd6, axioms evidence aeddfabd, both present; the axioms evidence lists length_bound_linear_short_weierstrass); HYP-0d4f14da (L2 barrier; proof-attempt, PI-checked, not reviewed); HYP-a8d1f541 (Conjecture C*, 154,288 toy cases, experimental).
- Web lookups (5 of 5 used, Crossref API): LW03, Sat05 (year 2006, confirmed), Coppersmith-Shparlinski confirmed; LW02 DOI lookup and one Kiltz-Winterhof DOI guess returned no data.

## Response table
Line numbers refer to the revised main.tex.

| Review item | Change / decision |
|---|---|
| REV-2b383b9b B1 (axiom evidence) | Done. Trust-base paragraph (l.219-228) now cites one evidence file per theorem (B b585f279, C 5da55f17, D ca0a1a26) with declaration names; verified by grep. |
| 2b383b9b N1 (binders, xCoord, files) | Done, l.186-189: binders from `variable` lines, `Affine`, `F[X]`, xCoord = 0 at infinity (harmless), declaration-to-file map for B/C/D. |
| 2b383b9b N2 / 15104e72 N7 (existence, "one device") | Done: l.67-69 states the trivial Lagrange upper bound (deg g <= N-1; (r-3)/2 for B) and "determine minimal degree up to constant factor ~3"; Limitations l.294 replaced; abstract l.33 and l.135 say constant g is treated separately. |
| 2b383b9b N3 / 15104e72 N1 (degree vs cost) | Done, l.54-60: Horner gives <= d multiplications; SLP with s multiplications has degree <= 2^s so degree bounds give only a logarithmic bound; X^(p-2) cheap; bit-complexity statement kept. Section 7 (l.253-275) gives the formal SLP bound. |
| 2b383b9b N4 (theorem numbering) | Done: starred theorem environments named Theorem B/C/D (l.11-13, 91, 99, 105); \ref uses removed; remark counter separate. Remark "Theorem A" kept as background. |
| 2b383b9b N5 (bibliography) | Done in refs.bib: first names; DOIs for LW02 (as reported by REV-2b383b9b; my own LW02 lookup failed), LW03, Sat05, CS00; "unverified" year wording removed (l.250ff). Satoh year 2006 verified via Crossref. |
| 2b383b9b N6 (omitted prior work) | Partly done: Coppersmith-Shparlinski added and cited (l.36, 241; verified). Declined: Kiltz-Winterhof 2004/2006 and Shparlinski's book: not verifiable within the 5-lookup budget (one DOI attempt failed); not cited rather than cited unverified. |
| 2b383b9b N7 (novelty wording C) | Done, l.248: quotes ledger "likely implied by / weaker than Lange-Winterhof-type results", not claimed novel. Novelty-status paragraph retained. |
| 2b383b9b N8 (proof wording) | Done: third term degree <= 2m, 0 when c=0 (l.147); redundant "Q != P0" removed, Q affine stated (l.153); g(s+)+g(s-) defined as symmetric expression (l.139); "2!=0!=3" replaced by "2!=0 and 3!=0" (l.76, 92, abstract l.30). |
| 2b383b9b N9 (ID line breaks) | Done: HYP/PRF/REV IDs wrapped in \mbox throughout. |
| 2b383b9b N10 (underfull boxes) | Done: \sloppy group in Section 5 (l.174-239) and one sentence reworded; final log has no warnings. |
| 15104e72 N2 (3!=0 superfluous) | Done, l.97 and l.160: noted superfluous per review, retained as formalized hypothesis. |
| 15104e72 N3 (abstract hypotheses) | Done, abstract l.29-31. |
| 15104e72 N4 (2N<r vs (r-1)/2) | Declined (reviewer: harmless); original wording kept (l.106). |
| 15104e72 N5 (F_27 instance) | Done, l.111-116: instance added, attributed to the review, stated as checked there by computer, not in Lean (k^2 in {1,16,49} = 1 mod 3 rechecked by hand; curve/order not recomputed by me). |
| 15104e72 N6 (representative convention) | Done, l.47-50. |
| New (i) SLP bound | Section 7(i), l.256-275: exact Lean statement, source commit, evidence paths; status "formally verified, independent review pending"; cost corollary marked not formalized. |
| New (ii) L2 barrier | Section 7(ii), l.278-284: proof attempt, PI-checked, not reviewed, not formalized; no proof in the report. |
| New conjecture C* | Section 7(iii), l.285-290: HYP-a8d1f541, experimental, 154,288 toy cases, p <= 997, max deficit 3. Abstract and limitations updated (l.38-40, 297). |
| Title page / provenance | Revision note and task ECDLP-36 (l.19); provenance sentence updated. |

## Build summary
`cd research/ecdlp/papers/PAP-ef6e2010-7950-47cf-bb75-05801891905b && latexmk -pdf -interaction=nonstopmode main.tex`: exit 0, 8 pages; main.log has no errors, no LaTeX/BibTeX warnings, no overfull/underfull boxes, no undefined references (grep checked). Run directly, not via `scripts/research.py exec`, so the log is not ledger evidence; the PI may rerun via exec.

## Limitations
- Lean not rebuilt; earlier Lean quotes unchanged; the SLP statement was copied from SLPBound.lean and not independently reviewed.
- F_27 example, L2 and C* claims are reported from review/ledger, not recomputed.
- Kiltz-Winterhof and Shparlinski's book remain uncited; the LW02 DOI rests on REV-2b383b9b. No full texts accessed; novelty remains unsettled.
- Revision needs re-review of changed passages, in particular Section 7.
- AI worker, same provider as reviewers; model identity self-reported.
