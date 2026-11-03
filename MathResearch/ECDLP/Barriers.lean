module

public import MathResearch.ECDLP.Basic
public import Mathlib.GroupTheory.OrderOfElement
public import Mathlib.Data.Nat.PrimeFin
public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Data.Int.Interval
public import Mathlib.Data.Set.Card
public import Mathlib.Tactic

/-!
# ECDLP: generic-program coefficient bound and embedding-degree trace bound

Ledger: research/ecdlp, task ECDLP-10 (TSK-afacfd9c-4a07-4b4f-b7ce-4ccd3341da0e),
RUN-d0b4df5c-47cc-43e7-a7bb-449926187a0b.

Part A formalizes HYP-57d71f43 (addition/subtraction straight-line programs compute only
`n • P` with `|n| ≤ 2 ^ length`, hence cannot reach every element of a large cyclic group).
Part B formalizes HYP-eff2cfbb (few Hasse-interval traces are "M-bad"). No bit-complexity
statement is made; Part A is an unconditional bound on a restricted program model only.
-/

@[expose] public section

namespace MathResearch.ECDLP

/-! ## Part A: straight-line programs -/

section SLP

variable {G : Type*} [AddCommGroup G]

/-- A straight-line program step `(j, l, b₁, b₂)` appends `s₁ • a_j + s₂ • a_l` where
`s = 1` if the Boolean is `true` and `-1` otherwise; out-of-range indices read `0`. -/
def slpStep (acc : List G) (s : ℕ × ℕ × Bool × Bool) : G :=
  (if s.2.2.1 then (1 : ℤ) else -1) • acc.getD s.1 0 +
    (if s.2.2.2 then (1 : ℤ) else -1) • acc.getD s.2.1 0

/-- Evaluation of a program on `P`: the list `[P, a₁, …, a_L]`. -/
def slpEval (P : G) (prog : List (ℕ × ℕ × Bool × Bool)) : List G :=
  prog.foldl (fun acc s => acc ++ [slpStep acc s]) [P]

private lemma sign_bound (b : Bool) (n : ℤ) : |(if b then (1 : ℤ) else -1) * n| = |n| := by
  cases b <;> simp

private lemma slpEval_aux (P : G) (prog : List (ℕ × ℕ × Bool × Bool)) :
    ∀ (acc : List G) (k : ℕ),
      (∀ x ∈ acc, ∃ n : ℤ, x = n • P ∧ |n| ≤ 2 ^ k) →
      ∀ x ∈ prog.foldl (fun acc s => acc ++ [slpStep acc s]) acc,
        ∃ n : ℤ, x = n • P ∧ |n| ≤ 2 ^ (k + prog.length) := by
  induction prog with
  | nil => intro acc k h x hx; simpa using h x hx
  | cons s rest ih =>
    intro acc k h x hx
    have hget : ∀ i : ℕ, ∃ n : ℤ, acc.getD i 0 = n • P ∧ |n| ≤ 2 ^ k := by
      intro i
      by_cases hi : i < acc.length
      · have : acc.getD i 0 ∈ acc := by
          rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]; exact List.getElem_mem hi
        exact h _ this
      · refine ⟨0, ?_, by positivity⟩
        rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; simp
    have key : ∀ y ∈ acc ++ [slpStep acc s], ∃ n : ℤ, y = n • P ∧ |n| ≤ 2 ^ (k + 1) := by
      intro y hy
      rcases List.mem_append.mp hy with hy | hy
      · obtain ⟨n, h1, h2⟩ := h y hy
        exact ⟨n, h1, h2.trans (pow_le_pow_right₀ (by norm_num) (by omega))⟩
      · have hy' : y = slpStep acc s := by simpa using hy
        obtain ⟨n1, h1, h1b⟩ := hget s.1
        obtain ⟨n2, h2, h2b⟩ := hget s.2.1
        refine ⟨(if s.2.2.1 then (1 : ℤ) else -1) * n1 + (if s.2.2.2 then (1 : ℤ) else -1) * n2,
          ?_, ?_⟩
        · rw [hy', slpStep, h1, h2, add_smul, mul_smul, mul_smul]
        · calc _ ≤ |(if s.2.2.1 then (1 : ℤ) else -1) * n1| +
                |(if s.2.2.2 then (1 : ℤ) else -1) * n2| := abs_add_le _ _
            _ = |n1| + |n2| := by rw [sign_bound, sign_bound]
            _ ≤ 2 ^ k + 2 ^ k := add_le_add h1b h2b
            _ = 2 ^ (k + 1) := by ring
    have := ih _ (k + 1) key x hx
    simpa [List.length_cons, Nat.add_assoc, Nat.add_comm 1] using this

/-- A1 (HYP-57d71f43, coefficient bound): every value computed by an addition/subtraction
straight-line program of length `L` from `P` is `n • P` with `|n| ≤ 2 ^ L`. -/
theorem slpEval_mem_bound (P : G) (prog : List (ℕ × ℕ × Bool × Bool)) {x : G}
    (hx : x ∈ slpEval P prog) : ∃ n : ℤ, x = n • P ∧ |n| ≤ 2 ^ prog.length := by
  have := slpEval_aux P prog [P] 0 (by
    intro y hy
    obtain rfl : y = P := by simpa using hy
    exact ⟨1, by simp, by simp⟩) x hx
  simpa using this

/-- A2 (HYP-57d71f43, corollary): if `P` has finite additive order `r` with
`2 ^ (L + 1) + 1 < r`, some `Q ∈ zmultiples P` is not among the values of any
addition/subtraction straight-line program of length at most `L`. -/
theorem exists_unreachable_of_addOrderOf (P : G) {r L : ℕ} (hP : addOrderOf P = r)
    (hr : 2 ^ (L + 1) + 1 < r) :
    ∃ Q ∈ AddSubgroup.zmultiples P,
      ∀ prog : List (ℕ × ℕ × Bool × Bool), prog.length ≤ L → Q ∉ slpEval P prog := by
  classical
  by_contra hcon
  push Not at hcon
  set S : Finset G := (Finset.Icc (-(2 ^ L : ℤ)) (2 ^ L)).image (fun n : ℤ => n • P) with hS
  have hsub : (AddSubgroup.zmultiples P : Set G) ⊆ (S : Set G) := by
    intro Q hQ
    obtain ⟨prog, hlen, hmem⟩ := hcon Q hQ
    obtain ⟨n, rfl, hn⟩ := slpEval_mem_bound P prog hmem
    have hn' : |n| ≤ 2 ^ L := hn.trans (pow_le_pow_right₀ (by norm_num) hlen)
    rw [abs_le] at hn'
    rw [hS, Finset.mem_coe, Finset.mem_image]
    exact ⟨n, Finset.mem_Icc.mpr hn', rfl⟩
  have h1 : Nat.card (AddSubgroup.zmultiples P) = r := by rw [Nat.card_zmultiples, hP]
  have h2 : Nat.card (AddSubgroup.zmultiples P) ≤ S.card := by
    have := Set.ncard_le_ncard hsub S.finite_toSet
    rw [Set.ncard_coe_finset, ← Nat.card_coe_set_eq] at this
    exact this
  have h3 : S.card ≤ 2 ^ (L + 1) + 1 := by
    refine (Finset.card_image_le (s := Finset.Icc (-(2 ^ L : ℤ)) (2 ^ L))).trans ?_
    rw [Int.card_Icc]
    have : ((2 ^ L : ℤ) + 1 - -(2 ^ L : ℤ)).toNat = 2 ^ (L + 1) + 1 := by
      have : (2 ^ L : ℤ) + 1 - -(2 ^ L : ℤ) = ((2 ^ (L + 1) + 1 : ℕ) : ℤ) := by push_cast; ring
      rw [this, Int.toNat_natCast]
    omega
  omega

end SLP

/-! ## Part B: trace bound -/

section Trace

/-- Integer `t` with `t² ≤ 4q` is `M`-bad (HYP-eff2cfbb) if `q + 1 - t` has a prime factor `r`
with `r² > 16 q`, `r ∤ q`, and `r ∣ q^m - 1` for some `1 ≤ m ≤ M` (so the order of `q`
modulo `r` is at most `M`). -/
def MBad (q M : ℕ) (t : ℤ) : Prop :=
  t ^ 2 ≤ 4 * q ∧ ∃ r : ℕ, r.Prime ∧ 16 * q < r ^ 2 ∧ ¬ r ∣ q ∧ (r : ℤ) ∣ (q : ℤ) + 1 - t ∧
    ∃ m : ℕ, 1 ≤ m ∧ m ≤ M ∧ r ∣ q ^ m - 1

/-- B1 (HYP-eff2cfbb, step 1): a number `r` with `r² > 16 q` divides `q + 1 - t` for at most
one `t` with `t² ≤ 4q`. -/
theorem trace_unique_of_dvd {q r : ℕ} (hr : 16 * q < r ^ 2) {t t' : ℤ}
    (ht : t ^ 2 ≤ 4 * q) (ht' : t' ^ 2 ≤ 4 * q)
    (h : (r : ℤ) ∣ (q : ℤ) + 1 - t) (h' : (r : ℤ) ∣ (q : ℤ) + 1 - t') : t = t' := by
  have hd : (r : ℤ) ∣ t - t' := by
    have := dvd_sub h' h
    have e : (q : ℤ) + 1 - t' - ((q : ℤ) + 1 - t) = t - t' := by ring
    rwa [e] at this
  have hlt : |t - t'| < (r : ℤ) := by
    apply abs_lt_of_sq_lt_sq _ (by positivity)
    have : (16 : ℤ) * q < (r : ℤ) ^ 2 := by exact_mod_cast hr
    nlinarith [sq_nonneg (t + t')]
  have := Int.eq_zero_of_abs_lt_dvd hd hlt
  omega

/-- B2 (HYP-eff2cfbb, step 2): if `q ≥ 2`, `M ≥ 1`, and `s` is a finite set of primes, each
with `r² > 16 q` and each dividing `∏_{m=1}^{M} (q^m - 1)`, then `s.card < M (M+1)`. -/
theorem card_primes_lt {q M : ℕ} (hq : 2 ≤ q) (hM : 1 ≤ M) (s : Finset ℕ)
    (hp : ∀ r ∈ s, r.Prime) (hr : ∀ r ∈ s, 16 * q < r ^ 2)
    (hdvd : ∀ r ∈ s, r ∣ ∏ m ∈ Finset.Icc 1 M, (q ^ m - 1)) : s.card < M * (M + 1) := by
  set N := ∏ m ∈ Finset.Icc 1 M, (q ^ m - 1) with hN
  have hMpos : 0 < M * (M + 1) := by positivity
  rcases s.eq_empty_or_nonempty with rfl | hne
  · simpa using hMpos
  have hNpos : 0 < N := by
    apply Finset.prod_pos
    intro m hm
    have : 1 ≤ m := (Finset.mem_Icc.mp hm).1
    have : q ^ 1 ≤ q ^ m := Nat.pow_le_pow_right (by omega) this
    simp at this; omega
  have hNle : N ≤ q ^ (∑ m ∈ Finset.Icc 1 M, m) := by
    rw [← Finset.prod_pow_eq_pow_sum]
    exact Finset.prod_le_prod (fun m _ => Nat.sub_le _ _)
  have hsum : ∀ n : ℕ, 2 * ∑ m ∈ Finset.Icc 1 n, m = n * (n + 1) := by
    intro n
    induction n with
    | zero => simp
    | succ n ih => rw [Finset.sum_Icc_succ_top (by omega), mul_add, ih]; ring
  have hprod : ∏ r ∈ s, r ∣ N := Finset.prod_primes_dvd N (fun r hr' => (hp r hr').prime) hdvd
  have hPle : ∏ r ∈ s, r ≤ N := Nat.le_of_dvd hNpos hprod
  have h1 : (16 * q) ^ s.card ≤ ∏ r ∈ s, r ^ 2 :=
    Finset.pow_card_le_prod s (fun r => r ^ 2) (16 * q) (fun r hr' => (hr r hr').le)
  have h2 : ∏ r ∈ s, r ^ 2 = (∏ r ∈ s, r) ^ 2 := Finset.prod_pow _ _ _
  have hk : s.card ≠ 0 := (Finset.card_pos.mpr hne).ne'
  have h3 : q ^ s.card < (16 * q) ^ s.card := Nat.pow_lt_pow_left (by omega) hk
  have h4 : (∏ r ∈ s, r) ^ 2 ≤ (q ^ (∑ m ∈ Finset.Icc 1 M, m)) ^ 2 :=
    Nat.pow_le_pow_left (hPle.trans hNle) 2
  have h5 : (q ^ (∑ m ∈ Finset.Icc 1 M, m)) ^ 2 = q ^ (M * (M + 1)) := by
    rw [← pow_mul, mul_comm, hsum]
  have : q ^ s.card < q ^ (M * (M + 1)) := by
    calc _ < _ := h3
      _ ≤ _ := h1
      _ = _ := h2
      _ ≤ _ := h4
      _ = _ := h5
  exact (Nat.pow_lt_pow_iff_right (by omega)).mp this

/-- Every `M`-bad integer lies in `[-2q, 2q]`, so the set of `M`-bad integers is finite. -/
theorem MBad_finite (q M : ℕ) (hq : 1 ≤ q) : {t : ℤ | MBad q M t}.Finite := by
  apply (Set.finite_Icc (-(2 * q : ℤ)) (2 * q)).subset
  intro t ht
  have h := ht.1
  have hq' : (1 : ℤ) ≤ q := by exact_mod_cast hq
  have h2 : t ^ 2 ≤ (2 * (q : ℤ)) ^ 2 := by nlinarith
  exact Set.mem_Icc.mpr (abs_le_of_sq_le_sq' h2 (by positivity))

/-- B3 (HYP-eff2cfbb, trace bound): for `q ≥ 2`, `M ≥ 1`, the number of `M`-bad integers
`t` (with `t² ≤ 4q`) is at most `M (M + 1)`. -/
theorem card_MBad_le (q M : ℕ) (hq : 2 ≤ q) (hM : 1 ≤ M) :
    {t : ℤ | MBad q M t}.ncard ≤ M * (M + 1) := by
  classical
  set N := ∏ m ∈ Finset.Icc 1 M, (q ^ m - 1) with hN
  have hNpos : 0 < N := by
    apply Finset.prod_pos
    intro m hm
    have : 1 ≤ m := (Finset.mem_Icc.mp hm).1
    have : q ^ 1 ≤ q ^ m := Nat.pow_le_pow_right (by omega) this
    simp at this; omega
  set R : Finset ℕ := N.primeFactors.filter (fun r => 16 * q < r ^ 2) with hR
  have hRcard : R.card < M * (M + 1) := by
    apply card_primes_lt hq hM R
    · intro r hr; exact Nat.prime_of_mem_primeFactors (Finset.mem_filter.mp hr).1
    · intro r hr; exact (Finset.mem_filter.mp hr).2
    · intro r hr; exact Nat.dvd_of_mem_primeFactors (Finset.mem_filter.mp hr).1
  have hex : ∀ t ∈ {t : ℤ | MBad q M t}, ∃ r ∈ R, (r : ℤ) ∣ (q : ℤ) + 1 - t := by
    intro t ht
    obtain ⟨_, r, hrp, hr2, _, hrd, m, hm1, hmM, hrm⟩ := ht
    refine ⟨r, ?_, hrd⟩
    rw [hR, Finset.mem_filter, Nat.mem_primeFactors]
    refine ⟨⟨hrp, ?_, hNpos.ne'⟩, hr2⟩
    exact hrm.trans (Finset.dvd_prod_of_mem (fun m => q ^ m - 1) (Finset.mem_Icc.mpr ⟨hm1, hmM⟩))
  choose! f hfR hfd using hex
  have hfin : ((R : Set ℕ)).Finite := R.finite_toSet
  have := Set.ncard_le_ncard_of_injOn f (fun t ht => hfR t ht) (by
    intro t ht t' ht' h
    have hrR := Finset.mem_filter.mp (hfR t ht)
    refine trace_unique_of_dvd hrR.2 ht.1 ht'.1 (hfd t ht) ?_
    rw [h]; exact hfd t' ht') hfin
  rw [Set.ncard_coe_finset] at this
  omega

end Trace

end MathResearch.ECDLP
