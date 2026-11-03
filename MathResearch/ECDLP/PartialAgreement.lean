module

public import MathResearch.ECDLP.CurveX

/-!
# ECDLP: partial-agreement degree bound `S_j(A) ≤ 3 deg g`

Ledger: research/ecdlp, task ECDLP-27 (TSK-1e2b2bbf-772e-4d0e-932b-91009cb1282e),
RUN-ac3107bf-b5bd-44a0-ae47-8413aed2f895; HYP-a1dd5501 part (2). Generalizes the root-counting
argument of `Interp`/`LinearInterp` from consecutive `k` (step 1) to step `j` and a subset `A`.
The second difference of `k ↦ k²` with step `j` is the constant `c = 2 j²`; the cleared polynomial
`D^d (Σ gᵢ ... ) - D^d (2 g + c)` has degree exactly `3 d` for `d = deg g ≥ 1` whatever `c` is.
If `deg g = 0` one needs `c ≠ 0`, i.e. `(j : F) ≠ 0` (and `2 ≠ 0`); this is a genuine hypothesis
of the formal statement. Nothing here concerns bit complexity or existence of `g`.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace PartialAgreement

variable {K : Type*} [Field K]

/-- Cleared polynomial `D^d (g(z₁) + g(z₂) - 2 g(u) - c)` for an arbitrary constant `c`. -/
noncomputable def Nc (A B D g : K[X]) (d : ℕ) (c : K) : K[X] :=
  (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * Interp.q A B D i)) -
    D ^ d * (2 * g + C c)

theorem eval_Nc (A B D g : K[X]) (d : ℕ) (c : K) (hg : g.natDegree ≤ d) (u z₁ z₂ : K)
    (hS : (z₁ + z₂) * D.eval u = A.eval u) (hT : z₁ * z₂ * D.eval u = B.eval u) :
    (Nc A B D g d c).eval u =
      D.eval u ^ d * (g.eval z₁ + g.eval z₂ - 2 * g.eval u - c) := by
  have h := Interp.eval_N A B D g d hg u z₁ z₂ hS hT
  have e : Nc A B D g d c = Interp.N A B D g d + D ^ d * (2 - C c) := by
    unfold Nc Interp.N; ring
  rw [e, eval_add, h, eval_mul, eval_pow, eval_sub, eval_C]
  simp only [eval_ofNat]
  ring

/-- Counting lemma: for `g` of degree `d ≥ 1`, `Nc` is nonzero of degree exactly `3 d`
for every constant `c`, so a set of roots has at most `3 d` elements. -/
theorem countingc (A B D g : K[X]) (c : K) (hA : A.natDegree ≤ 2)
    (hBD : (B * D).natDegree ≤ 4) (hD : D.Monic) (hD2 : D.natDegree = 2)
    (h2 : (2 : K) ≠ 0) (hd : 1 ≤ g.natDegree) (Z : Finset K)
    (hZ : ∀ z ∈ Z, (Nc A B D g g.natDegree c).eval z = 0) :
    Z.card ≤ 3 * g.natDegree := by
  set d := g.natDegree with hd_def
  have hfirst := Interp.natDegree_N_le A B D g d hA hBD hD2.le
  have hDp : (D ^ d).natDegree = 2 * d := by rw [hD.natDegree_pow, hD2]; ring
  have hC : (2 * g + C c : K[X]) = C 2 * g + C c := by
    rw [show (C (2 : K)) = 2 from map_ofNat C 2]
  have hc : (C (2 : K) * g).natDegree = d := natDegree_C_mul h2
  have hgl : (2 * g + C c : K[X]).natDegree = d := by
    rw [hC, natDegree_add_eq_left_of_natDegree_lt]
    · exact hc
    · rw [hc, natDegree_C]; omega
  have hne : (2 * g + C c : K[X]) ≠ 0 := by
    intro h; rw [h] at hgl; simp at hgl; omega
  have hsec : (D ^ d * (2 * g + C c)).natDegree = 3 * d := by
    rw [natDegree_mul (pow_ne_zero _ hD.ne_zero) hne, hDp, hgl]; ring
  have hlt : (∑ i ∈ Finset.range (d + 1), C (g.coeff i) * (D ^ (d - i) * Interp.q A B D i)).natDegree
      < (D ^ d * (2 * g + C c)).natDegree := by rw [hsec]; omega
  have hN : (Nc A B D g d c).natDegree = 3 * d := by
    unfold Nc
    rw [natDegree_sub_eq_right_of_natDegree_lt hlt, hsec]
  have hN0 : Nc A B D g d c ≠ 0 := by
    intro h; rw [h] at hN; simp at hN; omega
  have := card_le_degree_of_subset_roots (p := Nc A B D g d c) (Z := Z) (by
    intro z hz
    exact (mem_roots hN0).2 (hZ z hz))
  rw [hN] at this
  exact this

/-- **Abstract partial-agreement bound.** For a finite index set `C` with injective centre map
`xc`, plus/minus maps `xp`, `xm` satisfying the cleared sum/product relations with centre
offset `x₀`, and `g(xp i) + g(xm i) - 2 g(xc i) = c` for `i ∈ C`: `#C ≤ 3 deg g`, provided
`deg g ≥ 1` or `c ≠ 0`. -/
theorem card_le_three_natDegree {ι : Type*} (a b x₀ c : K) (h2 : (2 : K) ≠ 0) (g : K[X])
    (hd : 1 ≤ g.natDegree ∨ c ≠ 0) (C : Finset ι) (xc xp xm : ι → K)
    (hinj : Set.InjOn xc C)
    (hS : ∀ i ∈ C, (xp i + xm i) * (xc i - x₀) ^ 2 =
      2 * ((x₀ * xc i + a) * (xc i + x₀) + 2 * b))
    (hT : ∀ i ∈ C, xp i * xm i * (xc i - x₀) ^ 2 =
      (x₀ * xc i - a) ^ 2 - 4 * b * (xc i + x₀))
    (hg : ∀ i ∈ C, g.eval (xp i) + g.eval (xm i) - 2 * g.eval (xc i) = c) :
    C.card ≤ 3 * g.natDegree := by
  classical
  rcases Nat.eq_zero_or_pos g.natDegree with hd0 | hd1
  · have hc : c ≠ 0 := by
      rcases hd with h | h
      · omega
      · exact h
    have hempty : C = ∅ := by
      rw [Finset.eq_empty_iff_forall_notMem]
      intro i hi
      have := hg i hi
      rw [eq_C_of_natDegree_eq_zero hd0] at this
      simp only [eval_C] at this
      exact hc (by rw [← this]; ring)
    simp [hempty]
  · have key := countingc (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) g c
      (Interp.natDegree_numS_le a b x₀)
      (Interp.natDegree_numT_den_le a b x₀) (Interp.den_monic x₀) (Interp.den_natDegree x₀) h2
      hd1 (C.image xc) (by
        intro z hz
        obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hz
        rw [eval_Nc _ _ _ g g.natDegree c le_rfl (xc i) (xp i) (xm i)]
        · have := hg i hi
          rw [this]; ring
        · simpa [Interp.numS, Interp.den] using hS i hi
        · simpa [Interp.numT, Interp.den] using hT i hi)
    rwa [Finset.card_image_of_injOn hinj] at key

end PartialAgreement

open WeierstrassCurve WeierstrassCurve.Affine

namespace CurveX

variable {F : Type*} [Field F] [DecidableEq F]

/-- X1/X2 for arbitrary nonzero `Q`, `P'` with distinct x-coordinates. -/
theorem relations_add_sub {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0) (h3 : W.a₃ = 0)
    {Q P' : W.Point} (hQ : Q ≠ 0) (hP : P' ≠ 0) (hx : xCoord Q ≠ xCoord P') :
    (xCoord (Q + P') + xCoord (Q - P')) * (xCoord Q - xCoord P') ^ 2 =
      2 * ((xCoord P' * xCoord Q + W.a₄) * (xCoord Q + xCoord P') + 2 * W.a₆) ∧
    xCoord (Q + P') * xCoord (Q - P') * (xCoord Q - xCoord P') ^ 2 =
      (xCoord P' * xCoord Q - W.a₄) ^ 2 - 4 * W.a₆ * (xCoord Q + xCoord P') := by
  cases Q with
  | zero => exact absurd rfl hQ
  | some u v hQ' =>
    cases P' with
    | zero => exact absurd rfl hP
    | some x₀ y₀ hP' =>
      exact xCoord_relations h1 h2 h3 hQ' hP' hx

open Polynomial in
/-- **Partial-agreement degree bound (HYP-a1dd5501 part (2)).** `W` short Weierstrass over `F`
with `2 ≠ 0`; `P` of order `r`; `2 N < r`; `A ⊆ [1, N]`; `g(x(kP)) = k²` for `k ∈ A`. For
`j ≥ 1`, the number of `k ∈ A` with `j < k`, `k - j ∈ A`, `k + j ∈ A` is at most `3 deg g`,
provided `deg g ≥ 1` or `(j : F) ≠ 0`. -/
theorem partial_agreement_degree_bound {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (A : Finset ℕ) (hA : ∀ k ∈ A, 1 ≤ k ∧ k ≤ N) (g : F[X])
    (hg : ∀ k ∈ A, g.eval (xCoord (k • P)) = (k : F) ^ 2) (j : ℕ) (hj : 1 ≤ j)
    (hjg : 1 ≤ g.natDegree ∨ (j : F) ≠ 0) :
    (A.filter (fun k => j < k ∧ k - j ∈ A ∧ k + j ∈ A)).card ≤ 3 * g.natDegree := by
  classical
  set C := A.filter (fun k => j < k ∧ k - j ∈ A ∧ k + j ∈ A) with hC
  have hmem : ∀ k ∈ C, j < k ∧ k - j ∈ A ∧ k + j ∈ A ∧ k ∈ A := by
    intro k hk
    obtain ⟨hkA, hk2⟩ := Finset.mem_filter.mp hk
    exact ⟨hk2.1, hk2.2.1, hk2.2.2, hkA⟩
  have hinj := xCoord_smul_injOn (W := W) hr hN
  have hjA : ∀ k ∈ C, 1 ≤ j ∧ j ≤ N := by
    intro k hk
    obtain ⟨a1, a2, a3, a4⟩ := hmem k hk
    exact ⟨hj, by have := (hA k a4).2; omega⟩
  refine PartialAgreement.card_le_three_natDegree W.a₄ W.a₆ (xCoord (j • P)) (2 * (j : F) ^ 2)
    h2' g ?_ C (fun k => xCoord (k • P)) (fun k => xCoord ((k + j) • P))
    (fun k => xCoord ((k - j) • P)) ?_ ?_ ?_ ?_
  · rcases hjg with h | h
    · exact Or.inl h
    · exact Or.inr (mul_ne_zero h2' (pow_ne_zero 2 h))
  · intro k hk l hl hkl
    have hk' := (hA k (hmem k hk).2.2.2)
    have hl' := (hA l (hmem l hl).2.2.2)
    exact hinj (by simpa using hk') (by simpa using hl') hkl
  all_goals
    intro k hk
    obtain ⟨a1, a2, a3, a4⟩ := hmem k hk
    have hkA := hA k a4
    have hjN := hjA k hk
    have hP0 : j • P ≠ 0 := nsmul_ne_zero_of_lt hr hj (by omega)
    have hQ0 : k • P ≠ 0 := nsmul_ne_zero_of_lt hr (by omega) (by omega)
    have hx : xCoord (k • P) ≠ xCoord (j • P) := by
      intro h
      have := hinj (x₁ := k) (x₂ := j) (by simp only [Set.mem_Icc]; omega)
        (by simp only [Set.mem_Icc]; omega) h
      omega
    have ep : (k + j) • P = k • P + j • P := add_nsmul P k j
    have em : (k - j) • P = k • P - j • P := by
      rw [eq_sub_iff_add_eq, ← add_nsmul, Nat.sub_add_cancel a1.le]
    have := relations_add_sub h1 h2 h3 hQ0 hP0 hx
    rw [ep, em]
  · exact this.1
  · exact this.2
  · have e1 := hg (k + j) a3
    have e2 := hg (k - j) a2
    have e3 := hg k a4
    rw [← ep, ← em, e1, e2, e3]
    have : ((k - j : ℕ) : F) = (k : F) - j := by rw [Nat.cast_sub a1.le]
    push_cast
    rw [this]
    ring

end CurveX

end MathResearch.ECDLP
