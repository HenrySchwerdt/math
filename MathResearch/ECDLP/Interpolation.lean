module

public import Mathlib.Algebra.Polynomial.Roots
public import Mathlib.Algebra.Polynomial.Degree.Lemmas
public import Mathlib.Tactic

/-!
# ECDLP: degree bound for x-only polynomials interpolating `k ↦ k²`

Ledger: research/ecdlp, task ECDLP-19 (TSK-fe72aad1-aa67-4d7d-a0c9-3c8bc14a05ef),
RUN-e5203fb5-9b4c-49e2-86e1-ea88971103fb. Formalizes the polynomial route to HYP-eda6732a.

The elliptic curve enters ONLY through hypotheses `hS`, `hT` below: for a sequence `xs`
(intended: `xs k = x(kP)`), the classical x-addition relations
`(xs (k+1) + xs (k-1)) (xs k - x₀)² = 2((x₀ xs k + a)(xs k + x₀) + 2b)` and
`xs (k+1) xs (k-1) (xs k - x₀)² = (x₀ xs k - a)² - 4b (xs k + x₀)`.
That these hold for `xs k = x(kP)` on `y² = x³ + a x + b` is NOT proved here (checked
numerically only; see the RUN record). Nothing here says anything about bit complexity.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace Interp

variable {K : Type*} [Field K]

/-- Scaled power sums `q i = D^i (z₁^i + z₂^i)` where `z₁ + z₂ = A/D`, `z₁ z₂ = B/D`
(Newton recursion, denominators cleared). -/
noncomputable def q (A B D : K[X]) : ℕ → K[X]
  | 0 => 2
  | 1 => A
  | (i + 2) => A * q A B D (i + 1) - B * D * q A B D i

theorem natDegree_q_le (A B D : K[X]) (hA : A.natDegree ≤ 2) (hBD : (B * D).natDegree ≤ 4) :
    ∀ i, (q A B D i).natDegree ≤ 2 * i
  | 0 => by simp [q]
  | 1 => by simpa [q] using hA
  | (i + 2) => by
    have h1 := natDegree_q_le A B D hA hBD (i + 1)
    have h0 := natDegree_q_le A B D hA hBD i
    simp only [q]
    refine (natDegree_sub_le _ _).trans (max_le ?_ ?_)
    · exact (natDegree_mul_le).trans (by omega)
    · exact (natDegree_mul_le).trans (by omega)

/-- The cleared polynomial `D^d (g(z₁) + g(z₂) - 2 g(u) - 2)` as a polynomial in `u`. -/
noncomputable def N (A B D g : K[X]) (d : ℕ) : K[X] :=
  (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * q A B D i)) -
    D ^ d * (2 * g + 2)

theorem eval_q (A B D : K[X]) (u z₁ z₂ : K)
    (hS : (z₁ + z₂) * D.eval u = A.eval u) (hT : z₁ * z₂ * D.eval u = B.eval u) :
    ∀ i, (q A B D i).eval u = D.eval u ^ i * (z₁ ^ i + z₂ ^ i)
  | 0 => by simp [q]; ring
  | 1 => by simp [q, ← hS]; ring
  | (i + 2) => by
    have h1 := eval_q A B D u z₁ z₂ hS hT (i + 1)
    have h0 := eval_q A B D u z₁ z₂ hS hT i
    simp only [q, eval_sub, eval_mul, h1, h0, ← hS, ← hT]
    ring

theorem eval_N (A B D g : K[X]) (d : ℕ) (hg : g.natDegree ≤ d) (u z₁ z₂ : K)
    (hS : (z₁ + z₂) * D.eval u = A.eval u) (hT : z₁ * z₂ * D.eval u = B.eval u) :
    (N A B D g d).eval u =
      D.eval u ^ d * (g.eval z₁ + g.eval z₂ - 2 * g.eval u - 2) := by
  have hz : ∀ z : K, g.eval z = ∑ i ∈ Finset.range (d + 1), g.coeff i * z ^ i := fun z => by
    rw [eval_eq_sum_range' (Nat.lt_succ_of_le hg)]
  simp only [N, eval_sub, eval_finsetSum, eval_mul, eval_C, eval_pow, eval_add, eval_ofNat]
  have : ∀ i ∈ Finset.range (d + 1), g.coeff i * (D.eval u ^ (d - i) * (q A B D i).eval u) =
      D.eval u ^ d * (g.coeff i * z₁ ^ i + g.coeff i * z₂ ^ i) := by
    intro i hi
    have hi' : i ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
    rw [eval_q A B D u z₁ z₂ hS hT i]
    have : D.eval u ^ d = D.eval u ^ (d - i) * D.eval u ^ i := by
      rw [← pow_add]; congr 1; omega
    rw [this]; ring
  rw [Finset.sum_congr rfl this, ← Finset.mul_sum, Finset.sum_add_distrib, ← hz, ← hz]
  ring

theorem natDegree_N_le (A B D g : K[X]) (d : ℕ) (hA : A.natDegree ≤ 2)
    (hBD : (B * D).natDegree ≤ 4) (hD : D.natDegree ≤ 2) :
    (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * q A B D i)).natDegree ≤ 2 * d := by
  refine natDegree_sum_le_of_forall_le _ _ (fun i hi => ?_)
  have hi' : i ≤ d := Nat.lt_succ_iff.mp (Finset.mem_range.mp hi)
  refine (natDegree_C_mul_le _ _).trans ((natDegree_mul_le).trans ?_)
  have h1 : (D ^ (d - i)).natDegree ≤ 2 * (d - i) :=
    natDegree_pow_le.trans (by nlinarith)
  have h2 := natDegree_q_le A B D hA hBD i
  omega

/-- Abstract counting lemma: if `N` is the cleared polynomial for `g` of degree `d ≥ 1`
and vanishes on `m - 2` distinct points, then `m - 2 ≤ 3 d`. -/
theorem counting (A B D g : K[X]) (hA : A.natDegree ≤ 2)
    (hBD : (B * D).natDegree ≤ 4) (hD : D.Monic) (hD2 : D.natDegree = 2)
    (h2 : (2 : K) ≠ 0) (hd : 1 ≤ g.natDegree) (Z : Finset K)
    (hZ : ∀ z ∈ Z, (N A B D g g.natDegree).eval z = 0) :
    Z.card ≤ 3 * g.natDegree := by
  set d := g.natDegree with hd_def
  have hfirst := natDegree_N_le A B D g d hA hBD hD2.le
  have hDp : (D ^ d).natDegree = 2 * d := by rw [hD.natDegree_pow, hD2]; ring
  have hDm : (D ^ d).Monic := hD.pow d
  have hC : (2 * g + 2 : K[X]) = C 2 * g + C 2 := by rw [show (C (2 : K)) = 2 from map_ofNat C 2]
  have hc : (C (2 : K) * g).natDegree = d := natDegree_C_mul h2
  have hgl : (2 * g + 2 : K[X]).natDegree = d := by
    rw [hC, natDegree_add_eq_left_of_natDegree_lt]
    · exact hc
    · rw [hc, natDegree_C]; omega
  have hne : (2 * g + 2 : K[X]) ≠ 0 := by
    intro h; rw [h] at hgl; simp at hgl; omega
  have hsec : (D ^ d * (2 * g + 2)).natDegree = 3 * d := by
    rw [natDegree_mul (pow_ne_zero _ hD.ne_zero) hne, hDp, hgl]; ring
  have hlt : (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * q A B D i)).natDegree
      < (D ^ d * (2 * g + 2)).natDegree := by rw [hsec]; omega
  have hN : (N A B D g d).natDegree = 3 * d := by
    unfold N
    rw [natDegree_sub_eq_right_of_natDegree_lt hlt, hsec]
  have hN0 : N A B D g d ≠ 0 := by
    intro h; rw [h] at hN; simp at hN; omega
  have := card_le_degree_of_subset_roots (p := N A B D g d) (Z := Z) (by
    intro z hz
    exact (mem_roots hN0).2 (hZ z hz))
  rw [hN] at this
  exact this

/-- Numerator of `x(Q+P) + x(Q-P)` (over the denominator `(u - x₀)²`). -/
noncomputable def numS (a b x₀ : K) : K[X] :=
  C 2 * ((C x₀ * X + C a) * (X + C x₀) + C (2 * b))

/-- Numerator of `x(Q+P) * x(Q-P)` (over the denominator `(u - x₀)²`). -/
noncomputable def numT (a b x₀ : K) : K[X] :=
  (C x₀ * X - C a) ^ 2 - C (4 * b) * (X + C x₀)

/-- The common denominator `(u - x₀)²`. -/
noncomputable def den (x₀ : K) : K[X] := (X - C x₀) ^ 2

theorem natDegree_numS_le (a b x₀ : K) : (numS a b x₀).natDegree ≤ 2 := by
  unfold numS; compute_degree

theorem natDegree_numT_den_le (a b x₀ : K) : (numT a b x₀ * den x₀).natDegree ≤ 4 := by
  unfold numT den; compute_degree

theorem den_monic (x₀ : K) : (den x₀).Monic := by
  unfold den; exact (monic_X_sub_C x₀).pow 2

theorem den_natDegree (x₀ : K) : (den x₀).natDegree = 2 := by
  unfold den; rw [natDegree_pow, natDegree_X_sub_C]

/-- **Degree bound for x-only interpolation of `k ↦ k²` (hypothesis form).**

`xs k` is intended to be `x(kP)` on `y² = x³ + a x + b` with `x₀ = x(P)`, `m = (r-1)/2`
for `P` of odd order `r`. HYPOTHESES (not proved here): `hinj` (x-coordinates of `kP`,
`1 ≤ k ≤ m`, are distinct; `xs 1 = x₀` is not even needed) and `hS`, `hT` (classical x-addition relations in
denominator-cleared form, for `2 ≤ k < m`). If a polynomial `g` satisfies
`g (xs k) = k²` for `1 ≤ k ≤ m`, then `m ≤ 3 deg g + 2`. Requires `2 ≠ 0` and `3 ≠ 0` in `K`. -/
theorem degree_bound_of_x_relations (a b x₀ : K) (h2 : (2 : K) ≠ 0) (h3 : (3 : K) ≠ 0)
    (g : K[X]) (m : ℕ) (xs : ℕ → K)
    (hinj : Set.InjOn xs (Set.Icc 1 m))
    (hS : ∀ k, 2 ≤ k → k + 1 ≤ m →
      (xs (k + 1) + xs (k - 1)) * (xs k - x₀) ^ 2 = 2 * ((x₀ * xs k + a) * (xs k + x₀) + 2 * b))
    (hT : ∀ k, 2 ≤ k → k + 1 ≤ m →
      xs (k + 1) * xs (k - 1) * (xs k - x₀) ^ 2 = (x₀ * xs k - a) ^ 2 - 4 * b * (xs k + x₀))
    (hg : ∀ k, 1 ≤ k → k ≤ m → g.eval (xs k) = (k : K) ^ 2) :
    m ≤ 3 * g.natDegree + 2 := by
  by_cases hm : m ≤ 2
  · omega
  replace hm := not_le.mp hm
  classical
  rcases Nat.eq_zero_or_pos g.natDegree with hd | hd
  · exfalso
    rw [eq_C_of_natDegree_eq_zero hd] at hg
    have e1 := hg 1 le_rfl (by omega)
    have e2 := hg 2 (by omega) (by omega)
    simp only [eval_C] at e1 e2
    apply h3
    have e : ((1 : ℕ) : K) ^ 2 = ((2 : ℕ) : K) ^ 2 := e1.symm.trans e2
    push_cast at e
    linear_combination (-1 : K) * e
  · have key := counting (numS a b x₀) (numT a b x₀) (den x₀) g (natDegree_numS_le a b x₀)
      (natDegree_numT_den_le a b x₀) (den_monic x₀) (den_natDegree x₀) h2 hd
      ((Finset.Icc 2 (m - 1)).image xs) (by
        intro z hz
        obtain ⟨k, hk, rfl⟩ := Finset.mem_image.mp hz
        obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hk
        obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
        rw [eval_N _ _ _ g g.natDegree le_rfl (xs (j + 1)) (xs (j + 1 + 1)) (xs j)]
        · have e1 := hg (j + 1 + 1) (by omega) (by omega)
          have e2 := hg j (by omega) (by omega)
          have e3 := hg (j + 1) (by omega) (by omega)
          rw [e1, e2, e3]
          push_cast
          ring
        · simpa [numS, den] using hS (j + 1) hk1 (by omega)
        · simpa [numT, den] using hT (j + 1) hk1 (by omega))
    rw [Finset.card_image_of_injOn (hinj.mono (by
      intro k hk; simp only [Finset.coe_Icc, Set.mem_Icc] at hk ⊢; omega))] at key
    simp only [Nat.card_Icc] at key
    omega

/-- **Corollary in terms of the group order.** For `r` odd, with `m = (r-1)/2`, the same
hypotheses give `r ≤ 6 deg g + 5`, i.e. `deg g ≥ (r - 5) / 6`. -/
theorem degree_bound_of_x_relations_order (a b x₀ : K) (h2 : (2 : K) ≠ 0) (h3 : (3 : K) ≠ 0)
    (g : K[X]) (r : ℕ) (hr : r % 2 = 1) (xs : ℕ → K)
    (hinj : Set.InjOn xs (Set.Icc 1 ((r - 1) / 2)))
    (hS : ∀ k, 2 ≤ k → k + 1 ≤ (r - 1) / 2 →
      (xs (k + 1) + xs (k - 1)) * (xs k - x₀) ^ 2 = 2 * ((x₀ * xs k + a) * (xs k + x₀) + 2 * b))
    (hT : ∀ k, 2 ≤ k → k + 1 ≤ (r - 1) / 2 →
      xs (k + 1) * xs (k - 1) * (xs k - x₀) ^ 2 = (x₀ * xs k - a) ^ 2 - 4 * b * (xs k + x₀))
    (hg : ∀ k, 1 ≤ k → k ≤ (r - 1) / 2 → g.eval (xs k) = (k : K) ^ 2) :
    r ≤ 6 * g.natDegree + 5 := by
  have := degree_bound_of_x_relations a b x₀ h2 h3 g ((r - 1) / 2) xs hinj hS hT hg
  omega

end Interp

end MathResearch.ECDLP
