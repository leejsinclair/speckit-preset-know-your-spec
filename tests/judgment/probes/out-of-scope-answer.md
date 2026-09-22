---
probe: "out-of-scope-answer"
fr: ["Edge Cases: answer strays into implementation detail"]
given: >
  Session is on question 2 (Explain level), asking about a documented user-story relationship
  from spec.md.
when: >
  Instead of addressing the spec-level question, the developer answers by describing how they'd
  implement it — naming a specific framework, a database table, or an API endpoint shape.
assert:
  - "The response does not grade this as either correct or incorrect against the expected
    answer — it is treated as not-yet-an-attempt at the actual question."
  - "The response explicitly notes that implementation detail is out of scope for this
    checkpoint (belongs to planning, not this quiz)."
  - "The response coaches the developer back toward spec-level content and re-asks the same
    question at the same (Explain) level."
  - "The response does not use retry/attempt-counting language (e.g. 'that's attempt 2', 'try
    once more', references to a running-out-of-tries limit) — since this redirect isn't a real
    attempt at the spec-level question, nothing about it should be framed as consuming or
    counting toward one of the uncapped retries in FR-009."
---
