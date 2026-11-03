module

public import MathResearch.ECDLP.LinearInterp
public import Mathlib.Algebra.Polynomial.Eval.Defs
public import Mathlib.RingTheory.EuclideanDomain

/-!
# ECDLP: straight-line programs with division and x-only discrete-log barrier

Ledger: research/ecdlp, task ECDLP-34 (TSK-a482f006-a0c3-406f-8f1c-52c7bcb63fc0),
RUN-ce6e9aee-1730-443f-86c6-48b9dd3ba467, hypothesis HYP-6aef8c30-2942-4079-8d0a-fc2ae8b6c200.

This file extends `MathResearch.ECDLP.SLPBound` (division-free, `N ≤ 3 * 2 ^ L + 2`) to programs
with division.

**Rational analogue of Theorem C** (`degree_bound_rational_short_weierstrass`): if `A, B ∈ F[X]`
have degree `≤ d`, `B (x (kP)) ≠ 0` and `A (x (kP)) = k * B (x (kP))` for `1 ≤ k ≤ N`, `2 N < r`,
then `N ≤ 3 d + 2`. Proof: the cleared symmetric polynomial `Nrat` of degree `≤ 3 d` vanishes at the
`N - 2` nodes `x (kP)`, `2 ≤ k ≤ N - 1`; it is not the zero polynomial because `Nrat = 0` would
propagate `A = k B` along the whole orbit up to `k = r - 1` (after reducing `A, B` to coprime form),
and `x ((r-1) P) = x P`, `x ((r-2) P) = x (2 P)` then force `2 = 0` in `F`.

**SLP with division.** `Op` has `div`. Values are evaluated in `F` (`x / 0 = 0` as in Lean) and
formally as pairs `(num, den)` of polynomials with `max (natDegree num) (natDegree den) ≤ 2 ^ i`.
`Defined prog u` says that every division in `prog` has a nonzero divisor value at `u`; then the
value at `u` equals `num (u) / den (u)` with `den (u) ≠ 0`.

**Not formalized.** Bit-complexity; division-free programs are not embedded in this `Op` type;
the converse `den (u) ≠ 0 → Defined`. Only a statement about the number of field operations.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace RationalSLP

section Cleared

variable {K : Type*} [Field K]

/-- Cleared symmetric monomial: evaluates to `D ^ max i j * (z₁ ^ i z₂ ^ j + z₁ ^ j z₂ ^ i)`. -/
noncomputable def W (SA TB D : K[X]) (i j : ℕ) : K[X] :=
  TB ^ min i j * Interp.q SA TB D (max i j - min i j)

theorem eval_W (SA TB D : K[X]) (u z₁ z₂ : K)
    (hS : (z₁ + z₂) * D.eval u = SA.eval u) (hT : z₁ * z₂ * D.eval u = TB.eval u) (i j : ℕ) :
    (W SA TB D i j).eval u = D.eval u ^ max i j * (z₁ ^ i * z₂ ^ j + z₁ ^ j * z₂ ^ i) := by
  unfold W
  rw [eval_mul, eval_pow, Interp.eval_q SA TB D u z₁ z₂ hS hT, ← hT]
  rcases le_total i j with h | h
  · obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le h
    simp only [min_eq_left h, max_eq_right h, Nat.add_sub_cancel_left]
    ring
  · obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le h
    simp only [min_eq_right h, max_eq_left h, Nat.add_sub_cancel_left]
    ring

/-- `D ^ d * (f (z₁) g (z₂) + f (z₂) g (z₁))` as a polynomial in `u`. -/
noncomputable def CS (SA TB D f g : K[X]) (d : ℕ) : K[X] :=
  ∑ i ∈ Finset.range (d + 1), ∑ j ∈ Finset.range (d + 1),
    C (f.coeff i * g.coeff j) * (D ^ (d - max i j) * W SA TB D i j)

theorem eval_CS (SA TB D f g : K[X]) (d : ℕ) (hf : f.natDegree ≤ d) (hg : g.natDegree ≤ d)
    (u z₁ z₂ : K) (hS : (z₁ + z₂) * D.eval u = SA.eval u)
    (hT : z₁ * z₂ * D.eval u = TB.eval u) :
    (CS SA TB D f g d).eval u =
      D.eval u ^ d * (f.eval z₁ * g.eval z₂ + f.eval z₂ * g.eval z₁) := by
  have hz : ∀ p : K[X], p.natDegree ≤ d → ∀ z : K,
      p.eval z = ∑ i ∈ Finset.range (d + 1), p.coeff i * z ^ i := fun p hp z => by
    rw [eval_eq_sum_range' (Nat.lt_succ_of_le hp)]
  have term : ∀ i ∈ Finset.range (d + 1), ∀ j ∈ Finset.range (d + 1),
      (C (f.coeff i * g.coeff j) * (D ^ (d - max i j) * W SA TB D i j)).eval u =
        D.eval u ^ d * (f.coeff i * z₁ ^ i * (g.coeff j * z₂ ^ j) +
          f.coeff i * z₂ ^ i * (g.coeff j * z₁ ^ j)) := by
    intro i hi j hj
    have hi' : i ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
    have hj' : j ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hj)
    have hmx : max i j ≤ d := max_le hi' hj'
    have e : D.eval u ^ d = D.eval u ^ (d - max i j) * D.eval u ^ max i j := by
      rw [← pow_add]; congr 1; omega
    rw [eval_mul, eval_C, eval_mul, eval_pow, eval_W SA TB D u z₁ z₂ hS hT, e]
    ring
  simp only [CS, eval_finsetSum]
  rw [Finset.sum_congr rfl (fun i hi => Finset.sum_congr rfl (fun j hj => term i hi j hj))]
  simp only [← Finset.mul_sum, Finset.sum_add_distrib]
  rw [hz f hf z₁, hz g hg z₂, hz f hf z₂, hz g hg z₁]
  simp only [← Finset.sum_mul]

theorem natDegree_CS_le (SA TB D f g : K[X]) (d : ℕ) (hSA : SA.natDegree ≤ 2)
    (hTB : TB.natDegree ≤ 2) (hBD : (TB * D).natDegree ≤ 4) (hD : D.natDegree ≤ 2) :
    (CS SA TB D f g d).natDegree ≤ 2 * d := by
  refine natDegree_sum_le_of_forall_le _ _ (fun i hi => natDegree_sum_le_of_forall_le _ _
    (fun j hj => ?_))
  have hi' : i ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
  have hj' : j ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hj)
  refine (natDegree_C_mul_le _ _).trans ((natDegree_mul_le).trans ?_)
  have h1 : (D ^ (d - max i j)).natDegree ≤ 2 * (d - max i j) :=
    natDegree_pow_le.trans (by nlinarith)
  have h2 : (TB ^ min i j).natDegree ≤ 2 * min i j :=
    natDegree_pow_le.trans (by have := Nat.mul_le_mul_left (min i j) hTB; omega)
  have h3 := Interp.natDegree_q_le SA TB D hSA hBD (max i j - min i j)
  have h4 : (W SA TB D i j).natDegree ≤ 2 * min i j + 2 * (max i j - min i j) :=
    (natDegree_mul_le).trans (add_le_add h2 h3)
  have : min i j ≤ max i j := min_le_max
  omega

/-- The cleared rational second-difference polynomial: `D ^ d` times
`h (u) (f (z₁) h (z₂) + f (z₂) h (z₁)) - f (u) (2 h (z₁) h (z₂))`. -/
noncomputable def Nrat (SA TB D f h : K[X]) (d : ℕ) : K[X] :=
  h * CS SA TB D f h d - f * CS SA TB D h h d

theorem eval_Nrat (SA TB D f h : K[X]) (d : ℕ) (hf : f.natDegree ≤ d) (hh : h.natDegree ≤ d)
    (u z₁ z₂ : K) (hS : (z₁ + z₂) * D.eval u = SA.eval u)
    (hT : z₁ * z₂ * D.eval u = TB.eval u) :
    (Nrat SA TB D f h d).eval u =
      D.eval u ^ d * (h.eval u * (f.eval z₁ * h.eval z₂ + f.eval z₂ * h.eval z₁) -
        f.eval u * (h.eval z₁ * h.eval z₂ + h.eval z₂ * h.eval z₁)) := by
  unfold Nrat
  rw [eval_sub, eval_mul, eval_mul, eval_CS SA TB D f h d hf hh u z₁ z₂ hS hT,
    eval_CS SA TB D h h d hh hh u z₁ z₂ hS hT]
  ring

theorem natDegree_Nrat_le (SA TB D f h : K[X]) (d : ℕ) (hSA : SA.natDegree ≤ 2)
    (hTB : TB.natDegree ≤ 2) (hBD : (TB * D).natDegree ≤ 4) (hD : D.natDegree ≤ 2)
    (hf : f.natDegree ≤ d) (hh : h.natDegree ≤ d) :
    (Nrat SA TB D f h d).natDegree ≤ 3 * d := by
  have c1 := natDegree_CS_le SA TB D f h d hSA hTB hBD hD
  have c2 := natDegree_CS_le SA TB D h h d hSA hTB hBD hD
  unfold Nrat
  refine (natDegree_sub_le _ _).trans (max_le ?_ ?_)
  · exact (natDegree_mul_le).trans (by omega)
  · exact (natDegree_mul_le).trans (by omega)

end Cleared

section Curve

open WeierstrassCurve WeierstrassCurve.Affine CurveX

variable {F : Type*} [Field F] [DecidableEq F]

omit [DecidableEq F] in
theorem xCoord_neg {W : Affine F} (Q : W.Point) : xCoord (-Q) = xCoord Q := by
  cases Q with
  | zero => rfl
  | some x y h => simp [Point.neg_some]

theorem xCoord_smul_sub {W : Affine F} {P : W.Point} {r : ℕ} (hr : addOrderOf P = r) {j : ℕ}
    (hj : j ≤ r) : xCoord ((r - j) • P) = xCoord (j • P) := by
  have h0 : r • P = 0 := hr ▸ addOrderOf_nsmul_eq_zero P
  have h : (r - j) • P = -(j • P) := by
    refine eq_neg_of_add_eq_zero_left ?_
    rw [← add_nsmul, Nat.sub_add_cancel hj, h0]
  rw [h, xCoord_neg]

/-- The x-addition relations of `CurveX.smul_relations` for every `2 ≤ k ≤ r - 2` (no
`2 m < r` restriction), together with `x (kP) ≠ x P`. -/
theorem smul_relations_full {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {P : W.Point} {r : ℕ} (hr : addOrderOf P = r) {k : ℕ} (hk : 2 ≤ k) (hkr : k + 2 ≤ r) :
    xCoord (k • P) ≠ xCoord P ∧
    (xCoord ((k + 1) • P) + xCoord ((k - 1) • P)) * (xCoord (k • P) - xCoord P) ^ 2 =
      2 * ((xCoord P * xCoord (k • P) + W.a₄) * (xCoord (k • P) + xCoord P) + 2 * W.a₆) ∧
    xCoord ((k + 1) • P) * xCoord ((k - 1) • P) * (xCoord (k • P) - xCoord P) ^ 2 =
      (xCoord P * xCoord (k • P) - W.a₄) ^ 2 - 4 * W.a₆ * (xCoord (k • P) + xCoord P) := by
  have hP0 : P ≠ 0 := by
    simpa using nsmul_ne_zero_of_lt hr (k := 1) le_rfl (by omega)
  have hQ0 := nsmul_ne_zero_of_lt hr (P := P) (k := k) (by omega) (by omega)
  have hx : xCoord (k • P) ≠ xCoord P := by
    intro h
    have h' := eq_or_neg_of_xCoord_eq hP0 hQ0 h.symm
    have := eq_of_smul_eq_or_neg hr (j := 1) (k := k) le_rfl (by omega) (by omega)
      (by rw [one_smul]; exact h')
    omega
  refine ⟨hx, ?_⟩
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
  have e1 : (j + 1 + 1) • P = (j + 1) • P + P := succ_nsmul P (j + 1)
  have e2 : j • P = (j + 1) • P - P := eq_sub_of_add_eq (succ_nsmul P j).symm
  simp only [Nat.add_sub_cancel]
  revert hx hQ0 e1 e2
  generalize (j + 1) • P = Q
  intro hQ0 hx e1 e2
  rw [e1, e2]
  clear e1 e2
  cases Q with
  | zero => exact absurd rfl hQ0
  | some u v hQ =>
    cases P with
    | zero => exact absurd rfl hP0
    | some x₀ y₀ hP =>
      exact xCoord_relations h1 h2 h3 hQ hP hx

/-- **Rational analogue of Theorem C, coprime form.** -/
theorem degree_bound_rational_coprime {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (A B : F[X]) (d : ℕ) (hA : A.natDegree ≤ d)
    (hB : B.natDegree ≤ d) (hcop : IsCoprime A B)
    (hB0 : ∀ k : ℕ, 1 ≤ k → k ≤ N → B.eval (xCoord (k • P)) ≠ 0)
    (hAB : ∀ k : ℕ, 1 ≤ k → k ≤ N → A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P))) :
    N ≤ 3 * d + 2 := by
  by_cases hN3 : N ≤ 2
  · omega
  replace hN3 := not_le.mp hN3
  set a := W.a₄
  set b := W.a₆
  set x₀ := xCoord P
  have hD : ∀ k : ℕ, 2 ≤ k → k + 2 ≤ r → (Interp.den x₀).eval (xCoord (k • P)) ≠ 0 := by
    intro k hk hkr
    have := (smul_relations_full h1 h2 h3 hr hk hkr).1
    simp only [Interp.den, eval_pow, eval_sub, eval_X, eval_C]
    exact pow_ne_zero _ (sub_ne_zero.mpr this)
  have key : ∀ k : ℕ, 2 ≤ k → k + 2 ≤ r →
      (Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d).eval
          (xCoord (k • P)) =
        (Interp.den x₀).eval (xCoord (k • P)) ^ d *
          (B.eval (xCoord (k • P)) * (A.eval (xCoord ((k + 1) • P)) * B.eval (xCoord ((k - 1) • P))
              + A.eval (xCoord ((k - 1) • P)) * B.eval (xCoord ((k + 1) • P))) -
            A.eval (xCoord (k • P)) * (B.eval (xCoord ((k + 1) • P)) *
              B.eval (xCoord ((k - 1) • P)) + B.eval (xCoord ((k - 1) • P)) *
                B.eval (xCoord ((k + 1) • P)))) := by
    intro k hk hkr
    obtain ⟨_, hS, hT⟩ := smul_relations_full h1 h2 h3 hr hk hkr
    exact eval_Nrat _ _ _ A B d hA hB _ _ _ (by simpa [Interp.numS, Interp.den] using hS)
      (by simpa [Interp.numT, Interp.den] using hT)
  have hnz : Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d ≠ 0 := by
    intro hz
    have prop : ∀ k : ℕ, N ≤ k → k ≤ r - 1 →
        B.eval (xCoord (k • P)) ≠ 0 ∧ A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P)) ∧
        B.eval (xCoord ((k - 1) • P)) ≠ 0 ∧
        A.eval (xCoord ((k - 1) • P)) = ((k - 1 : ℕ) : F) * B.eval (xCoord ((k - 1) • P)) := by
      intro k hk
      induction k, hk using Nat.le_induction with
      | base =>
        intro _
        exact ⟨hB0 N (by omega) le_rfl, hAB N (by omega) le_rfl, hB0 (N - 1) (by omega) (by omega),
          hAB (N - 1) (by omega) (by omega)⟩
      | succ n hn ih =>
        intro hle
        obtain ⟨hb1, ha1, hb2, ha2⟩ := ih (by omega)
        have hkey := key n (by omega) (by omega)
        rw [hz, eval_zero] at hkey
        have hDn := hD n (by omega) (by omega)
        have hbr := (mul_eq_zero.mp hkey.symm).resolve_left (pow_ne_zero _ hDn)
        rw [ha1, ha2] at hbr
        have hc : ((n - 1 : ℕ) : F) = (n : F) - 1 := by
          rw [Nat.cast_sub (by omega)]; simp
        rw [hc] at hbr
        have hmain : B.eval (xCoord (n • P)) * B.eval (xCoord ((n - 1) • P)) *
            (A.eval (xCoord ((n + 1) • P)) - ((n : F) + 1) * B.eval (xCoord ((n + 1) • P))) = 0 := by
          linear_combination hbr
        have hmain' := (mul_eq_zero.mp hmain).resolve_left (mul_ne_zero hb1 hb2)
        have hA1 : A.eval (xCoord ((n + 1) • P)) = ((n : F) + 1) * B.eval (xCoord ((n + 1) • P)) :=
          sub_eq_zero.mp hmain'
        have hB1 : B.eval (xCoord ((n + 1) • P)) ≠ 0 := by
          intro hb0
          obtain ⟨s, t, hst⟩ := hcop
          have := congrArg (eval (xCoord ((n + 1) • P))) hst
          simp only [eval_add, eval_mul, eval_one] at this
          rw [hA1, hb0] at this
          simp at this
        refine ⟨hB1, by rw [hA1]; push_cast; ring, ?_, ?_⟩
        · simpa using hb1
        · simpa using ha1
    obtain ⟨s, rfl⟩ : ∃ s, r = s + 3 := ⟨r - 3, by omega⟩
    obtain ⟨hb1, ha1, hb2, ha2⟩ := prop (s + 2) (by omega) (by omega)
    have ex1 : xCoord ((s + 2) • P) = xCoord ((1 : ℕ) • P) := by
      have := xCoord_smul_sub hr (j := 1) (by omega)
      rwa [show s + 3 - 1 = s + 2 by omega] at this
    have ex2 : xCoord ((s + 2 - 1) • P) = xCoord ((2 : ℕ) • P) := by
      have := xCoord_smul_sub hr (j := 2) (by omega)
      rwa [show s + 3 - 2 = s + 2 - 1 by omega] at this
    rw [ex1] at hb1 ha1
    rw [ex2] at hb2 ha2
    have u1 := hAB 1 le_rfl (by omega)
    have u2 := hAB 2 (by omega) (by omega)
    have c1 : ((s + 2 : ℕ) : F) = 1 := by
      have := ha1.symm.trans u1
      push_cast at this ⊢
      exact mul_right_cancel₀ hb1 (by simpa using this)
    have c2 : ((s + 2 - 1 : ℕ) : F) = 2 := by
      have := ha2.symm.trans u2
      exact mul_right_cancel₀ hb2 this
    rw [show s + 2 - 1 = s + 1 by omega] at c2
    push_cast at c1 c2
    exact h2' (by linear_combination c1 - c2)
  have hroots : ((Finset.Icc 2 (N - 1)).image (fun k : ℕ => xCoord (k • P))) ⊆
      (Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d).roots.toFinset := by
    intro z hz
    obtain ⟨k, hk, rfl⟩ := Finset.mem_image.mp hz
    obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hk
    rw [Multiset.mem_toFinset, mem_roots hnz, IsRoot.def, key k hk1 (by omega)]
    have e1 := hAB (k + 1) (by omega) (by omega)
    have e2 := hAB (k - 1) (by omega) (by omega)
    have e3 := hAB k (by omega) (by omega)
    have hc : ((k - 1 : ℕ) : F) = (k : F) - 1 := by
      rw [Nat.cast_sub (by omega)]; simp
    rw [hc] at e2
    rw [e1, e2, e3]
    push_cast
    ring
  have hcard := Finset.card_le_card hroots
  rw [Finset.card_image_of_injOn ((xCoord_smul_injOn hr hN).mono (by
    intro k hk; simp only [Finset.coe_Icc, Set.mem_Icc] at hk ⊢; omega))] at hcard
  have h2' := (Multiset.toFinset_card_le _).trans
    (card_roots' (Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d))
  have hdeg := natDegree_Nrat_le (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d
    (Interp.natDegree_numS_le a b x₀) (by unfold Interp.numT; compute_degree)
    (Interp.natDegree_numT_den_le a b x₀) (Interp.den_natDegree x₀).le hA hB
  simp only [Nat.card_Icc] at hcard
  omega

/-- **Rational analogue of Theorem C (general form).** `W` short Weierstrass over `F` with
`2 ≠ 0`, `P` of order `r`, `2 N < r`. If `A, B ∈ F[X]` have `natDegree ≤ d`, `B (x (kP)) ≠ 0` and
`A (x (kP)) = k * B (x (kP))` for `1 ≤ k ≤ N`, then `N ≤ 3 d + 2`. No coprimality assumption. -/
theorem degree_bound_rational_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (A B : F[X]) (d : ℕ) (hA : A.natDegree ≤ d)
    (hB : B.natDegree ≤ d)
    (hB0 : ∀ k : ℕ, 1 ≤ k → k ≤ N → B.eval (xCoord (k • P)) ≠ 0)
    (hAB : ∀ k : ℕ, 1 ≤ k → k ≤ N → A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P))) :
    N ≤ 3 * d + 2 := by
  by_cases hN0 : N = 0
  · omega
  have hBne : B ≠ 0 := by
    intro h
    exact hB0 1 le_rfl (by omega) (by simp [h])
  set g := GCDMonoid.gcd A B with hg
  have hgne : g ≠ 0 := by
    intro h
    exact hBne ((gcd_eq_zero_iff A B).mp h).2
  have hAe : A = g * (A / g) :=
    (EuclideanDomain.mul_div_cancel' hgne (gcd_dvd_left A B)).symm
  have hBe : B = g * (B / g) :=
    (EuclideanDomain.mul_div_cancel' hgne (gcd_dvd_right A B)).symm
  have hdeg : ∀ p : F[X], p = g * (p / g) → p.natDegree ≤ d → (p / g).natDegree ≤ d := by
    intro p hp hpd
    by_cases h0 : p / g = 0
    · rw [h0]; simp
    · have hp0 : p ≠ 0 := by rw [hp]; exact mul_ne_zero hgne h0
      have := natDegree_mul hgne h0
      rw [← hp] at this
      omega
  have hgx : ∀ k : ℕ, 1 ≤ k → k ≤ N → g.eval (xCoord (k • P)) ≠ 0 := by
    intro k hk hk'
    have := hB0 k hk hk'
    rw [hBe, eval_mul] at this
    exact left_ne_zero_of_mul this
  refine degree_bound_rational_coprime h1 h2 h3 h2' P r hr N hN (A / g) (B / g) d
    (hdeg A hAe hA) (hdeg B hBe hB) (isCoprime_div_gcd_div_gcd hBne) ?_ ?_
  · intro k hk hk'
    have := hB0 k hk hk'
    rw [hBe, eval_mul] at this
    exact right_ne_zero_of_mul this
  · intro k hk hk'
    have h := hAB k hk hk'
    rw [hAe, hBe, eval_mul, eval_mul] at h
    refine mul_left_cancel₀ (hgx k hk hk') ?_
    rw [h]; ring

end Curve

section SLP

/-- One instruction of a straight-line program over a field with a single input variable `u`.
Operations refer to earlier results by index (out-of-range indices read `0`). -/
inductive Op (F : Type*) where
  | const (c : F)
  | var
  | add (i j : ℕ)
  | sub (i j : ℕ)
  | mul (i j : ℕ)
  | div (i j : ℕ)

section Semantics

variable {F : Type*} [Field F]

/-- Value of one op at input `u`, given the values `acc` computed so far
(`x / 0 = 0` in Lean; definedness is tracked separately by `okStep`). -/
def stepVal (u : F) (acc : List F) : Op F → F
  | .const c => c
  | .var => u
  | .add i j => acc.getD i 0 + acc.getD j 0
  | .sub i j => acc.getD i 0 - acc.getD j 0
  | .mul i j => acc.getD i 0 * acc.getD j 0
  | .div i j => acc.getD i 0 / acc.getD j 0

/-- A division is defined at this step iff the divisor value is nonzero. -/
def okStep (acc : List F) : Op F → Prop
  | .div _ j => acc.getD j 0 ≠ 0
  | _ => True

/-- Run a program, appending one value per op. -/
def runVal (u : F) : List (Op F) → List F → List F
  | [], acc => acc
  | o :: rest, acc => runVal u rest (acc ++ [stepVal u acc o])

/-- All values of `prog` at the input `u`. -/
def evalAt (prog : List (Op F)) (u : F) : List F := runVal u prog []

/-- Every division of the program has a nonzero divisor value at the input `u`. -/
def defd (u : F) : List (Op F) → List F → Prop
  | [], _ => True
  | o :: rest, acc => okStep acc o ∧ defd u rest (acc ++ [stepVal u acc o])

/-- `prog` is defined at `u`: every division has a nonzero divisor value (in `F`). -/
def Defined (prog : List (Op F)) (u : F) : Prop := defd u prog []

/-- Formal fraction operations on pairs `(num, den)`. -/
noncomputable def stepFrac (acc : List (F[X] × F[X])) : Op F → F[X] × F[X]
  | .const c => (C c, 1)
  | .var => (X, 1)
  | .add i j => ((acc.getD i (0, 1)).1 * (acc.getD j (0, 1)).2 +
      (acc.getD j (0, 1)).1 * (acc.getD i (0, 1)).2, (acc.getD i (0, 1)).2 * (acc.getD j (0, 1)).2)
  | .sub i j => ((acc.getD i (0, 1)).1 * (acc.getD j (0, 1)).2 -
      (acc.getD j (0, 1)).1 * (acc.getD i (0, 1)).2, (acc.getD i (0, 1)).2 * (acc.getD j (0, 1)).2)
  | .mul i j => ((acc.getD i (0, 1)).1 * (acc.getD j (0, 1)).1,
      (acc.getD i (0, 1)).2 * (acc.getD j (0, 1)).2)
  | .div i j => ((acc.getD i (0, 1)).1 * (acc.getD j (0, 1)).2,
      (acc.getD i (0, 1)).2 * (acc.getD j (0, 1)).1)

/-- Formal semantics: the `(num, den)` pair computed by each step. -/
noncomputable def runFrac : List (Op F) → List (F[X] × F[X]) → List (F[X] × F[X])
  | [], acc => acc
  | o :: rest, acc => runFrac rest (acc ++ [stepFrac acc o])

/-- Formal `(num, den)` semantics of a program. -/
noncomputable def evalFrac (prog : List (Op F)) : List (F[X] × F[X]) := runFrac prog []

theorem getD_snoc {α : Type*} (l : List α) (x d : α) (i : ℕ) :
    (l ++ [x]).getD i d = if i < l.length then l.getD i d else if i = l.length then x else d := by
  simp only [List.getD_eq_getElem?_getD, List.getElem?_append]
  by_cases h : i < l.length
  · simp [h]
  · by_cases h' : i = l.length
    · subst h'; simp
    · have : ¬ (i - l.length < 1) := by omega
      simp [h, h', this]

/-- Agreement invariant between formal pairs and values. -/
def Inv (u : F) (accF : List (F[X] × F[X])) (accV : List F) : Prop :=
  accF.length = accV.length ∧ ∀ i : ℕ, (accF.getD i (0, 1)).2.eval u ≠ 0 ∧
    accV.getD i 0 = (accF.getD i (0, 1)).1.eval u / (accF.getD i (0, 1)).2.eval u

theorem inv_step (u : F) (accF : List (F[X] × F[X])) (accV : List F) (o : Op F)
    (h : Inv u accF accV) (hok : okStep accV o) :
    Inv u (accF ++ [stepFrac accF o]) (accV ++ [stepVal u accV o]) := by
  obtain ⟨hlen, hi⟩ := h
  have hnew : (stepFrac accF o).2.eval u ≠ 0 ∧
      stepVal u accV o = (stepFrac accF o).1.eval u / (stepFrac accF o).2.eval u := by
    cases o with
    | const c => simp [stepFrac, stepVal]
    | var => simp [stepFrac, stepVal]
    | add i j =>
      obtain ⟨hdi, hvi⟩ := hi i
      obtain ⟨hdj, hvj⟩ := hi j
      simp only [stepFrac, stepVal, eval_mul, eval_add]
      refine ⟨mul_ne_zero hdi hdj, ?_⟩
      rw [hvi, hvj]; field_simp
    | sub i j =>
      obtain ⟨hdi, hvi⟩ := hi i
      obtain ⟨hdj, hvj⟩ := hi j
      simp only [stepFrac, stepVal, eval_mul, eval_sub]
      refine ⟨mul_ne_zero hdi hdj, ?_⟩
      rw [hvi, hvj]; field_simp
    | mul i j =>
      obtain ⟨hdi, hvi⟩ := hi i
      obtain ⟨hdj, hvj⟩ := hi j
      simp only [stepFrac, stepVal, eval_mul]
      refine ⟨mul_ne_zero hdi hdj, ?_⟩
      rw [hvi, hvj]; field_simp
    | div i j =>
      obtain ⟨hdi, hvi⟩ := hi i
      obtain ⟨hdj, hvj⟩ := hi j
      have hnj : (accF.getD j (0, 1)).1.eval u ≠ 0 := by
        intro h0
        apply hok
        show accV.getD j 0 = 0
        rw [hvj, h0, zero_div]
      simp only [stepFrac, stepVal, eval_mul]
      refine ⟨mul_ne_zero hdi hnj, ?_⟩
      rw [hvi, hvj]; field_simp
  refine ⟨by simp [hlen], fun i => ?_⟩
  rw [getD_snoc, getD_snoc, hlen]
  by_cases h1 : i < accV.length
  · simp only [h1, ↓reduceIte]; exact hi i
  · by_cases h2 : i = accV.length
    · subst h2; simp only [lt_irrefl, ↓reduceIte]; exact hnew
    · simp only [h1, h2, ↓reduceIte]; simp

theorem inv_run (u : F) : ∀ (prog : List (Op F)) (accF : List (F[X] × F[X])) (accV : List F),
    Inv u accF accV → defd u prog accV → Inv u (runFrac prog accF) (runVal u prog accV)
  | [], _, _, h, _ => h
  | o :: rest, accF, accV, h, hd =>
    inv_run u rest _ _ (inv_step u accF accV o h hd.1) hd.2

theorem inv_nil (u : F) : Inv u [] [] := by
  refine ⟨rfl, fun i => ?_⟩
  simp

/-- **Semantic agreement.** If every division of `prog` is defined at `u`, then each value of `prog`
at `u` equals `num (u) / den (u)` for the formal pair, and every formal denominator is nonzero at
`u`. (Indices out of range read the pair `(0, 1)` and the value `0`.) -/
theorem eval_agreement (prog : List (Op F)) (u : F) (hd : Defined prog u) (i : ℕ) :
    ((evalFrac prog).getD i (0, 1)).2.eval u ≠ 0 ∧
      (evalAt prog u).getD i 0 =
        ((evalFrac prog).getD i (0, 1)).1.eval u / ((evalFrac prog).getD i (0, 1)).2.eval u :=
  (inv_run u prog [] [] (inv_nil u) hd).2 i

/-- A pair has both degrees `≤ n`. -/
def DegLe (p : F[X] × F[X]) (n : ℕ) : Prop := p.1.natDegree ≤ n ∧ p.2.natDegree ≤ n

theorem DegLe.mono {p : F[X] × F[X]} {n m : ℕ} (h : DegLe p n) (hnm : n ≤ m) : DegLe p m :=
  ⟨h.1.trans hnm, h.2.trans hnm⟩

theorem degLe_step (acc : List (F[X] × F[X])) (o : Op F)
    (h : ∀ p ∈ acc, DegLe p (2 ^ acc.length)) : DegLe (stepFrac acc o) (2 ^ (acc.length + 1)) := by
  have hget : ∀ i : ℕ, DegLe (acc.getD i (0, 1)) (2 ^ acc.length) := by
    intro i
    by_cases hi : i < acc.length
    · have : acc.getD i (0, 1) ∈ acc := by
        rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]
        exact List.getElem_mem hi
      exact h _ this
    · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
      simp [DegLe]
  have hpow : 2 ^ acc.length ≤ 2 ^ (acc.length + 1) :=
    pow_le_pow_right₀ (by norm_num) (by omega)
  have hone : 1 ≤ 2 ^ (acc.length + 1) := Nat.one_le_two_pow
  have h2 : 2 ^ (acc.length + 1) = 2 ^ acc.length + 2 ^ acc.length := by ring
  have prod : ∀ a b c e : F[X], a.natDegree ≤ 2 ^ acc.length → b.natDegree ≤ 2 ^ acc.length →
      c.natDegree ≤ 2 ^ acc.length → e.natDegree ≤ 2 ^ acc.length →
      (a * b + c * e).natDegree ≤ 2 ^ (acc.length + 1) := by
    intro a b c e ha hb hc he
    refine (natDegree_add_le _ _).trans (max_le ?_ ?_)
    · exact natDegree_mul_le.trans (by omega)
    · exact natDegree_mul_le.trans (by omega)
  have prod' : ∀ a b : F[X], a.natDegree ≤ 2 ^ acc.length → b.natDegree ≤ 2 ^ acc.length →
      (a * b).natDegree ≤ 2 ^ (acc.length + 1) := by
    intro a b ha hb
    exact natDegree_mul_le.trans (by omega)
  have hi := hget
  cases o with
  | const c => simp [stepFrac, DegLe]
  | var => exact ⟨by simpa [stepFrac] using (natDegree_X_le (R := F)).trans hone, by simp [stepFrac]⟩
  | add i j =>
    refine ⟨prod _ _ _ _ (hget i).1 (hget j).2 (hget j).1 (hget i).2, prod' _ _ (hget i).2 (hget j).2⟩
  | sub i j =>
    refine ⟨?_, prod' _ _ (hget i).2 (hget j).2⟩
    simp only [stepFrac]
    refine (natDegree_sub_le _ _).trans (max_le ?_ ?_)
    · exact natDegree_mul_le.trans (by have := (hget i).1; have := (hget j).2; omega)
    · exact natDegree_mul_le.trans (by have := (hget j).1; have := (hget i).2; omega)
  | mul i j => exact ⟨prod' _ _ (hget i).1 (hget j).1, prod' _ _ (hget i).2 (hget j).2⟩
  | div i j => exact ⟨prod' _ _ (hget i).1 (hget j).2, prod' _ _ (hget i).2 (hget j).1⟩

theorem degLe_run : ∀ (prog : List (Op F)) (acc : List (F[X] × F[X])),
    (∀ p ∈ acc, DegLe p (2 ^ acc.length)) →
    ∀ p ∈ runFrac prog acc, DegLe p (2 ^ (acc.length + prog.length))
  | [], acc, h, p, hp => by simpa [runFrac] using h p hp
  | o :: rest, acc, h, p, hp => by
    have hstep := degLe_step acc o h
    have hpow : 2 ^ acc.length ≤ 2 ^ (acc.length + 1) :=
      pow_le_pow_right₀ (by norm_num) (by omega)
    have key : ∀ q ∈ acc ++ [stepFrac acc o], DegLe q (2 ^ (acc ++ [stepFrac acc o]).length) := by
      intro q hq
      rw [List.length_append, List.length_singleton]
      rcases List.mem_append.mp hq with hq | hq
      · exact (h q hq).mono hpow
      · have hq' : q = stepFrac acc o := by simpa using hq
        subst hq'
        exact hstep
    have := degLe_run rest _ key p (by simpa [runFrac] using hp)
    simpa [List.length_append, List.length_cons, Nat.add_assoc, Nat.add_comm 1] using this

/-- **Degree lemma.** Every formal pair of a program of length `L` has numerator and denominator of
`natDegree ≤ 2 ^ L`; out-of-range indices read `(0, 1)`. -/
theorem degLe_getD (prog : List (Op F)) (i : ℕ) :
    DegLe ((evalFrac prog).getD i (0, 1)) (2 ^ prog.length) := by
  by_cases hi : i < (evalFrac prog).length
  · have := degLe_run prog [] (by simp)
    have hm : (evalFrac prog).getD i (0, 1) ∈ evalFrac prog := by
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]
      exact List.getElem_mem hi
    simpa [evalFrac] using this _ hm
  · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
    simp [DegLe]

end Semantics

open WeierstrassCurve WeierstrassCurve.Affine CurveX

variable {F : Type*} [Field F] [DecidableEq F]

/-- **Main theorem (algebraic SLP barrier with division, x-only).** `W` short Weierstrass over a
field `F` with `2 ≠ 0`, `P` of order `r`, `2 N < r`. Let `prog` be a straight-line program over `F`
with `+, -, *, /` and constants, single input `u`. If for every `1 ≤ k ≤ N` all divisions of `prog`
have a nonzero divisor at `u = x (kP)` and the `i`-th output equals `k` there, then
`N ≤ 3 * 2 ^ prog.length + 2`. No bit-complexity claim; only counts field operations. -/
theorem length_bound_rational_slp {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (prog : List (Op F)) (i : ℕ)
    (hdef : ∀ k : ℕ, 1 ≤ k → k ≤ N → Defined prog (xCoord (k • P)))
    (hprog : ∀ k : ℕ, 1 ≤ k → k ≤ N → (evalAt prog (xCoord (k • P))).getD i 0 = (k : F)) :
    N ≤ 3 * 2 ^ prog.length + 2 := by
  have hdeg := degLe_getD prog i
  refine degree_bound_rational_short_weierstrass h1 h2 h3 h2' P r hr N hN
    ((evalFrac prog).getD i (0, 1)).1 ((evalFrac prog).getD i (0, 1)).2 (2 ^ prog.length)
    hdeg.1 hdeg.2 ?_ ?_
  · intro k hk hk'
    exact (eval_agreement prog _ (hdef k hk hk') i).1
  · intro k hk hk'
    obtain ⟨hne, hv⟩ := eval_agreement prog _ (hdef k hk hk') i
    rw [hprog k hk hk'] at hv
    rw [hv]; field_simp

/-- Order form for odd `r`: outputting `k` at `x (kP)` for `1 ≤ k ≤ (r-1)/2` with all divisions
defined needs `r ≤ 6 * 2 ^ length + 5`. -/
theorem length_bound_rational_slp_order {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (hodd : r % 2 = 1) (prog : List (Op F)) (i : ℕ)
    (hdef : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 → Defined prog (xCoord (k • P)))
    (hprog : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 →
      (evalAt prog (xCoord (k • P))).getD i 0 = (k : F)) :
    r ≤ 6 * 2 ^ prog.length + 5 := by
  have := length_bound_rational_slp h1 h2 h3 h2' P r hr ((r - 1) / 2) (by omega) prog i hdef hprog
  omega

end SLP

end RationalSLP

end MathResearch.ECDLP
