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
to PATH. No Mathlib dependency is needed for the bootstrap smoke check. Add
Mathlib at a compatible pinned revision with its manifest when a proof needs it;
record this dependency change in a DEC and review it before integration.

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
