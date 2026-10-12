---
probe: "after-clarify-start"
fr: ["FR-025", "FR-028"]
given: >
  The command has just been started by the after_clarify hook at the end of a /speckit-clarify
  run that asked no questions because the spec was already clear. Step 0 read spec.md from disk.
  Step 1 is finished: it found no repairs and derived all five questions. The spec page helper is
  not installed. Nothing has been shown to the developer yet. The derived question 1 (Recognise
  level, multiple choice) is "Which of these is the primary purpose of the feature?" with the
  options "A. Quiz the developer on a finished spec", "B. Generate a plan from the spec",
  "C. Rewrite the spec for clarity", "D. Track which developers have read the spec".
when: >
  The developer has sent nothing since /speckit-clarify ended.
assert:
  - "The response presents question 1 at the Recognise level, with its options."
  - "The response does not ask whether to run the checkpoint and does not wait for confirmation."
  - "The response does not say there is nothing to check, or that the checkpoint is skipped
    because nothing changed."
  - "The response does not present question 2 or any hint before the developer answers."
---
