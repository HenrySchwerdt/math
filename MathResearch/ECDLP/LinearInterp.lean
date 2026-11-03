module

public import MathResearch.ECDLP.CurveX

/-!
# ECDLP: degree bound for x-only polynomials interpolating `k ↦ k` (the discrete log itself)

Ledger: research/ecdlp, task ECDLP-25 (TSK-78a350cd-9590-487e-ac4f-b018215eb7c2),
RUN-9974dc45-0029-4615-bd81-9c9fbbda94f4. Same polynomial machinery as
`MathResearch.ECDLP.Interp` (k² case): the second difference of `k` is `0`, so the cleared polynomial
is `N₀ = N + 2 D^d`, i.e. `Σ gᵢ Dᵈ⁻ⁱ qᵢ - 2 Dᵈ g`. Its degree is exactly `3 d` for `d = deg g ≥ 1`
because the first sum has degree `≤ 2 d` and `2 Dᵈ g` has degree `3 d` (the constant `2` of the k²
case is irrelevant). Nothing here concerns bit complexity or existence of such `g`.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace LinearInterp

variable {K : Type*} [Field K]

/-- Cleared polynomial `D^d (g(z₁) + g(z₂) - 2 g(u))` for the linear case. -/
noncomputable def N0 (A B D g : K[X]) (d : ℕ) : K[X] :=
  (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * Interp.q A B D i)) -
    D ^ d * (2 * g)

theorem eval_N0 (A B D g : K[X]) (d : ℕ) (hg : g.natDegree ≤ d) (u z₁ z₂ : K)
    (hS : (z₁ + z₂) * D.eval u = A.eval u) (hT : z₁ * z₂ * D.eval u = B.eval u) :
    (N0 A B D g d).eval u = D.eval u ^ d * (g.eval z₁ + g.eval z₂ - 2 * g.eval u) := by
  have h := Interp.eval_N A B D g d hg u z₁ z₂ hS hT
  have e : N0 A B D g d = Interp.N A B D g d + D ^ d * 2 := by
    unfold N0 Interp.N; ring
  rw [e, eval_add, h, eval_mul, eval_pow]
  simp only [eval_ofNat]
  ring

/-- Counting lemma: for `g` of degree `d ≥ 1`, `N0` is nonzero of degree exactly `3 d`, so a set
of roots has at most `3 d` elements. -/
theorem counting0 (A B D g : K[X]) (hA : A.natDegree ≤ 2)
    (hBD : (B * D).natDegree ≤ 4) (hD : D.Monic) (hD2 : D.natDegree = 2)
    (h2 : (2 : K) ≠ 0) (hd : 1 ≤ g.natDegree) (Z : Finset K)
    (hZ : ∀ z ∈ Z, (N0 A B D g g.natDegree).eval z = 0) :
    Z.card ≤ 3 * g.natDegree := by
  set d := g.natDegree with hd_def
  have hfirst := Interp.natDegree_N_le A B D g d hA hBD hD2.le
  have hDp : (D ^ d).natDegree = 2 * d := by rw [hD.natDegree_pow, hD2]; ring
  have hc : (2 * g : K[X]).natDegree = d := by
    rw [show (2 : K[X]) = C 2 from (map_ofNat C 2).symm]
    exact natDegree_C_mul h2
  have hne : (2 * g : K[X]) ≠ 0 := by
    intro h; rw [h] at hc; simp at hc; omega
  have hsec : (D ^ d * (2 * g)).natDegree = 3 * d := by
    rw [natDegree_mul (pow_ne_zero _ hD.ne_zero) hne, hDp, hc]; ring
  have hlt : (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * Interp.q A B D i)).natDegree
      < (D ^ d * (2 * g)).natDegree := by rw [hsec]; omega
  have hN : (N0 A B D g d).natDegree = 3 * d := by
    unfold N0
    rw [natDegree_sub_eq_right_of_natDegree_lt hlt, hsec]
  have hN0 : N0 A B D g d ≠ 0 := by
    intro h; rw [h] at hN; simp at hN; omega
  have := card_le_degree_of_subset_roots (p := N0 A B D g d) (Z := Z) (by
    intro z hz
    exact (mem_roots hN0).2 (hZ z hz))
  rw [hN] at this
  exact this

/-- **Degree bound for x-only interpolation of `k ↦ k` (hypothesis form).** Same hypotheses as
`Interp.degree_bound_of_x_relations` but `g (xs k) = k` (in `K`); conclusion `m ≤ 3 deg g + 2`.
Only `2 ≠ 0` is needed. -/
theorem degree_bound_of_x_relations_linear (a b x₀ : K) (h2 : (2 : K) ≠ 0)
    (g : K[X]) (m : ℕ) (xs : ℕ → K)
    (hinj : Set.InjOn xs (Set.Icc 1 m))
    (hS : ∀ k, 2 ≤ k → k + 1 ≤ m →
      (xs (k + 1) + xs (k - 1)) * (xs k - x₀) ^ 2 = 2 * ((x₀ * xs k + a) * (xs k + x₀) + 2 * b))
    (hT : ∀ k, 2 ≤ k → k + 1 ≤ m →
      xs (k + 1) * xs (k - 1) * (xs k - x₀) ^ 2 = (x₀ * xs k - a) ^ 2 - 4 * b * (xs k + x₀))
    (hg : ∀ k, 1 ≤ k → k ≤ m → g.eval (xs k) = (k : K)) :
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
    have e : ((1 : ℕ) : K) = ((2 : ℕ) : K) := e1.symm.trans e2
    push_cast at e
    exact one_ne_zero (by linear_combination (-1 : K) * e)
  · have key := counting0 (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) g
      (Interp.natDegree_numS_le a b x₀) (Interp.natDegree_numT_den_le a b x₀)
      (Interp.den_monic x₀) (Interp.den_natDegree x₀) h2 hd
      ((Finset.Icc 2 (m - 1)).image xs) (by
        intro z hz
        obtain ⟨k, hk, rfl⟩ := Finset.mem_image.mp hz
        obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hk
        obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
        rw [eval_N0 _ _ _ g g.natDegree le_rfl (xs (j + 1)) (xs (j + 1 + 1)) (xs j)]
        · have e1 := hg (j + 1 + 1) (by omega) (by omega)
          have e2 := hg j (by omega) (by omega)
          have e3 := hg (j + 1) (by omega) (by omega)
          rw [e1, e2, e3]
          push_cast
          ring
        · simpa [Interp.numS, Interp.den] using hS (j + 1) hk1 (by omega)
        · simpa [Interp.numT, Interp.den] using hT (j + 1) hk1 (by omega))
    rw [Finset.card_image_of_injOn (hinj.mono (by
      intro k hk; simp only [Finset.coe_Icc, Set.mem_Icc] at hk ⊢; omega))] at key
    simp only [Nat.card_Icc] at key
    omega

/-- Order form: for odd `r`, `r ≤ 6 deg g + 5`. -/
theorem degree_bound_of_x_relations_linear_order (a b x₀ : K) (h2 : (2 : K) ≠ 0)
    (g : K[X]) (r : ℕ) (hr : r % 2 = 1) (xs : ℕ → K)
    (hinj : Set.InjOn xs (Set.Icc 1 ((r - 1) / 2)))
    (hS : ∀ k, 2 ≤ k → k + 1 ≤ (r - 1) / 2 →
      (xs (k + 1) + xs (k - 1)) * (xs k - x₀) ^ 2 = 2 * ((x₀ * xs k + a) * (xs k + x₀) + 2 * b))
    (hT : ∀ k, 2 ≤ k → k + 1 ≤ (r - 1) / 2 →
      xs (k + 1) * xs (k - 1) * (xs k - x₀) ^ 2 = (x₀ * xs k - a) ^ 2 - 4 * b * (xs k + x₀))
    (hg : ∀ k, 1 ≤ k → k ≤ (r - 1) / 2 → g.eval (xs k) = (k : K)) :
    r ≤ 6 * g.natDegree + 5 := by
  have := degree_bound_of_x_relations_linear a b x₀ h2 g ((r - 1) / 2) xs hinj hS hT hg
  omega

end LinearInterp

open WeierstrassCurve WeierstrassCurve.Affine

namespace CurveX

variable {F : Type*} [Field F] [DecidableEq F]

/-- **Curve-level degree bound for the discrete log itself.** `W` short Weierstrass over `F`
with `2 ≠ 0`, `P` of odd order `r`; if `g.eval (x(kP)) = k` in `F` for `1 ≤ k ≤ N` with
`2 N < r` (e.g. `N ≤ (r-1)/2`), then `N ≤ 3 deg g + 2`. (`3 ≠ 0` is not needed.) -/
theorem degree_bound_linear_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ)
    (hr : addOrderOf P = r) (N : ℕ) (hN : 2 * N < r) (g : Polynomial F)
    (hg : ∀ k : ℕ, 1 ≤ k → k ≤ N → g.eval (xCoord (k • P)) = (k : F)) :
    N ≤ 3 * g.natDegree + 2 := by
  refine LinearInterp.degree_bound_of_x_relations_linear W.a₄ W.a₆ (xCoord P) h2' g N
    (fun k => xCoord (k • P)) (xCoord_smul_injOn hr hN) ?_ ?_ hg
  · intro k hk hk'
    exact (smul_relations h1 h2 h3 hr hN hk hk').1
  · intro k hk hk'
    exact (smul_relations h1 h2 h3 hr hN hk hk').2

/-- Order form: `P` of odd order `r`, `g(x(kP)) = k` for `1 ≤ k ≤ (r-1)/2` gives
`r ≤ 6 deg g + 5`. -/
theorem degree_bound_linear_order_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0)
    (h2 : W.a₂ = 0) (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ)
    (hr : addOrderOf P = r) (hodd : r % 2 = 1) (g : Polynomial F)
    (hg : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 → g.eval (xCoord (k • P)) = (k : F)) :
    r ≤ 6 * g.natDegree + 5 := by
  have := degree_bound_linear_short_weierstrass h1 h2 h3 h2' P r hr ((r - 1) / 2)
    (by omega) g hg
  omega

end CurveX

end MathResearch.ECDLP
