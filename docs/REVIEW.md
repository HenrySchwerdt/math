# Independent review and integration

The PI assigns a separate reviewer; an author cannot self-approve. The first
packet contains only the exact statement, assumptions, inputs, evidence paths
and candidate commit. Omit the proposing model's confidence and recommendation.
Reviewer writes initial findings before reading the author's assessment.

Every REV JSON uses the shared artifact schema; its report records reviewer
provider/model/RUN, target commit and artifacts, counterexamples attempted,
commands/tests, assumptions checked, separate complexity analysis, scope and
limitations, decision (accept/reject/revise) and rationale. A reviewer can reject
work from any provider, including its own. Unexecuted checks remain unexecuted.

Independent review precedes PI integration review for methodology, hypothesis
and final-result changes. Final review by Sol or Opus records a distinct REV
and exact reviewed commit. Revisions that affect findings require re-review.
Conflicting findings remain linked and unresolved until a reasoned DEC resolves
them; Git merge success is not mathematical agreement. Formal claims additionally
require the exact Lean statement, pinned toolchain and successful build evidence.
