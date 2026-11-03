module

public import MathResearch.ECDLP.LinearInterp
public import Mathlib.Algebra.Polynomial.Eval.Defs

/-!
# ECDLP: algebraic straight-line-program lower bound for x-only discrete-log computation

Ledger: research/ecdlp, task ECDLP-32 (TSK-af4a7113-a8c4-49df-9099-2b7d7f648846),
RUN-e44599c2-9911-4297-898b-8950066b8adf, hypothesis HYP-92a9b4d9-827b-45fc-b881-1e7cf3b3443b.

**Model.** A program over a commutative ring `F` is a list of `Op`s with a single input variable
`x`. Each op appends one value: a constant of `F` (constants are free), the input `x`, or the sum,
difference or product of two earlier values (indices out of range read `0`). It is division-free,
has no comparisons or branching, and the only input is the single scalar `x = x(Q)`.

**What is proved.** Step `i` has polynomial degree `≤ 2 ^ (i+1)` (hence every value is a polynomial
of degree `≤ 2 ^ length` in `x`), and combined with the formally verified
`CurveX.degree_bound_linear_short_weierstrass` (Theorem C): a program of length `L` computing `k`
at `x(kP)` for `1 ≤ k ≤ N`, `2 N < r`, forces `N ≤ 3 * 2 ^ L + 2`.

**What is NOT formalized.** Any bit-complexity consequence (e.g. cost `≥ c log p` per field
operation, hence `Ω(n²)` bit operations). That is a cost-model remark outside this file.
Lower bounds here are on the number of ring operations in this restricted model only.
-/

@[expose] public section

namespace MathResearch.ECDLP

open Polynomial

namespace SLPBound

/-- One instruction of a division-free straight-line program in one variable. -/
inductive Op (F : Type*) where
  | const (c : F)
  | var
  | add (i j : ℕ)
  | sub (i j : ℕ)
  | mul (i j : ℕ)

section Run

variable {F R : Type*} [CommRing F] [CommRing R]

/-- Semantics of one op in `R` given the values `acc` computed so far, a ring map `φ : F →+* R`
interpreting constants and the value `x` of the input. Out-of-range indices read `0`. -/
def stepVal (φ : F →+* R) (x : R) (acc : List R) : Op F → R
  | .const c => φ c
  | .var => x
  | .add i j => acc.getD i 0 + acc.getD j 0
  | .sub i j => acc.getD i 0 - acc.getD j 0
  | .mul i j => acc.getD i 0 * acc.getD j 0

/-- The list of all values computed (one per op). -/
def run (φ : F →+* R) (x : R) (prog : List (Op F)) : List R :=
  prog.foldl (fun acc o => acc ++ [stepVal φ x acc o]) []

/-- Polynomial semantics: the polynomial in the input computed by each step. -/
noncomputable def evalPoly (prog : List (Op F)) : List F[X] := run Polynomial.C Polynomial.X prog

/-- Value semantics: run the program at the input value `u : F`. -/
def evalAt (prog : List (Op F)) (u : F) : List F := run (RingHom.id F) u prog

private lemma run_aux_map {S : Type*} [CommRing S] (ψ : R →+* S) (φ : F →+* R) (x : R)
    (prog : List (Op F)) (acc : List R) :
    (prog.foldl (fun a o => a ++ [stepVal φ x a o]) acc).map ψ =
      prog.foldl (fun a o => a ++ [stepVal (ψ.comp φ) (ψ x) a o]) (acc.map ψ) := by
  induction prog generalizing acc with
  | nil => rfl
  | cons o rest ih =>
    simp only [List.foldl_cons]
    rw [ih, List.map_append]
    congr 2
    have hget : ∀ i : ℕ, ψ (acc.getD i 0) = (acc.map ψ).getD i 0 := by
      intro i
      simp only [List.getD_eq_getElem?_getD, List.getElem?_map]
      cases acc[i]? <;> simp
    cases o with
    | const c => simp [stepVal]
    | var => simp [stepVal]
    | add i j => simp only [stepVal, map_add, hget, List.map_cons, List.map_nil]
    | sub i j => simp only [stepVal, map_sub, hget, List.map_cons, List.map_nil]
    | mul i j => simp only [stepVal, map_mul, hget, List.map_cons, List.map_nil]

/-- Ring maps commute with running a program. -/
theorem run_map {S : Type*} [CommRing S] (ψ : R →+* S) (φ : F →+* R) (x : R)
    (prog : List (Op F)) :
    (run φ x prog).map ψ = run (ψ.comp φ) (ψ x) prog := by
  have := run_aux_map ψ φ x prog []
  simpa [run] using this

/-- Evaluating each step polynomial at `u` equals running the program at `u`. -/
theorem evalPoly_map_eval (prog : List (Op F)) (u : F) :
    (evalPoly prog).map (Polynomial.eval u) = evalAt prog u := by
  have h := run_map (Polynomial.evalRingHom u) (Polynomial.C : F →+* F[X]) Polynomial.X prog
  have e : (Polynomial.evalRingHom u).comp (Polynomial.C : F →+* F[X]) = RingHom.id F := by
    ext; simp
  rw [e] at h
  simpa [evalPoly, evalAt] using h

/-- Pointwise form: the `i`-th value at `u` is the `i`-th step polynomial evaluated at `u`. -/
theorem evalAt_getD (prog : List (Op F)) (u : F) (i : ℕ) :
    (evalAt prog u).getD i 0 = ((evalPoly prog).getD i 0).eval u := by
  rw [← evalPoly_map_eval]
  simp only [List.getD_eq_getElem?_getD, List.getElem?_map]
  cases (evalPoly prog)[i]? <;> simp

private lemma run_aux_deg (prog : List (Op F)) :
    ∀ (acc : List F[X]),
      (∀ p ∈ acc, p.natDegree ≤ 2 ^ acc.length) →
      ∀ p ∈ prog.foldl (fun a o => a ++ [stepVal Polynomial.C Polynomial.X a o]) acc,
        p.natDegree ≤ 2 ^ (acc.length + prog.length) := by
  induction prog with
  | nil => intro acc h p hp; simpa using h p hp
  | cons o rest ih =>
    intro acc h p hp
    have hget : ∀ i : ℕ, (acc.getD i 0).natDegree ≤ 2 ^ acc.length := by
      intro i
      by_cases hi : i < acc.length
      · have : acc.getD i 0 ∈ acc := by
          rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]
          exact List.getElem_mem hi
        exact h _ this
      · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
        simp
    have hpow : 2 ^ acc.length ≤ 2 ^ (acc.length + 1) :=
      pow_le_pow_right₀ (by norm_num) (by omega)
    have hone : 1 ≤ 2 ^ (acc.length + 1) := Nat.one_le_two_pow
    have key : ∀ q ∈ acc ++ [stepVal Polynomial.C Polynomial.X acc o],
        q.natDegree ≤ 2 ^ (acc ++ [stepVal Polynomial.C Polynomial.X acc o]).length := by
      intro q hq
      rw [List.length_append, List.length_singleton]
      rcases List.mem_append.mp hq with hq | hq
      · exact (h q hq).trans hpow
      · have hq' : q = stepVal Polynomial.C Polynomial.X acc o := by simpa using hq
        subst hq'
        have h2 : 2 ^ (acc.length + 1) = 2 ^ acc.length + 2 ^ acc.length := by ring
        cases o with
        | const c => simp [stepVal]
        | var => simpa [stepVal] using (natDegree_X_le (R := F)).trans hone
        | add i j =>
          simp only [stepVal]
          exact (natDegree_add_le _ _).trans (max_le ((hget i).trans hpow) ((hget j).trans hpow))
        | sub i j =>
          simp only [stepVal]
          exact (natDegree_sub_le _ _).trans (max_le ((hget i).trans hpow) ((hget j).trans hpow))
        | mul i j =>
          simp only [stepVal]
          rw [h2]
          exact (natDegree_mul_le).trans (add_le_add (hget i) (hget j))
    have := ih _ key p hp
    simpa [List.length_append, List.length_cons, Nat.add_assoc, Nat.add_comm 1] using this

/-- **Degree lemma.** Every step polynomial of a program of length `L` has `natDegree ≤ 2 ^ L`. -/
theorem natDegree_le_of_mem {prog : List (Op F)} {p : F[X]} (hp : p ∈ evalPoly prog) :
    p.natDegree ≤ 2 ^ prog.length := by
  have := run_aux_deg prog [] (by simp) p hp
  simpa using this

/-- Any (possibly out-of-range, reading `0`) output index has degree `≤ 2 ^ L`. -/
theorem natDegree_getD_le (prog : List (Op F)) (i : ℕ) :
    ((evalPoly prog).getD i 0).natDegree ≤ 2 ^ prog.length := by
  by_cases hi : i < (evalPoly prog).length
  · apply natDegree_le_of_mem
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]
    exact List.getElem_mem hi
  · rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]
    simp

end Run

open WeierstrassCurve WeierstrassCurve.Affine CurveX

variable {F : Type*} [Field F] [DecidableEq F]

/-- **Main theorem (algebraic SLP barrier, x-only, division-free).** `W` short Weierstrass over a
field `F` with `2 ≠ 0`, `P` of order `r`, `2 N < r`. If the `i`-th output of the program `prog`
(division-free, single input `u`, constants free) equals `k` in `F` when run at `u = x(kP)`, for all
`1 ≤ k ≤ N`, then `N ≤ 3 * 2 ^ prog.length + 2`, i.e. `prog.length ≥ log₂ ((N - 2) / 3)`.
Only a statement about the number of ring operations; no bit-cost claim. -/
theorem length_bound_linear_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (prog : List (Op F)) (i : ℕ)
    (hprog : ∀ k : ℕ, 1 ≤ k → k ≤ N → (evalAt prog (xCoord (k • P))).getD i 0 = (k : F)) :
    N ≤ 3 * 2 ^ prog.length + 2 := by
  have hg : ∀ k : ℕ, 1 ≤ k → k ≤ N →
      ((evalPoly prog).getD i 0).eval (xCoord (k • P)) = (k : F) := by
    intro k hk hk'
    rw [← evalAt_getD]
    exact hprog k hk hk'
  have := degree_bound_linear_short_weierstrass h1 h2 h3 h2' P r hr N hN _ hg
  have := natDegree_getD_le prog i
  omega

/-- Polynomial-output form of the main theorem: `g` is any step polynomial of `prog`. -/
theorem length_bound_linear_of_mem {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (N : ℕ) (hN : 2 * N < r) (prog : List (Op F)) (g : F[X]) (hgm : g ∈ evalPoly prog)
    (hg : ∀ k : ℕ, 1 ≤ k → k ≤ N → g.eval (xCoord (k • P)) = (k : F)) :
    N ≤ 3 * 2 ^ prog.length + 2 := by
  have := degree_bound_linear_short_weierstrass h1 h2 h3 h2' P r hr N hN g hg
  have := natDegree_le_of_mem hgm
  omega

/-- Order form for odd `r`: outputting `k` at `x(kP)` for `1 ≤ k ≤ (r-1)/2` needs
`r ≤ 6 * 2 ^ length + 5`. -/
theorem length_bound_linear_order {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (P : W.Point) (r : ℕ) (hr : addOrderOf P = r)
    (hodd : r % 2 = 1) (prog : List (Op F)) (i : ℕ)
    (hprog : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 →
      (evalAt prog (xCoord (k • P))).getD i 0 = (k : F)) :
    r ≤ 6 * 2 ^ prog.length + 5 := by
  have := length_bound_linear_short_weierstrass h1 h2 h3 h2' P r hr ((r - 1) / 2) (by omega)
    prog i hprog
  omega

/-- The `k²` variant (Theorem B): outputting `k²` at `x(kP)` for `1 ≤ k ≤ (r-1)/2`, `r` odd,
`2, 3 ≠ 0`, needs `r ≤ 6 * 2 ^ length + 5`. -/
theorem length_bound_sq_short_weierstrass {W : Affine F} (h1 : W.a₁ = 0) (h2 : W.a₂ = 0)
    (h3 : W.a₃ = 0) (h2' : (2 : F) ≠ 0) (h3' : (3 : F) ≠ 0) (P : W.Point) (r : ℕ)
    (hr : addOrderOf P = r) (hodd : r % 2 = 1) (prog : List (Op F)) (i : ℕ)
    (hprog : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 →
      (evalAt prog (xCoord (k • P))).getD i 0 = (k : F) ^ 2) :
    r ≤ 6 * 2 ^ prog.length + 5 := by
  have hg : ∀ k : ℕ, 1 ≤ k → k ≤ (r - 1) / 2 →
      ((evalPoly prog).getD i 0).eval (xCoord (k • P)) = (k : F) ^ 2 := by
    intro k hk hk'
    rw [← evalAt_getD]
    exact hprog k hk hk'
  have := degree_bound_short_weierstrass h1 h2 h3 h2' h3' P r hr hodd _ hg
  have := natDegree_getD_le prog i
  omega

end SLPBound

end MathResearch.ECDLP
