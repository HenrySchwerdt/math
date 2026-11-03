module

public import MathResearch.ECDLP.Basic
public import Mathlib.GroupTheory.OrderOfElement
public import Mathlib.FieldTheory.Finite.Basic

/-!
# ECDLP: homomorphic-transfer barrier lemmas

Ledger: research/ecdlp, task ECDLP-6 (TSK-899c645b-3ccf-4fcc-99a0-df147d16ee0f),
RUN-3e3276e3-3fe6-4071-b325-38d810a3f633.

Formalizes the abstract algebra of HYP-caa15771 (T1-T4) and HYP-49fb2746 (T5), and a
finite-field corollary (T6). The geometric applications (Frobenius on `E[r]`, pairings,
MOV/FR, anomalous attack) are NOT formalized here. No complexity statement is made.
-/

@[expose] public section

namespace MathResearch.ECDLP

section Transfer

variable {G H : Type*} [AddGroup G] [AddGroup H]

/-- T1 (HYP-caa15771): if `P` has prime additive order `r` and `φ : G →+ H` is a homomorphism,
then `φ P = 0` or `φ P` also has order exactly `r`. -/
theorem map_eq_zero_or_addOrderOf_eq {r : ℕ} [Fact r.Prime] {P : G} (hP : addOrderOf P = r)
    (φ : G →+ H) : φ P = 0 ∨ addOrderOf (φ P) = r := by
  have hd : addOrderOf (φ P) ∣ r := hP ▸ addOrderOf_map_dvd φ P
  rcases (Fact.out : r.Prime).eq_one_or_self_of_dvd _ hd with h | h
  · exact Or.inl (AddMonoid.addOrderOf_eq_one_iff.mp h)
  · exact Or.inr h

/-- T2 (HYP-caa15771): with `H` finite, a nonzero image of a prime-order point forces
`r ∣ |H|`. -/
theorem prime_dvd_natCard_of_map_ne_zero [Finite H] {r : ℕ} [Fact r.Prime] {P : G}
    (hP : addOrderOf P = r) (φ : G →+ H) (h : φ P ≠ 0) : r ∣ Nat.card H := by
  rcases map_eq_zero_or_addOrderOf_eq hP φ with h0 | h0
  · exact absurd h0 h
  · exact h0 ▸ addOrderOf_dvd_natCard (φ P)

/-- T3 (HYP-caa15771): if `H` is finite and `gcd (addOrderOf P) |H| = 1` then `φ P = 0`.
(Valid for arbitrary `P`, including infinite order, where the hypothesis forces `|H| = 1`.) -/
theorem map_eq_zero_of_coprime [Finite H] {P : G} (φ : G →+ H)
    (hc : Nat.Coprime (addOrderOf P) (Nat.card H)) : φ P = 0 := by
  have h1 : addOrderOf (φ P) ∣ addOrderOf P := addOrderOf_map_dvd φ P
  have h2 : addOrderOf (φ P) ∣ Nat.card H := addOrderOf_dvd_natCard (φ P)
  exact AddMonoid.addOrderOf_eq_one_iff.mp (Nat.eq_one_of_dvd_coprimes hc h1 h2)

end Transfer

section Connect

variable {G H : Type*} [AddCommGroup G] [AddCommGroup H]

/-- T4a (HYP-caa15771, connection to `Basic.lean`): for a prime-order base with nonzero
image, every solution `l` of the transferred instance is congruent mod `r` to every solution
`k` of the original instance. -/
theorem modEq_prime_of_map_solution {r : ℕ} [Fact r.Prime] (φ : G →+ H) {I : Instance G}
    (hr : addOrderOf I.base = r) (hφ : φ I.base ≠ 0) {k l : ℕ} (hk : IsSolution I k)
    (hl : IsSolution (I.map φ) l) : l ≡ k [MOD r] := by
  have h := modEq_of_map_solution φ hk hl
  rcases map_eq_zero_or_addOrderOf_eq hr φ with h0 | h0
  · exact absurd h0 hφ
  · rwa [h0] at h

/-- T4b (HYP-caa15771): if `φ I.base = 0` and `I` has a solution, every `l : ℕ` solves the
transferred instance (no information). -/
theorem isSolution_map_of_base_eq_zero (φ : G →+ H) {I : Instance G}
    (hφ : φ I.base = 0) (hI : Promise I) (l : ℕ) : IsSolution (I.map φ) l := by
  obtain ⟨k, hk⟩ := hI
  have h := IsSolution.map φ hk
  unfold IsSolution Instance.map at *
  simp only [hφ, smul_zero] at h ⊢
  exact h

end Connect

section Equivariance

/-- T5 (abstract part of HYP-49fb2746): if `f ∘ F = c • f` and `F x0 = x0` then
`(1 - c) • f x0 = 0`. -/
theorem one_sub_smul_map_fixed {r : ℕ} {V M : Type*} [AddCommGroup V] [AddCommGroup M]
    [Module (ZMod r) M] (F : V →+ V) (f : V →+ M) (c : ZMod r)
    (h : ∀ v, f (F v) = c • f v) {x0 : V} (hx : F x0 = x0) : (1 - c) • f x0 = 0 := by
  have := h x0
  rw [hx] at this
  rw [sub_smul, one_smul, ← this, sub_self]

/-- T5 (HYP-49fb2746, abstract part): moreover `c ≠ 1 → f x0 = 0` (`r` prime so `ZMod r` is a
field). -/
theorem map_fixed_eq_zero_of_ne_one {r : ℕ} [Fact r.Prime] {V M : Type*} [AddCommGroup V]
    [AddCommGroup M] [Module (ZMod r) M] (F : V →+ V) (f : V →+ M) (c : ZMod r)
    (h : ∀ v, f (F v) = c • f v) {x0 : V} (hx : F x0 = x0) (hc : c ≠ 1) : f x0 = 0 := by
  have h1 := one_sub_smul_map_fixed F f c h hx
  have hne : (1 - c) ≠ 0 := sub_ne_zero.mpr (Ne.symm hc)
  exact (smul_eq_zero.mp h1).resolve_left hne

end Equivariance

/-- T6 (corollary, finite fields): for a group hom `φ : G →* Kˣ` and `g` of prime order `r`,
`φ g ≠ 1 → r ∣ |K| - 1`. -/
theorem prime_dvd_card_sub_one_of_map_ne_one {G K : Type*} [Group G] [Field K] [Fintype K]
    {r : ℕ} [Fact r.Prime] {g : G} (hg : orderOf g = r) (φ : G →* Kˣ) (h : φ g ≠ 1) :
    r ∣ Fintype.card K - 1 := by
  classical
  have hd : orderOf (φ g) ∣ r := hg ▸ orderOf_map_dvd φ g
  rcases (Fact.out : r.Prime).eq_one_or_self_of_dvd _ hd with h1 | h1
  · exact absurd (orderOf_eq_one_iff.mp h1) h
  · rw [← Fintype.card_units, ← h1]
    exact orderOf_dvd_card

end MathResearch.ECDLP

end
