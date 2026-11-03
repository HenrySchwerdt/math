module

public import MathResearch.ECDLP.RationalSLP
public import MathResearch.ECDLP.CurveX

/-!
# ECDLP: algebraic decision trees with equality tests (Theorem DT)

Ledger: research/ecdlp, task ECDLP-40 (TSK-8d699b9a-e05b-4eac-9970-37a0857cb6ce),
RUN-038b1cc8-f156-456a-ab1c-736446d72183, hypothesis HYP-dbe79a50-030e-41b9-944b-271f2bd37042.

* `degree_bound_partial_short_weierstrass` (Lemma A): partial agreement `A = k B` on an arbitrary
  `G ⊆ [1, N]` gives at most `3 d` centres `k` with `k - 1, k, k + 1 ∈ G`.
* `Tree`, `Tree.run`, `Tree.arithDepth`: computation trees with equality tests.
* `Tree.length_bound`: a tree of arithmetic depth `L` outputting `k` at `x (kP)`, `1 ≤ k ≤ N`,
  `2 N < r`, forces `N ≤ 9 * 2 ^ L - 1`, whatever its number of tests.

Nothing here concerns comparisons, bit extraction or bit complexity.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace DecisionTree

open RationalSLP WeierstrassCurve WeierstrassCurve.Affine CurveX

section LemmaA

variable {F : Type*} [Field F] [DecidableEq F]

/-- **Lemma A, coprime form.** -/
theorem degree_bound_partial_coprime {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (G : Finset ℕ)
    (A B : F[X]) (d : ℕ) (hA : A.natDegree ≤ d) (hB : B.natDegree ≤ d) (hcop : IsCoprime A B)
    (hB0 : ∀ k ∈ G, B.eval (xCoord (k • P)) ≠ 0)
    (hAB : ∀ k ∈ G, A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P))) :
    ((Finset.Icc 2 (N - 1)).filter (fun k => k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G)).card ≤ 3 * d := by
  set C := (Finset.Icc 2 (N - 1)).filter (fun k => k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G) with hC
  by_cases hC0 : C = ∅
  · simp [hC0]
  obtain ⟨k0, hk0⟩ := Finset.nonempty_iff_ne_empty.mpr hC0
  obtain ⟨hk0I, hk0a, hk0b, hk0c⟩ := Finset.mem_filter.mp hk0
  obtain ⟨hk0l, hk0u⟩ := Finset.mem_Icc.mp hk0I
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
    obtain ⟨Good, hGood⟩ : ∃ Good : ℕ → Prop, ∀ k, Good k ↔
        (B.eval (xCoord (k • P)) ≠ 0 ∧ A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P))) :=
      ⟨_, fun _ => Iff.rfl⟩
    have stepUp : ∀ n : ℕ, 2 ≤ n → n + 2 ≤ r → Good (n - 1) → Good n → Good (n + 1) := by
      intro n hn hnr g1 g2
      obtain ⟨hb2, ha2⟩ := (hGood _).mp g1
      obtain ⟨hb1, ha1⟩ := (hGood _).mp g2
      have hkey := key n hn hnr
      rw [hz, eval_zero] at hkey
      have hDn := hD n hn hnr
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
      exact (hGood _).mpr ⟨hB1, by rw [hA1]; push_cast; ring⟩
    have stepDown : ∀ n : ℕ, 2 ≤ n → n + 2 ≤ r → Good n → Good (n + 1) → Good (n - 1) := by
      intro n hn hnr g1 g2
      obtain ⟨hb1, ha1⟩ := (hGood _).mp g1
      obtain ⟨hb2, ha2⟩ := (hGood _).mp g2
      have hkey := key n hn hnr
      rw [hz, eval_zero] at hkey
      have hDn := hD n hn hnr
      have hbr := (mul_eq_zero.mp hkey.symm).resolve_left (pow_ne_zero _ hDn)
      rw [ha1, ha2] at hbr
      push_cast at hbr
      have hc : ((n - 1 : ℕ) : F) = (n : F) - 1 := by
        rw [Nat.cast_sub (by omega)]; simp
      have hmain : B.eval (xCoord (n • P)) * B.eval (xCoord ((n + 1) • P)) *
          (A.eval (xCoord ((n - 1) • P)) - ((n - 1 : ℕ) : F) * B.eval (xCoord ((n - 1) • P))) = 0 := by
        rw [hc]; linear_combination hbr
      have hmain' := (mul_eq_zero.mp hmain).resolve_left (mul_ne_zero hb1 hb2)
      have hA1 : A.eval (xCoord ((n - 1) • P)) = ((n - 1 : ℕ) : F) * B.eval (xCoord ((n - 1) • P)) :=
        sub_eq_zero.mp hmain'
      have hB1 : B.eval (xCoord ((n - 1) • P)) ≠ 0 := by
        intro hb0
        obtain ⟨s, t, hst⟩ := hcop
        have := congrArg (eval (xCoord ((n - 1) • P))) hst
        simp only [eval_add, eval_mul, eval_one] at this
        rw [hA1, hb0] at this
        simp at this
      exact (hGood _).mpr ⟨hB1, hA1⟩
    have g0 : Good (k0 - 1) := (hGood _).mpr ⟨hB0 _ hk0a, hAB _ hk0a⟩
    have g1 : Good k0 := (hGood _).mpr ⟨hB0 _ hk0b, hAB _ hk0b⟩
    have hup : ∀ j : ℕ, k0 + j ≤ r - 1 → Good (k0 - 1 + j) ∧ Good (k0 + j) := by
      intro j
      induction j with
      | zero => intro _; exact ⟨by simpa using g0, by simpa using g1⟩
      | succ j ih =>
        intro hj
        obtain ⟨u1, u2⟩ := ih (by omega)
        have := stepUp (k0 + j) (by omega) (by omega)
          (by rw [show k0 + j - 1 = k0 - 1 + j by omega]; exact u1) u2
        exact ⟨by rw [show k0 - 1 + (j + 1) = k0 + j by omega]; exact u2,
          by rw [show k0 + (j + 1) = k0 + j + 1 by omega]; exact this⟩
    have hdown : ∀ j : ℕ, j ≤ k0 - 2 → Good (k0 - 1 - j) ∧ Good (k0 - j) := by
      intro j
      induction j with
      | zero => intro _; exact ⟨by simpa using g0, by simpa using g1⟩
      | succ j ih =>
        intro hj
        obtain ⟨u1, u2⟩ := ih (by omega)
        have := stepDown (k0 - 1 - j) (by omega) (by omega) u1
          (by rw [show k0 - 1 - j + 1 = k0 - j by omega]; exact u2)
        exact ⟨by rw [show k0 - 1 - (j + 1) = k0 - 1 - j - 1 by omega]; exact this,
          by rw [show k0 - (j + 1) = k0 - 1 - j by omega]; exact u1⟩
    have hall : ∀ k : ℕ, 1 ≤ k → k ≤ r - 1 → Good k := by
      intro k hk hkr
      by_cases hkk : k0 ≤ k
      · have := (hup (k - k0) (by omega)).2
        rwa [show k0 + (k - k0) = k by omega] at this
      · have := (hdown (k0 - 1 - k) (by omega)).1
        rwa [show k0 - 1 - (k0 - 1 - k) = k by omega] at this
    obtain ⟨s, rfl⟩ : ∃ s, r = s + 3 := ⟨r - 3, by omega⟩
    obtain ⟨hb1, ha1⟩ := (hGood _).mp (hall (s + 2) (by omega) (by omega))
    obtain ⟨hb2, ha2⟩ := (hGood _).mp (hall (s + 1) (by omega) (by omega))
    obtain ⟨hbu1, hau1⟩ := (hGood _).mp (hall 1 le_rfl (by omega))
    obtain ⟨hbu2, hau2⟩ := (hGood _).mp (hall 2 (by omega) (by omega))
    have ex1 : xCoord ((s + 2) • P) = xCoord ((1 : ℕ) • P) := by
      have := xCoord_smul_sub hr (j := 1) (by omega)
      rwa [show s + 3 - 1 = s + 2 by omega] at this
    have ex2 : xCoord ((s + 1) • P) = xCoord ((2 : ℕ) • P) := by
      have := xCoord_smul_sub hr (j := 2) (by omega)
      rwa [show s + 3 - 2 = s + 1 by omega] at this
    rw [ex1] at hb1 ha1
    rw [ex2] at hb2 ha2
    have c1 : ((s + 2 : ℕ) : F) = 1 := by
      have := ha1.symm.trans hau1
      push_cast at this ⊢
      exact mul_right_cancel₀ hbu1 (by simpa using this)
    have c2 : ((s + 1 : ℕ) : F) = 2 := by
      have := ha2.symm.trans hau2
      push_cast at this ⊢
      exact mul_right_cancel₀ hbu2 (by simpa using this)
    push_cast at c1 c2
    exact h2' (by linear_combination c1 - c2)
  have hroots : (C.image (fun k : ℕ => xCoord (k • P))) ⊆
      (Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d).roots.toFinset := by
    intro z hz
    obtain ⟨k, hk, rfl⟩ := Finset.mem_image.mp hz
    obtain ⟨hkI, hka, hkb, hkc⟩ := Finset.mem_filter.mp hk
    obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hkI
    rw [Multiset.mem_toFinset, mem_roots hnz, IsRoot.def, key k hk1 (by omega)]
    have e1 := hAB _ hkc
    have e2 := hAB _ hka
    have e3 := hAB _ hkb
    have hc : ((k - 1 : ℕ) : F) = (k : F) - 1 := by
      rw [Nat.cast_sub (by omega)]; simp
    rw [hc] at e2
    rw [e1, e2, e3]
    push_cast
    ring
  have hcard := Finset.card_le_card hroots
  have hinj : Set.InjOn (fun k : ℕ => xCoord (k • P)) (C : Set ℕ) :=
    (xCoord_smul_injOn hr hN).mono (by
      intro k hk
      obtain ⟨hkI, _⟩ := Finset.mem_filter.mp hk
      obtain ⟨_, _⟩ := Finset.mem_Icc.mp hkI
      simp only [Set.mem_Icc]; omega)
  rw [Finset.card_image_of_injOn hinj] at hcard
  have h2'' := (Multiset.toFinset_card_le _).trans
    (card_roots' (Nrat (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d))
  have hdeg := natDegree_Nrat_le (Interp.numS a b x₀) (Interp.numT a b x₀) (Interp.den x₀) A B d
    (Interp.natDegree_numS_le a b x₀) (by unfold Interp.numT; compute_degree)
    (Interp.natDegree_numT_den_le a b x₀) (Interp.den_natDegree x₀).le hA hB
  omega

/-- **Lemma A (general form, no coprimality).** `W` short Weierstrass over `F` with `2 ≠ 0`, `P` of
order `r`, `2 N < r`. If `A, B` have `natDegree ≤ d`, and `B (x (kP)) ≠ 0`,
`A (x (kP)) = k * B (x (kP))` for every `k` in an arbitrary finite set `G`, then at most `3 d`
integers `k ∈ [2, N - 1]` have `k - 1, k, k + 1 ∈ G`. -/
theorem degree_bound_partial_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (G : Finset ℕ) (A B : F[X]) (d : ℕ) (hA : A.natDegree ≤ d)
    (hB : B.natDegree ≤ d) (hB0 : ∀ k ∈ G, B.eval (xCoord (k • P)) ≠ 0)
    (hAB : ∀ k ∈ G, A.eval (xCoord (k • P)) = (k : F) * B.eval (xCoord (k • P))) :
    ((Finset.Icc 2 (N - 1)).filter (fun k => k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G)).card ≤ 3 * d := by
  by_cases hG0 : G = ∅
  · simp [hG0]
  obtain ⟨k1, hk1⟩ := Finset.nonempty_iff_ne_empty.mpr hG0
  have hBne : B ≠ 0 := by
    intro h
    exact hB0 k1 hk1 (by simp [h])
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
  have hgx : ∀ k ∈ G, g.eval (xCoord (k • P)) ≠ 0 := by
    intro k hk
    have := hB0 k hk
    rw [hBe, eval_mul] at this
    exact left_ne_zero_of_mul this
  refine degree_bound_partial_coprime h1 h2 h3 h2' P r hr N hN G (A / g) (B / g) d
    (hdeg A hAe hA) (hdeg B hBe hB) (isCoprime_div_gcd_div_gcd hBne) ?_ ?_
  · intro k hk
    have := hB0 k hk
    rw [hBe, eval_mul] at this
    exact right_ne_zero_of_mul this
  · intro k hk
    have h := hAB k hk
    rw [hAe, hBe, eval_mul, eval_mul] at h
    refine mul_left_cancel₀ (hgx k hk) ?_
    rw [h]; ring

end LemmaA

section Model

variable {F : Type*}

/-- A computation tree over `F` with one input. Registers are created only by arithmetic nodes
(`arith`), in order; register `0` is the input `u` and is free. `test reg z nz` branches on
"register `reg` is zero"; `leaf out` outputs register `out`. -/
inductive Tree (F : Type*) where
  | leaf (out : ℕ)
  | arith (op : Op F) (next : Tree F)
  | test (reg : ℕ) (ifZero ifNonzero : Tree F)

namespace Tree

/-- Maximum number of arithmetic nodes on a root-to-leaf path (tests are not counted). -/
def arithDepth : Tree F → ℕ
  | leaf _ => 0
  | arith _ n => n.arithDepth + 1
  | test _ z nz => max z.arithDepth nz.arithDepth

variable [Field F]

open Classical in
/-- Execution at input `u` with the register list `acc`. `none` if a division on the executed path
has a zero divisor; otherwise the value of the output register. Out-of-range registers read `0`. -/
noncomputable def run (u : F) : Tree F → List F → Option F
  | leaf o, acc => some (acc.getD o 0)
  | arith op n, acc => if okStep acc op then run u n (acc ++ [stepVal u acc op]) else none
  | test reg z nz, acc => if acc.getD reg 0 = 0 then run u z acc else run u nz acc

/-- Execution from the initial register list `[u]`. -/
noncomputable def exec (u : F) (T : Tree F) : Option F := T.run u [u]

open Classical in
/-- Final formal register list and output index along the generic path: at a test of a register
whose formal numerator is the zero polynomial take the zero branch, otherwise the nonzero one. -/
noncomputable def gfin : List (F[X] × F[X]) → Tree F → List (F[X] × F[X]) × ℕ
  | accF, leaf o => (accF, o)
  | accF, arith op n => gfin (accF ++ [stepFrac accF op]) n
  | accF, test reg z nz =>
    if (accF.getD reg (0, 1)).1 = 0 then gfin accF z else gfin accF nz

open Classical in
/-- The nonzero formal numerators tested along the generic path. -/
noncomputable def gtests : List (F[X] × F[X]) → Tree F → List F[X]
  | _, leaf _ => []
  | accF, arith op n => gtests (accF ++ [stepFrac accF op]) n
  | accF, test reg z nz =>
    if (accF.getD reg (0, 1)).1 = 0 then gtests accF z
    else (accF.getD reg (0, 1)).1 :: gtests accF nz

theorem gfin_ext : ∀ (T : Tree F) (accF : List (F[X] × F[X])),
    ∃ ext : List (F[X] × F[X]), (gfin accF T).1 = accF ++ ext ∧ ext.length ≤ T.arithDepth
  | leaf _, accF => ⟨[], by simp [gfin, arithDepth]⟩
  | arith op n, accF => by
    obtain ⟨ext, h1, h2⟩ := gfin_ext n (accF ++ [stepFrac accF op])
    refine ⟨stepFrac accF op :: ext, ?_, ?_⟩
    · simp only [gfin, h1]; simp
    · simp only [arithDepth]; simp; omega
  | test reg z nz, accF => by
    simp only [gfin, arithDepth]
    split_ifs
    · obtain ⟨ext, h1, h2⟩ := gfin_ext z accF
      exact ⟨ext, h1, h2.trans (le_max_left _ _)⟩
    · obtain ⟨ext, h1, h2⟩ := gfin_ext nz accF
      exact ⟨ext, h1, h2.trans (le_max_right _ _)⟩

theorem degLe_step' (acc : List (F[X] × F[X])) (o : Op F) (m : ℕ)
    (hget : ∀ i : ℕ, DegLe (acc.getD i (0, 1)) (2 ^ m)) :
    DegLe (stepFrac acc o) (2 ^ (m + 1)) := by
  have hone : 1 ≤ 2 ^ (m + 1) := Nat.one_le_two_pow
  have h2 : 2 ^ (m + 1) = 2 ^ m + 2 ^ m := by ring
  have prod : ∀ a b c e : F[X], a.natDegree ≤ 2 ^ m → b.natDegree ≤ 2 ^ m →
      c.natDegree ≤ 2 ^ m → e.natDegree ≤ 2 ^ m → (a * b + c * e).natDegree ≤ 2 ^ (m + 1) := by
    intro a b c e ha hb hc he
    refine (natDegree_add_le _ _).trans (max_le ?_ ?_)
    · exact natDegree_mul_le.trans (by omega)
    · exact natDegree_mul_le.trans (by omega)
  have prod' : ∀ a b : F[X], a.natDegree ≤ 2 ^ m → b.natDegree ≤ 2 ^ m →
      (a * b).natDegree ≤ 2 ^ (m + 1) := by
    intro a b ha hb
    exact natDegree_mul_le.trans (by omega)
  cases o with
  | const c => simp [stepFrac, DegLe]
  | var => exact ⟨by simpa [stepFrac] using (natDegree_X_le (R := F)).trans hone, by simp [stepFrac]⟩
  | add i j =>
    exact ⟨prod _ _ _ _ (hget i).1 (hget j).2 (hget j).1 (hget i).2,
      prod' _ _ (hget i).2 (hget j).2⟩
  | sub i j =>
    refine ⟨?_, prod' _ _ (hget i).2 (hget j).2⟩
    simp only [stepFrac]
    refine (natDegree_sub_le _ _).trans (max_le ?_ ?_)
    · exact natDegree_mul_le.trans (by have := (hget i).1; have := (hget j).2; omega)
    · exact natDegree_mul_le.trans (by have := (hget j).1; have := (hget i).2; omega)
  | mul i j => exact ⟨prod' _ _ (hget i).1 (hget j).1, prod' _ _ (hget i).2 (hget j).2⟩
  | div i j => exact ⟨prod' _ _ (hget i).1 (hget j).2, prod' _ _ (hget i).2 (hget j).1⟩

/-- Index-wise degree invariant: register `i` has formal degrees `≤ 2 ^ i`. -/
def DegInv (acc : List (F[X] × F[X])) : Prop :=
  1 ≤ acc.length ∧ ∀ i, i < acc.length → DegLe (acc.getD i (0, 1)) (2 ^ i)

theorem degInv_step {acc : List (F[X] × F[X])} (h : DegInv acc) (o : Op F) :
    DegInv (acc ++ [stepFrac acc o]) := by
  obtain ⟨hlen, hi⟩ := h
  obtain ⟨m, hm⟩ : ∃ m, acc.length = m + 1 := ⟨acc.length - 1, by omega⟩
  have hget : ∀ i : ℕ, DegLe (acc.getD i (0, 1)) (2 ^ m) := by
    intro i
    by_cases hi' : i < acc.length
    · exact (hi i hi').mono (pow_le_pow_right₀ (by norm_num) (by omega))
    · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
      simp [DegLe]
  have hnew := degLe_step' acc o m hget
  refine ⟨by simp, fun i hi' => ?_⟩
  rw [getD_snoc]
  simp only [List.length_append, List.length_singleton] at hi'
  by_cases h1 : i < acc.length
  · simp only [h1, ↓reduceIte]; exact hi i h1
  · have h2 : i = acc.length := by omega
    subst h2
    simp only [lt_irrefl, ↓reduceIte]
    rw [hm]
    exact hnew

theorem degInv_gfin : ∀ (T : Tree F) (accF : List (F[X] × F[X])), DegInv accF →
    DegInv (gfin accF T).1
  | leaf _, accF, h => by simpa [gfin] using h
  | arith op n, accF, h => by
    simpa [gfin] using degInv_gfin n _ (degInv_step h op)
  | test reg z nz, accF, h => by
    simp only [gfin]
    split_ifs
    · exact degInv_gfin z accF h
    · exact degInv_gfin nz accF h

theorem mem_gtests : ∀ (T : Tree F) (accF : List (F[X] × F[X])), ∀ p ∈ gtests accF T,
    p ≠ 0 ∧ ∃ i, i < (gfin accF T).1.length ∧ p = ((gfin accF T).1.getD i (0, 1)).1
  | leaf _, accF, p, hp => by simp [gtests] at hp
  | arith op n, accF, p, hp => by
    simpa [gtests, gfin] using mem_gtests n _ p (by simpa [gtests] using hp)
  | test reg z nz, accF, p, hp => by
    simp only [gtests] at hp
    simp only [gfin]
    split_ifs at hp ⊢ with hz
    · exact mem_gtests z accF p hp
    · rcases List.mem_cons.mp hp with rfl | hp
      · obtain ⟨ext, hext, _⟩ := gfin_ext nz accF
        have hreg : reg < accF.length := by
          by_contra hh
          apply hz
          rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
          simp
        refine ⟨hz, reg, ?_, ?_⟩
        · rw [hext]; simp; omega
        · rw [hext, List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD,
            List.getElem?_append_left hreg]
      · exact mem_gtests nz accF p hp

theorem inv_init (u : F) : Inv u [((X : F[X]), (1 : F[X]))] [u] := by
  refine ⟨rfl, fun i => ?_⟩
  rcases i with _ | i
  · simp
  · simp

/-- On inputs avoiding every root of the tested numerators, the execution follows the generic
path and outputs the generic formal fraction. -/
theorem run_generic (u : F) : ∀ (T : Tree F) (accF : List (F[X] × F[X])) (accV : List F) (v : F),
    Inv u accF accV → T.run u accV = some v → (∀ p ∈ gtests accF T, p.eval u ≠ 0) →
    ((gfin accF T).1.getD (gfin accF T).2 (0, 1)).2.eval u ≠ 0 ∧
      v = ((gfin accF T).1.getD (gfin accF T).2 (0, 1)).1.eval u /
        ((gfin accF T).1.getD (gfin accF T).2 (0, 1)).2.eval u
  | leaf o, accF, accV, v, hinv, hrun, _ => by
    simp only [run, Option.some.injEq] at hrun
    obtain ⟨hd, hv⟩ := hinv.2 o
    simp only [gfin]
    exact ⟨hd, by rw [← hrun]; exact hv⟩
  | arith op n, accF, accV, v, hinv, hrun, hts => by
    simp only [run] at hrun
    split_ifs at hrun with hok
    · exact run_generic u n _ _ v (inv_step u accF accV op hinv hok) hrun
        (by simpa [gtests] using hts)
  | test reg z nz, accF, accV, v, hinv, hrun, hts => by
    obtain ⟨hd, hv⟩ := hinv.2 reg
    simp only [run] at hrun
    simp only [gfin, gtests] at hts ⊢
    by_cases hp : (accF.getD reg (0, 1)).1 = 0
    · simp only [hp, ↓reduceIte] at hts ⊢
      have hz : accV.getD reg 0 = 0 := by rw [hv, hp]; simp
      simp only [hz, ↓reduceIte] at hrun
      exact run_generic u z accF accV v hinv hrun hts
    · simp only [hp, ↓reduceIte] at hts ⊢
      have hnz : accV.getD reg 0 ≠ 0 := by
        rw [hv]
        exact div_ne_zero (hts _ List.mem_cons_self) hd
      simp only [hnz, ↓reduceIte] at hrun
      exact run_generic u nz accF accV v hinv hrun (fun q hq => hts q (List.mem_cons_of_mem _ hq))

end Tree

end Model

section Count

variable {F : Type*} [Field F] [DecidableEq F]

theorem sum_two_pow (n : ℕ) : ∑ i ∈ Finset.range n, 2 ^ i + 1 = 2 ^ n := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, pow_succ]; omega

/-- At most `2 ^ len - 1` indices `k ≤ N` have `x (kP)` a root of a nonzero numerator among
registers `i < len` with degrees `≤ 2 ^ i`. -/
theorem card_bad_le {W : Affine F} (P : W.Point) (r : ℕ) (hr : addOrderOf P = r) (N : ℕ)
    (hN : 2 * N < r) (fin : List (F[X] × F[X]))
    (hdeg : ∀ i, i < fin.length → DegLe (fin.getD i (0, 1)) (2 ^ i)) :
    ((Finset.Icc 1 N).filter (fun k => ∃ i, i < fin.length ∧ (fin.getD i (0, 1)).1 ≠ 0 ∧
        (fin.getD i (0, 1)).1.eval (xCoord (k • P)) = 0)).card ≤ 2 ^ fin.length - 1 := by
  have hsub : ((Finset.Icc 1 N).filter (fun k => ∃ i, i < fin.length ∧
      (fin.getD i (0, 1)).1 ≠ 0 ∧ (fin.getD i (0, 1)).1.eval (xCoord (k • P)) = 0)) ⊆
      (Finset.range fin.length).biUnion (fun i => (Finset.Icc 1 N).filter (fun k =>
        (fin.getD i (0, 1)).1 ≠ 0 ∧ (fin.getD i (0, 1)).1.eval (xCoord (k • P)) = 0)) := by
    intro k hk
    obtain ⟨hkI, i, hi, h⟩ := Finset.mem_filter.mp hk
    exact Finset.mem_biUnion.mpr ⟨i, Finset.mem_range.mpr hi, Finset.mem_filter.mpr ⟨hkI, h⟩⟩
  have hone : ∀ i ∈ Finset.range fin.length, ((Finset.Icc 1 N).filter (fun k =>
        (fin.getD i (0, 1)).1 ≠ 0 ∧ (fin.getD i (0, 1)).1.eval (xCoord (k • P)) = 0)).card
        ≤ 2 ^ i := by
    intro i hi
    have hi' := Finset.mem_range.mp hi
    by_cases h0 : (fin.getD i (0, 1)).1 = 0
    · rw [Finset.filter_false_of_mem (fun k _ h => h.1 h0)]; simp
    · have hinj : Set.InjOn (fun k : ℕ => xCoord (k • P)) (Finset.Icc 1 N : Set ℕ) := by
        simpa using xCoord_smul_injOn hr hN
      refine le_trans (Finset.card_le_card_of_injOn (fun k : ℕ => xCoord (k • P))
        (t := (fin.getD i (0, 1)).1.roots.toFinset) ?_ (hinj.mono (by
          intro k hk
          obtain ⟨hkI, _⟩ := Finset.mem_filter.mp hk
          exact hkI))) ?_
      · intro k hk
        obtain ⟨_, _, he⟩ := Finset.mem_filter.mp hk
        simp only [Finset.mem_coe, Multiset.mem_toFinset, mem_roots h0, IsRoot.def]
        exact he
      · exact ((Multiset.toFinset_card_le _).trans (card_roots' _)).trans (hdeg i hi').1
  have := (Finset.card_le_card hsub).trans (Finset.card_biUnion_le.trans (Finset.sum_le_sum hone))
  have h2 := sum_two_pow fin.length
  omega

end Count

section Main

variable {F : Type*} [Field F] [DecidableEq F]

/-- **Theorem DT (algebraic computation trees with equality tests).** `W` short Weierstrass over `F`
with `2 ≠ 0`, `P` of order `r`, `2 N < r`. Let `T` be a computation tree (arithmetic `+ - * /`,
constants, tests "register `= 0`", one input `u`) such that, for every `1 ≤ k ≤ N`, the execution
on `u = x (kP)` has all executed divisions defined and outputs `k`. If every path of `T` has at most
`L` arithmetic nodes, then `N ≤ 9 * 2 ^ L - 1`, regardless of the number of tests/depth. -/
theorem Tree.length_bound {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (T : Tree F) (L : ℕ) (hL : T.arithDepth ≤ L)
    (hrun : ∀ k : ℕ, 1 ≤ k → k ≤ N → T.exec (xCoord (k • P)) = some (k : F)) :
    N ≤ 9 * 2 ^ L - 1 := by
  set acc0 : List (F[X] × F[X]) := [((X : F[X]), (1 : F[X]))] with hacc0
  have hdi : Tree.DegInv acc0 := by
    refine ⟨by simp [hacc0], fun i hi => ?_⟩
    have : i = 0 := by simp [hacc0] at hi; omega
    subst this
    simp [hacc0, DegLe]
  have hdf := Tree.degInv_gfin T acc0 hdi
  obtain ⟨ext, hext, hextlen⟩ := Tree.gfin_ext T acc0
  have hlen : (Tree.gfin acc0 T).1.length ≤ L + 1 := by
    rw [hext]; simp [hacc0]; omega
  set fin := (Tree.gfin acc0 T).1 with hfin
  set q := fin.getD (Tree.gfin acc0 T).2 (0, 1) with hq
  have hqdeg : DegLe q (2 ^ L) := by
    by_cases ho : (Tree.gfin acc0 T).2 < fin.length
    · exact (hdf.2 _ ho).mono (pow_le_pow_right₀ (by norm_num) (by omega))
    · rw [hq, List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
      simp [DegLe]
  set G := (Finset.Icc 1 N).filter (fun k => ∀ p ∈ Tree.gtests acc0 T,
    p.eval (xCoord (k • P)) ≠ 0) with hG
  have hGdata : ∀ k ∈ G, q.2.eval (xCoord (k • P)) ≠ 0 ∧
      q.1.eval (xCoord (k • P)) = (k : F) * q.2.eval (xCoord (k • P)) := by
    intro k hk
    obtain ⟨hkI, hkt⟩ := Finset.mem_filter.mp hk
    obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hkI
    obtain ⟨hd, hv⟩ := Tree.run_generic _ T acc0 [xCoord (k • P)] (k : F)
      (Tree.inv_init _) (hrun k hk1 hk2) hkt
    have hd' : q.2.eval (xCoord (k • P)) ≠ 0 := hd
    have hv' : (k : F) = q.1.eval (xCoord (k • P)) / q.2.eval (xCoord (k • P)) := hv
    refine ⟨hd', ?_⟩
    rw [hv']; field_simp
  have hA := degree_bound_partial_short_weierstrass h1 h2 h3 h2' P r hr N hN G q.1 q.2 (2 ^ L)
    hqdeg.1 hqdeg.2 (fun k hk => (hGdata k hk).1) (fun k hk => (hGdata k hk).2)
  set Bad := (Finset.Icc 1 N).filter (fun k => ¬ ∀ p ∈ Tree.gtests acc0 T,
    p.eval (xCoord (k • P)) ≠ 0) with hBad
  have hBadcard : Bad.card ≤ 2 ^ (L + 1) - 1 := by
    have hc := card_bad_le P r hr N hN fin hdf.2
    have hsub : Bad ⊆ (Finset.Icc 1 N).filter (fun k => ∃ i, i < fin.length ∧
        (fin.getD i (0, 1)).1 ≠ 0 ∧ (fin.getD i (0, 1)).1.eval (xCoord (k • P)) = 0) := by
      intro k hk
      obtain ⟨hkI, hkn⟩ := Finset.mem_filter.mp hk
      push Not at hkn
      obtain ⟨p, hp, hp0⟩ := hkn
      obtain ⟨hpne, i, hi, hpi⟩ := Tree.mem_gtests T acc0 p hp
      refine Finset.mem_filter.mpr ⟨hkI, i, hi, ?_, ?_⟩
      · rw [← hpi]; exact hpne
      · rw [← hpi]; exact hp0
    have h2l : 2 ^ fin.length ≤ 2 ^ (L + 1) := pow_le_pow_right₀ (by norm_num) hlen
    have := (Finset.card_le_card hsub).trans hc
    omega
  have hcover : Finset.Icc 2 (N - 1) ⊆
      ((Finset.Icc 2 (N - 1)).filter (fun k => k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G)) ∪
        Bad.biUnion (fun b => ({b - 1, b, b + 1} : Finset ℕ)) := by
    intro k hk
    obtain ⟨hk1, hk2⟩ := Finset.mem_Icc.mp hk
    by_cases hc : k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G
    · exact Finset.mem_union_left _ (Finset.mem_filter.mpr ⟨hk, hc⟩)
    · apply Finset.mem_union_right
      have hmem : ∀ j, 1 ≤ j → j ≤ N → j ∉ G → j ∈ Bad := by
        intro j hj1 hj2 hjG
        refine Finset.mem_filter.mpr ⟨Finset.mem_Icc.mpr ⟨hj1, hj2⟩, fun hh => hjG ?_⟩
        exact Finset.mem_filter.mpr ⟨Finset.mem_Icc.mpr ⟨hj1, hj2⟩, hh⟩
      rw [Finset.mem_biUnion]
      by_cases ha : k - 1 ∈ G
      · by_cases hb : k ∈ G
        · have hcc : k + 1 ∉ G := fun h => hc ⟨ha, hb, h⟩
          exact ⟨k + 1, hmem _ (by omega) (by omega) hcc, by simp⟩
        · exact ⟨k, hmem _ (by omega) (by omega) hb, by simp⟩
      · exact ⟨k - 1, hmem _ (by omega) (by omega) ha, by simp; omega⟩
  have hcard1 := Finset.card_le_card hcover
  have hcard2 := (Finset.card_union_le _ _).trans' hcard1
  have hcard3 : (Bad.biUnion (fun b => ({b - 1, b, b + 1} : Finset ℕ))).card ≤ Bad.card * 3 := by
    refine Finset.card_biUnion_le_card_mul _ _ 3 (fun b _ => ?_)
    exact Finset.card_le_three
  have hcard4 : (Finset.Icc 2 (N - 1)).card = N - 2 := by simp; omega
  have hp : 1 ≤ 2 ^ L := Nat.one_le_two_pow
  have hpp : 2 ^ (L + 1) = 2 * 2 ^ L := by ring
  have := Finset.card_union_le
    ((Finset.Icc 2 (N - 1)).filter (fun k => k - 1 ∈ G ∧ k ∈ G ∧ k + 1 ∈ G))
    (Bad.biUnion (fun b => ({b - 1, b, b + 1} : Finset ℕ)))
  omega

end Main

end DecisionTree

end MathResearch.ECDLP
