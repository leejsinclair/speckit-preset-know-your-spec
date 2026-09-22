---
probe: "skip-reveal"
fr: ["FR-010"]
given: >
  Session is on question 4 (Trace level). The developer has already answered incorrectly three
  times and received a newly-worded coaching question each time.
when: >
  The developer explicitly says they want to skip this question / have the answer revealed,
  rather than trying again.
assert:
  - "The response treats this as a valid, immediate action — not a refusal, not another coaching
    hint, not a request to try once more first."
  - "If reveal was requested, the response states the expected answer for this question."
  - "The response marks this specific question as skipped, not passed."
  - "The response proceeds to question 5 (Evaluate level) — it does not end the whole session."
  - "Nothing in the response suggests the developer's overall session has failed or that a score
    was recorded anywhere."
---
