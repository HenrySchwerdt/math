# REV-16b2db9b-7ec3-44be-a4af-bce61bd09baf — statement-correspondence review of PRF-af19eaae

Reviewer RUN: RUN-b92a6a34-beec-419e-a904-bea4c625ecd5. Role: independent-reviewer.
Self-reported model: Claude Opus 5.5 (claude-opus-5-5), per this subagent's system
context; the runtime identity was not independently verified by the reviewer.

## Inputs (blind packet)

- Target commit 39ba7c8 (branch claude/exciting-mccarthy-yljzor). Working-tree
  `MathResearch/`, `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` and
  `research/ecdlp/proofs/checks/` were confirmed identical to 39ba7c8
  (`git diff --stat 39ba7c8 -- ...` empty; HEAD was 35f3723, which only adds draft records).
- Lean files: `MathResearch/ECDLP/Basic.lean`, `MathResearch/ECDLP/Transfer.lean`;
  toolchain `leanprover/lean4:v4.35.0`; Mathlib rev 56a005855ea17e0b0958f73ec801ae140b0a1679.
- Informal statements S1 (HYP-caa15771), S2 (HYP-49fb2746, abstract part), S3 (DLP relation).
- Claimed evidence: clean `lake build`; axioms only propext, Classical.choice, Quot.sound
  (`research/ecdlp/proofs/checks/Round2Axioms.lean`).
- Not received / not read before initial findings: author RUN reports, PRF .md, author
  confidence.

## Commands executed

All from repository root with `PATH=$HOME/.elan/bin:$PATH`.

1. `lake build` — exit 0, "Build completed successfully (2073 jobs)". A second run piped
   through `grep -iE 'warn|error|ECDLP'` returned no lines (no warnings; lakefile sets
   `-DwarningAsError=true`). Modules were replayed from cache; replay reproduces messages.
2. `lake env lean research/ecdlp/proofs/checks/Round2Axioms.lean` — exit 0. All 11
   declarations depend on a subset of {propext, Classical.choice, Quot.sound}:
   `isSolution_map_of_base_eq_zero` uses only propext; `one_sub_smul_map_fixed` uses
   propext, Quot.sound; the rest use all three. No `sorryAx`, no custom axioms.
3. `grep -nE '\b(sorry|admit|axiom|unsafe|opaque|implemented_by|native_decide)\b' -r
   MathResearch/ECDLP research/ecdlp/proofs/checks` — no matches.
4. `lake env lean <scratchpad>/review/Probe.lean` — exit 0 after one round of tactic fixes
   (first attempt exit 1 due to my own probe-script errors, not the target). Probe file is in
   the session scratchpad, not committed; its contents are summarized under Divergence attempts.

Note: `IsSolution.neg`, `addOrderOf_map_base_dvd` and `ECInstance` in Basic.lean are not in
the axiom check file; they are compiled by `lake build` (no sorry possible under the grep and
warning-as-error) but their axiom sets were not printed.

## Initial findings per declaration

Basic.lean (S3):

- `IsSolution I k := k • I.base = I.target`, `k : ℕ`. Matches S3 "k•P = Q". ℕ exponent:
  in finite groups equivalent to ℤ (probe D1b proves ∃ℕ ↔ ∃ℤ for `[Finite G]`).
- `Promise I := ∃ k : ℕ, IsSolution I k`. Docstring correctly says "cyclic monoid". In an
  infinite group this is strictly stronger than Q ∈ ⟨P⟩ (probe D1: in ℤ, (P,Q)=(1,−1) has
  integer log −1 but no ℕ solution). Irrelevant for ECDLP over finite fields; non-blocking
  but should be stated if the definition is ever used for infinite groups (e.g. E(ℚ)).
- `isSolution_iff_modEq`: given one solution k, l solves iff l ≡ k [MOD ord P]. Correct
  quantifiers; for infinite order ord = 0 and `MOD 0` is equality, which is also correct.
- `existsUnique_canonical_solution`: Promise ∧ 0 < ord → ∃! k < ord solving. Matches S3. The
  `hpos` hypothesis is necessary (ord = 0 makes "k < 0" empty) and automatic for finite G.
- `Instance.map`, `IsSolution.map`: transfer preserves solutions. Matches S3.
- `modEq_of_map_solution`: any solution l of the mapped instance satisfies l ≡ k mod
  ord(φP). This is the "determines k modulo ord(φP)" direction. The "only" (no more
  information) direction — every l ≡ k mod ord(φP) solves the mapped instance — is NOT a
  standalone declaration; it is a one-line consequence of `isSolution_iff_modEq` applied to
  `I.map φ` with `hk.map φ` (probe D3 checks it). Minor gap in S3 coverage.
- `addOrderOf_map_base_dvd`, `IsSolution.neg`, `ECInstance`: correct, not in S1–S3.
  `ECInstance` is an abbrev only; no elliptic-curve-specific theorem is proved.

Transfer.lean (S1, S2):

- T1 `map_eq_zero_or_addOrderOf_eq`: `[AddGroup G] [AddGroup H]`, `[Fact r.Prime]`,
  `addOrderOf P = r`, `φ : G →+ H` ⊢ φP = 0 ∨ ord(φP) = r. Exactly S1 clause 1, in slightly
  greater generality (non-commutative). `Fact r.Prime` is satisfiable (probe D4 instantiates
  r = 5, G = H = ZMod 5); not vacuous.
- T2 `prime_dvd_natCard_of_map_ne_zero`: `[Finite H]`, φP ≠ 0 ⊢ r ∣ Nat.card H. Matches S1
  clause 2. Keeping `[Finite H]` is the right choice: without it, Nat.card H = 0 for infinite H
  and the conclusion r ∣ 0 would be trivially true and misleading. Instantiated in probe D4.
- T3 `map_eq_zero_of_coprime`: `[Finite H]`, Coprime (ord P) (Nat.card H) ⊢ φP = 0. Matches S1
  clause 3. `[Finite H]` is superfluous (probe D2 proves the same statement without it, using
  `addOrderOf_dvd_natCard` with no finiteness); with infinite H, Coprime(n,0) forces n = 1 so
  it would hold vacuously. The formal statement is therefore slightly weaker than possible,
  never stronger than S1. The docstring's remark about infinite-order P (Coprime(0,|H|) ⇒
  |H| = 1) is correct.
- T4a `modEq_prime_of_map_solution`, T4b `isSolution_map_of_base_eq_zero`: correct
  combinations of S1 with S3 (prime-order base with nonzero image gives full information mod r;
  zero image gives none, under the Promise).
- T5 `one_sub_smul_map_fixed`, `map_fixed_eq_zero_of_ne_one`: V is only an AddCommGroup, F is
  `V →+ V`, f is `V →+ M`, M is a `ZMod r`-module, c : ZMod r. S2 asks for V an F_r-vector
  space; the formal version drops that and is strictly more general. The proof uses only
  `h x0` and `hx`; additivity of F and f is never used. This does not trivialize the result —
  it reflects that S2's abstract part is a one-line identity f(x0) = f(F x0) = c·f(x0). The
  `Module (ZMod r) M` assumption is satisfiable (probe D4 with M = ZMod 5, c = 2) and the c = 1
  exclusion is genuinely needed (probe: f = id, F = id, c = 1, f(1) ≠ 0). Matches S2.
- T6 `prime_dvd_card_sub_one_of_map_ne_one`: φ : G →* Kˣ, K finite field, ord g = r prime,
  φg ≠ 1 ⊢ r ∣ |K| − 1. ℕ subtraction is safe because |K| ≥ 2. Correct; not in S1–S3.

Not captured from S1–S3: (a) the S3 "only modulo" converse as a named lemma (derivable, see
above); (b) nothing else. Outside the packet but worth stating plainly: no geometric
application (Frobenius on E[r], Weil/Tate pairings, MOV/Frey–Rück, anomalous attack) and no
complexity claim is formalized; the file header says so.

## Divergence attempts

- D1 ℕ vs ℤ Promise in an infinite group: divergence FOUND but harmless for ECDLP over finite
  fields; docstring already says "cyclic monoid". Formalized in probe.
- D1b ℕ vs ℤ in finite groups: no divergence (proved).
- D2 dropping `[Finite H]` in T3: formal statement still holds (proved) → hypothesis is
  superfluous, not trivializing.
- D2' Nat.card = 0 trap in T2: avoided by `[Finite H]`.
- D3 "determines k only modulo ord(φP)": converse holds (proved from existing lemmas); not a
  standalone declaration.
- D4 vacuity checks: T1, T2, T5b instantiated on ZMod 5; c = 1 counter-instance shows T5b's
  `hc` is needed.
- D5 infinite-order base: `isSolution_iff_modEq` reduces to uniqueness via MOD 0; consistent.
- Checked that `Module (ZMod r) M` over an existing AddCommGroup cannot conflict (ZMod-module
  structures are unique when they exist); no impossible-instance vacuity.
- No instance found where an informal S1–S3 claim is true but the formal statement false, or
  vice versa within the stated hypotheses.

## Decision and rationale

Decision: **accept** (formal correctness of the listed declarations against S1–S3 only).

Rationale: build and axiom evidence reproduced; no sorry/axiom/unsafe; every declaration's
statement matches or generalizes the informal claim with non-vacuous, satisfiable
hypotheses. Non-blocking suggestions: (1) add the S3 converse lemma
(`isSolution_map_of_modEq`); (2) drop `[Finite H]` from T3 or note it is unnecessary;
(3) note in `Promise` docs that it differs from Q ∈ ⟨P⟩ for infinite-order P; (4) note in T5
docs that additivity of F, f is unused; (5) add `IsSolution.neg` and
`addOrderOf_map_base_dvd` to the axiom check file.

Scientific significance: all of these are standard, elementary textbook facts (Lagrange /
order divisibility for homomorphic images, uniqueness of discrete logs modulo the order,
the eigenvalue argument behind the MOV/Frey–Rück embedding-degree condition). They are
useful verified infrastructure, not new results, and they say nothing about the hardness or
complexity of ECDLP.

Complexity: not applicable — formal correctness only.

## After reading author assessment

Added after the initial findings above were written; the initial findings were not edited.

- The PRF cites source commit b43063b; `git diff --stat b43063b 39ba7c8` shows only the PRF
  .json/.md added, so the Lean sources reviewed at 39ba7c8 are identical to the cited source.
- The PRF's correspondence notes (ℕ exponents; T3 holds for any P; T5 is the abstract module
  statement only; no Frobenius/pairing application or "unification of MOV and anomalous
  attacks" formalized; elementary, not new; no bit-complexity content) agree with my findings.
- The PRF does not mention: the ℕ-Promise vs ⟨P⟩ difference for infinite-order bases, the
  superfluous `[Finite H]` in T3, the missing standalone "only modulo" converse, unused
  additivity in T5, or that three Basic.lean declarations are not in the axiom check file.
  None changes the decision. Decision remains **accept**.

## Limitations

- Reviewed only statement correspondence and build/axiom evidence at 39ba7c8; did not
  review the geometric HYP content, applications, or any complexity claims (none are made).
- Build replayed cached oleans; a clean rebuild from scratch was not run.
- Probe file lives in the session scratchpad and is not preserved in the repository.
- Same provider family as the author's PI (Anthropic); independence is role-based, not
  provider-based.
