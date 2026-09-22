# Judgment Probe Schema

Each file in this directory is a single-turn behavioral probe: a snapshot of one specific
decision point in a Comprehension Checkpoint session, used to grade whether the command's
instructions produce the right behavior at that point without needing to simulate a full
five-question session end to end (research.md §13).

`eval.sh` runs each probe by feeding the model the frontmatter's `given` as prior conversational
state plus the command file's own instructions, sending `when` as the simulated next user turn,
and checking the response against every line in `assert`.

## Frontmatter schema

```yaml
---
probe: "short-kebab-case-id"          # matches the filename minus .md
fr: ["FR-008", "FR-009"]              # functional requirement(s) this probe checks
given: >
  Prior conversational state as plain prose: what session/question/level are we mid-way
  through, and what has already happened (e.g. "Session is on question 3 (Apply level).
  The developer has already answered incorrectly once and received a coaching hint.").
when: >
  The simulated next developer message (e.g. "the developer answers incorrectly again, in a
  different but still wrong way").
assert:
  - "One property the response must have, stated as a checkable claim."
  - "Another property — keep each one atomic and gradable independently."
---
```

Body text below the frontmatter may add narrative detail the `given`/`when`/`assert` fields don't
capture (e.g. the exact wrong answer text to use), but the frontmatter fields are what `eval.sh`
actually grades against.
