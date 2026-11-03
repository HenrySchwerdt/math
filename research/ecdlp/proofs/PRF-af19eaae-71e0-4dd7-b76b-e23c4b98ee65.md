# PRF-af19eaae-71e0-4dd7-b76b-e23c4b98ee65 — DLP relation and transfer-barrier lemmas (Lean)

## Question, selection rationale and inputs
Formalize the exact DLP relation and the abstract algebra of HYP-caa15771 and HYP-49fb2746.

## Approach and observed execution
Basic.lean by PI; Transfer.lean by the formalization subagent (RUN-3e3276e3). PI re-ran
`lake build` and the axiom audit via `research.py exec` (evidence listed in JSON).

## Claims and verification
Declarations (namespace `MathResearch.ECDLP`): isSolution_iff_modEq,
existsUnique_canonical_solution, modEq_of_map_solution, map_eq_zero_or_addOrderOf_eq,
prime_dvd_natCard_of_map_ne_zero, map_eq_zero_of_coprime, modEq_prime_of_map_solution,
isSolution_map_of_base_eq_zero, one_sub_smul_map_fixed, map_fixed_eq_zero_of_ne_one,
prime_dvd_card_sub_one_of_map_ne_one. Toolchain v4.35.0, Mathlib 56a00585, source commit
b43063bb. Axioms: standard only.

Correspondence (PI reading, pending independent review): exponents are natural numbers;
T3 holds for any P; T5 is the abstract module statement only — the Frobenius/pairing
application and the "unification of MOV and anomalous attacks" are NOT formalized.

## Outcome, limitations and next action
Formally verified elementary lemmas; not new mathematics. No bit-complexity content.
Next: independent correspondence review.
