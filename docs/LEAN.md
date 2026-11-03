# Lean 4 formal proof environment

Lean 4 is the project's formal mathematics environment for both providers.
`lean-toolchain` pins `leanprover/lean4:v4.35.0`; `lakefile.toml` declares the
shared `MathResearch` library. `MathResearch/Basic.lean` contains only an identity
lemma to check the toolchain. It establishes no factorization or complexity result.

Install [Elan](https://lean-lang.org/install/manual/) if `lake` is unavailable.
Then from repository root:

```sh
lake --version
lean --version
lake build
```

Elan reads the pinned toolchain and downloads it on first use. If installed
without changing shell PATH, invoke `$HOME/.elan/bin/lake` or add that directory
to PATH. The upgrade handoff pins Mathlib 4.35.0 at commit
56a005855ea17e0b0958f73ec801ae140b0a1679, matching Lean 4.35.0. The current
smoke module does not yet import Mathlib or verify ECDLP mathematics. Claude
must implement the serious framework requested in docs/LAB_MISSION.md; review
dependency additions and exact statements before accepting research results.

Keep generic definitions in MathResearch; add project-specific modules under
MathResearch/<Project> and import them from MathResearch.lean so `lake build`
checks them. Avoid `sorry`, `admit`, new axioms and unsafe shortcuts in accepted
proofs. Builds treat warnings as errors. Review `#print axioms <declaration>`;
state and justify any standard logical axioms. CI builds the same pinned project.

A formally verified PRF must specify the exact Lean declaration and source file,
source commit, toolchain file, reproducible command and successful evidence.
A build of the identity smoke check does not verify another theorem. Correctness,
termination and bit-complexity are separate obligations; formalizing functional
correctness alone does not prove O(n log n). Formal verification does not change
the research target's current unproved status.

Sources checked 2026-11-02: [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/),
[Lean 4.35.0 release](https://github.com/leanprover/lean4/releases/tag/v4.35.0).

## Mathlib dependency readiness

MathResearch/MathlibCheck.lean imports the pinned elliptic-curve affine-point
and element-order modules and checks their existing definitions. It is included
in the root library build. This verifies usable dependency imports, not a new
ECDLP theorem. The full reusable framework remains Claude's implementation task.
