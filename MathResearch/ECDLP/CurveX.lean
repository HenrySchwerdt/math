module

public import MathResearch.ECDLP.Interpolation
public import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Formula
public import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
public import Mathlib.GroupTheory.OrderOfElement

/-!
# ECDLP: x-addition identities on a short Weierstrass curve (unconditional Theorem B)

Ledger: research/ecdlp, task ECDLP-20 (TSK-f824b713-5e45-42f0-87b0-d4a8614d3a3a),
RUN-55019cbd-64f8-4e22-ad27-61316ef59d20; discharges the hypotheses of
`MathResearch.ECDLP.Interp.degree_bound_of_x_relations_order` for HYP-eda6732a.
Short Weierstrass means `a₁ = a₂ = a₃ = 0`, `a = a₄`, `b = a₆`. Nothing here concerns bit complexity.
-/

@[expose] public section

namespace MathResearch.ECDLP

open WeierstrassCurve WeierstrassCurve.Affine

namespace CurveX

variable {F : Type*} [Field F]

/-- Algebraic core of X1/X2 (HYP-eda6732a): for `v² = u³ + a u + b`, `y₀² = x₀³ + a x₀ + b`,
`u ≠ x₀`, the quantities `s± = (v ∓ y₀)²/(u-x₀)² - (u+x₀)` satisfy the cleared sum and product
identities. -/
theorem sum_prod_identity (a b u v x₀ y₀ : F) (hv : v ^ 2 = u ^ 3 + a * u + b)
    (hy : y₀ ^ 2 = x₀ ^ 3 + a * x₀ + b) (hne : u ≠ x₀) :
    (((v - y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀)) + ((v + y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀))) *
        (u - x₀) ^ 2 = 2 * ((x₀ * u + a) * (u + x₀) + 2 * b) ∧
    ((v - y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀)) * ((v + y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀)) *
        (u - x₀) ^ 2 = (x₀ * u - a) ^ 2 - 4 * b * (u + x₀) := by
  have hd : u - x₀ ≠ 0 := sub_ne_zero.mpr hne
  constructor
  · field_simp
    linear_combination 2 * hv + 2 * hy
  · have key : (v ^ 2 - y₀ ^ 2) ^ 2 - (u + x₀) * (u - x₀) ^ 2 * (2 * v ^ 2 + 2 * y₀ ^ 2)
        + (u + x₀) ^ 2 * (u - x₀) ^ 4 = (u - x₀) ^ 2 * ((x₀ * u - a) ^ 2 - 4 * b * (u + x₀)) := by
      rw [hv, hy]; ring
    field_simp
    linear_combination key


open Affine.Point in
/-- The x-coordinate of an affine point (`0` at infinity, by convention). Only used for points
known to be affine. -/
noncomputable def xCoord {W : Affine F} : W.Point → F
  | .zero => 0
  | .some x _ _ => x

@[simp] theorem xCoord_some {W : Affine F} {x y : F} (h : W.Nonsingular x y) :
    xCoord (Point.some x y h) = x := rfl

theorem xCoord_of_xRep {W : Affine F} {P : W.Point} {x : F} (h : P.xRep = ![x, 1]) :
    xCoord P = x := by
  cases P with
  | zero =>
    have h' : (0 : W.Point).xRep = ![x, 1] := h
    simp at h'
  | some x' y' h' => simpa using h

variable [DecidableEq F]

/-- X3 (HYP-eda6732a): for affine `Q = (u,v)`, `P = (x₀,y₀)` on a short Weierstrass curve with
`u ≠ x₀`, `x(Q+P) = (v-y₀)²/(u-x₀)² - (u+x₀)` and `x(Q-P) = (v+y₀)²/(u-x₀)² - (u+x₀)`. -/
theorem xCoord_add_sub {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {u v x₀ y₀ : F} (hQ : W.Nonsingular u v) (hP : W.Nonsingular x₀ y₀) (hne : u ≠ x₀) :
    xCoord (Point.some u v hQ + Point.some x₀ y₀ hP) =
        (v - y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀) ∧
    xCoord (Point.some u v hQ - Point.some x₀ y₀ hP) =
        (v + y₀) ^ 2 / (u - x₀) ^ 2 - (u + x₀) := by
  have hd : u - x₀ ≠ 0 := sub_ne_zero.mpr hne
  constructor
  · refine xCoord_of_xRep ?_
    rw [Point.xRep_add_of_X_ne hQ hP hne]
    simp only [h1, h2, zero_mul, add_zero, zero_add]
    congr 2
    field_simp
  · refine xCoord_of_xRep ?_
    rw [Point.xRep_sub_of_X_ne hQ hP hne]
    simp only [h1, h2, h3, zero_mul, add_zero, zero_add]
    congr 2
    field_simp

omit [DecidableEq F] in
/-- Equations of a short Weierstrass curve. -/
theorem short_equation {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {x y : F} (h : W.Equation x y) : y ^ 2 = x ^ 3 + W.a₄ * x + W.a₆ := by
  rw [equation_iff] at h
  simpa [h1, h2, h3] using h

/-- X1 and X2 for `W.Point` (HYP-eda6732a): sum and product identities of
`x(Q+P)`, `x(Q-P)` for affine `Q ≠ ±P` on a short Weierstrass curve. -/
theorem xCoord_relations {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {u v x₀ y₀ : F} (hQ : W.Nonsingular u v) (hP : W.Nonsingular x₀ y₀) (hne : u ≠ x₀) :
    (xCoord (Point.some u v hQ + Point.some x₀ y₀ hP) +
        xCoord (Point.some u v hQ - Point.some x₀ y₀ hP)) * (u - x₀) ^ 2 =
      2 * ((x₀ * u + W.a₄) * (u + x₀) + 2 * W.a₆) ∧
    xCoord (Point.some u v hQ + Point.some x₀ y₀ hP) *
        xCoord (Point.some u v hQ - Point.some x₀ y₀ hP) * (u - x₀) ^ 2 =
      (x₀ * u - W.a₄) ^ 2 - 4 * W.a₆ * (u + x₀) := by
  obtain ⟨e1, e2⟩ := xCoord_add_sub h1 h2 h3 hQ hP hne
  rw [e1, e2]
  exact sum_prod_identity W.a₄ W.a₆ u v x₀ y₀ (short_equation h1 h2 h3 hQ.1)
    (short_equation h1 h2 h3 hP.1) hne


omit [Field F] [DecidableEq F] in
/-- Multiples `kP`, `1 ≤ k < r`, of a point of order `r` are nonzero (HYP-eda6732a). -/
theorem nsmul_ne_zero_of_lt {G : Type*} [AddCommGroup G] {P : G} {r k : ℕ}
    (hr : addOrderOf P = r) (hk : 1 ≤ k) (hkr : k < r) : k • P ≠ 0 := by
  intro h
  have := Nat.le_of_dvd (by omega) (hr ▸ (addOrderOf_dvd_iff_nsmul_eq_zero.mpr h))
  omega

omit [DecidableEq F] in
/-- Same x-coordinate of two affine points forces `A = ±B` (HYP-eda6732a). -/
theorem eq_or_neg_of_xCoord_eq {W : Affine F} {A B : W.Point} (hA : A ≠ 0) (hB : B ≠ 0)
    (h : xCoord A = xCoord B) : A = B ∨ A = -B := by
  cases A with
  | zero => exact absurd rfl hA
  | some x y hxy =>
    cases B with
    | zero => exact absurd rfl hB
    | some x' y' hxy' => exact Point.X_eq_iff.mp h

omit [Field F] [DecidableEq F] in
/-- Injectivity core (X4, group part; HYP-eda6732a): if `P` has order `r`, `1 ≤ j, k` and
`j + k < r`, then `jP = ±kP` forces `j = k`. -/
theorem eq_of_smul_eq_or_neg {G : Type*} [AddCommGroup G] {P : G} {r j k : ℕ}
    (hr : addOrderOf P = r) (hj : 1 ≤ j) (hk : 1 ≤ k) (hjk : j + k < r)
    (h : j • P = k • P ∨ j • P = -(k • P)) : j = k := by
  rcases h with h | h
  · have h0 : ((j : ℤ) - k) • P = 0 := by
      rw [sub_zsmul, natCast_zsmul, natCast_zsmul, h]
      abel
    have hd : (r : ℤ) ∣ (j : ℤ) - k := by
      rw [← hr]; exact addOrderOf_dvd_iff_zsmul_eq_zero.mpr h0
    have : (j : ℤ) - k = 0 := Int.eq_zero_of_abs_lt_dvd hd (by rw [abs_lt]; constructor <;> omega)
    omega
  · exfalso
    have h0 : (j + k) • P = 0 := by
      rw [add_nsmul, h, neg_add_cancel]
    have := Nat.le_of_dvd (by omega) (hr ▸ (addOrderOf_dvd_iff_nsmul_eq_zero.mpr h0))
    omega

/-- Injectivity of `k ↦ x(kP)` (X4; HYP-eda6732a): for `P` of order `r` and `j, k` in
`[1, m]` with `2m < r`, `x(jP) = x(kP)` implies `j = k`. -/
theorem xCoord_smul_injOn {W : Affine F} {P : W.Point} {r m : ℕ} (hr : addOrderOf P = r)
    (hm : 2 * m < r) : Set.InjOn (fun k : ℕ => xCoord (k • P)) (Set.Icc 1 m) := by
  intro j hj k hk h
  simp only [Set.mem_Icc] at hj hk
  have hj0 := nsmul_ne_zero_of_lt hr hj.1 (by omega)
  have hk0 := nsmul_ne_zero_of_lt hr hk.1 (by omega)
  rcases eq_or_neg_of_xCoord_eq hj0 hk0 h with h' | h'
  · exact eq_of_smul_eq_or_neg hr hj.1 hk.1 (by omega) (Or.inl h')
  · exact eq_of_smul_eq_or_neg hr hj.1 hk.1 (by omega) (Or.inr h')


/-- X4 + X3 combined (HYP-eda6732a): the denominator-cleared sum and product relations for
`xs k = x(kP)`, `2 ≤ k`, `k + 1 ≤ m`, `2m < r`, `P` of order `r`, `x₀ = x(P)`. -/
theorem smul_relations {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {P : W.Point} {r m : ℕ} (hr : addOrderOf P = r) (hm : 2 * m < r) {k : ℕ}
    (hk : 2 ≤ k) (hkm : k + 1 ≤ m) :
    (xCoord ((k + 1) • P) + xCoord ((k - 1) • P)) * (xCoord (k • P) - xCoord P) ^ 2 =
      2 * ((xCoord P * xCoord (k • P) + W.a₄) * (xCoord (k • P) + xCoord P) + 2 * W.a₆) ∧
    xCoord ((k + 1) • P) * xCoord ((k - 1) • P) * (xCoord (k • P) - xCoord P) ^ 2 =
      (xCoord P * xCoord (k • P) - W.a₄) ^ 2 - 4 * W.a₆ * (xCoord (k • P) + xCoord P) := by
  have hP0 : P ≠ 0 := by
    simpa using nsmul_ne_zero_of_lt hr (k := 1) le_rfl (by omega)
  have hQ0 := nsmul_ne_zero_of_lt hr (P := P) (k := k) (by omega) (by omega)
  have hinj := xCoord_smul_injOn (W := W) hr hm
  have hx : xCoord (k • P) ≠ xCoord P := by
    intro h
    have := hinj (x₁ := 1) (x₂ := k) (by simp only [Set.mem_Icc]; omega)
      (by simp only [Set.mem_Icc]; omega) (by simpa using h.symm)
    omega
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


open Polynomial in
/-- **Theorem B, unconditional form (HYP-eda6732a).** Let `W` be a short Weierstrass curve
(`a₁ = a₂ = a₃ = 0`) over a field `F` with `2 ≠ 0`, `3 ≠ 0`, and `P : W.Point` of odd order `r`.
If a polynomial `g` satisfies `g(x(kP)) = k²` in `F` for all `1 ≤ k ≤ (r-1)/2`, then
`r ≤ 6 deg g + 5`. This is a statement about polynomial degree only, not about bit complexity,
and says nothing on whether such `g` exists. -/
theorem degree_bound_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (h3' : (3 : F) ≠ 0) (P : W.Point) (r : ℕ)
    (hr : addOrderOf P = r) (hodd : r % 2 = 1) (g : F[X])
    (hg : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 → g.eval (xCoord (k • P)) = (k : F) ^ 2) :
    r ≤ 6 * g.natDegree + 5 := by
  have hm : 2 * ((r - 1) / 2) < r := by omega
  refine Interp.degree_bound_of_x_relations_order W.a₄ W.a₆ (xCoord P) h2' h3' g r hodd
    (fun k => xCoord (k • P)) (xCoord_smul_injOn hr hm) ?_ ?_ hg
  · intro k hk hk'
    exact (smul_relations h1 h2 h3 hr hm hk hk').1
  · intro k hk hk'
    exact (smul_relations h1 h2 h3 hr hm hk hk').2

end CurveX




end MathResearch.ECDLP
