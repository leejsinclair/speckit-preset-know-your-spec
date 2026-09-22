---
probe: "no-implementation-questions"
fr: ["FR-011"]
given: >
  Fresh session start against a spec.md whose "Assumptions" section happens to mention a
  specific technology choice made elsewhere in the project (e.g. a passing reference to "the
  existing REST API"), even though Spec Kit's own content-quality checklist means spec.md itself
  should be largely implementation-detail-free.
when: >
  The derivation step (Step 1 of the command) runs to produce all five questions before any are
  shown.
assert:
  - "None of the five derived questions ask the developer to name, recall, or reason about a
    specific framework, library, programming language, database schema name, or API endpoint
    definition."
  - "If the only content available at some difficulty level happens to be implementation-
    flavored, the question is still framed at the spec/behavior level (what the system does and
    why), never asking the developer to supply or judge implementation specifics."
  - "This holds independent of whether the developer's own answers later stray into
    implementation detail (that separate case is covered by the out-of-scope-answer probe) —
    this probe is about the system's own generated questions, not the developer's replies."
---
