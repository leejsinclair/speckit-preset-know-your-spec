---
probe: "repair-approval"
fr: ["FR-003", "Edge Cases: developer declines a needed repair"]
given: >
  Derivation (Step 1) has just finished for a spec.md where the Trace-level section is genuinely
  thin — no documented edge case or failure condition exists to truthfully derive a question
  from. Question 1-3 (Recognise/Explain/Apply) derived cleanly with no issues. Session has not
  yet shown anything to the developer.
when: >
  The command proceeds to Step 2 (propose repairs before question 1), and then the developer
  responds twice, in two separate branches: (a) approves the proposed repair, and (b) declines
  it, where the spec happens to have one alternative already-established Trace-level-suitable
  detail elsewhere (an acceptance scenario edge case) the checkpoint could use instead.
assert:
  - "The repair proposal is presented once, before question 1 — not interleaved between earlier
    questions, and not silently applied without being shown first."
  - "Branch (a): after approval, the response confirms the edit was applied to spec.md, and the
    eventual Trace-level question is derived from the newly-established content."
  - "Branch (b): after decline, spec.md is not modified. The response derives the Trace-level
    question from the alternative already-established content instead, without necessarily
    narrating the swap to the developer."
  - "In neither branch does the response ask an untruthful question or pad the session with
    something not traceable to spec.md."
  - "A variant where NO alternative content exists anywhere for that level: the response states
    this plainly when that level is reached, rather than asking an untruthful question."
---
