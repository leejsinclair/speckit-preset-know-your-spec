---
probe: "coaching-retry"
fr: ["FR-008", "FR-009"]
given: >
  Session is on question 3 (Apply level), derived from spec.md's "Functional Requirements"
  section. The developer has not yet answered.
when: >
  The developer gives an answer that is confidently wrong — it addresses the right topic but
  gets the actual rule backwards (e.g. claims a behavior is optional when the spec's FR states
  it as mandatory).
assert:
  - "The response does not state or paraphrase the full expected answer."
  - "The response names the specific gap in the developer's answer, not just 'incorrect'."
  - "The response points to a specific spec.md heading the developer can go re-read."
  - "The response ends with a new question at the same Apply level, not Recognise/Explain nor
    Trace/Evaluate."
  - "The new question is worded differently from the original question 3 — not a verbatim
    repeat."
  - "Nothing in the response implies an attempt limit or that the developer is about to run out
    of tries."
---
