# Scientific write-ups (LaTeX → PDF)

When the PI judges a result possibly new or a coherent body of verified results worth recording,
a write-up is produced under `research/<project>/papers/<PAP-id>/` with a PAP ledger record.

1. Drafting: a bounded worker writes `main.tex` (+ `refs.bib`) in scientific style: abstract,
   precise theorem statements with hypotheses, proofs or proof references, formal-verification
   section (exact Lean declarations, toolchain, commit, axioms), experimental methodology,
   limitations, and an explicit novelty-status paragraph. Only verified sources are cited;
   unverifiable items are marked or omitted.
2. Build: `latexmk -pdf -interaction=nonstopmode main.tex` inside the paper directory, executed
   via `scripts/research.py exec` so the build log is evidence. The PDF is committed with the source.
3. Review: at least one blind adversarial review of the mathematics and one independent review of
   the manuscript (correspondence to ledger records, overclaiming, citations). Findings are
   recorded as REV records; revisions are re-reviewed.
4. Status: every write-up is an internal technical report until a human approves external
   submission. Novelty claims require a documented literature comparison.
