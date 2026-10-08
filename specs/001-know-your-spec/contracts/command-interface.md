# Command Interface Contract: `speckit.know-your-spec.check`

This is the behavioral contract `commands/speckit.know-your-spec.check.md` must satisfy. It is
the "public API" of this extension in the sense the plan's Phase 1 asks for — there is no
programmatic API, database, or network endpoint; the interface is the command's conversational
behavior against `spec.md` as input and the developer's chat replies as the other party.

## Invocation

- **Automatic**: fires via the mandatory `after_specify` hook, immediately once `/speckit-specify`
  completes (FR-015).
- **Manual**: `/speckit-know-your-spec-check` (or its rendered skill/slash form) or the alias
  `/speckit-kys-check`, runnable on demand against any existing `spec.md` (FR-015).
- **Input**: none required beyond the ambient feature context (`.specify/feature.json` /
  `check-prerequisites.sh` resolution to the active `spec.md`), matching how other Spec Kit
  commands locate their target feature directory.

## Preconditions

- A `spec.md` must be resolvable via `check-prerequisites.sh` for the active feature. If none
  exists, the command must say so plainly and take no further action (it must not fabricate a
  session against a spec that doesn't exist).

## Behavior contract

1. **Derivation phase** (before any question is shown):
   - Privately derive, for each of the five fixed levels (Recognise, Explain, Apply, Trace,
     Evaluate), the question, its expected answer, and the `spec.md` heading supporting it
     (FR-001, FR-002).
   - Every question targets one fact, outcome, or judgment supported by a specific heading and
     has one unambiguous answer. It must not combine ideas, require synthesis across requirements,
     or expect multiple facts in a response (FR-002). Multiple-choice questions have exactly one
     correct option; free-text answers may be paraphrased but express that one answer target.
   - For any level whose supporting content is absent or ambiguous, derive a proposed repair or
     clarification to `spec.md` instead of inventing an untruthful question (FR-003).
   - If any repairs were derived, present them together as one consolidated approval request
     before question 1 (research.md §7). For each:
     - If approved, apply it to `spec.md`, then proceed to derive/ask from the now-established
       content.
     - If declined, substitute a question from different already-established content at that
       level if any exists; if none exists anywhere in the spec, say so plainly for that level
       rather than asking an untruthful question or padding (Edge Cases).

   - **Spec page offer** (after any repair, before question 1 — FR-018): if the helper and
     `python3` are present, ask once whether to open the spec on a page or stay in chat. If the
     page is chosen, start the helper in the background and give the developer its address
     exactly as printed; the command never opens or fetches the address itself (FR-021). If the
     helper or `python3` is missing, skip the offer silently; if the page refuses to start, say
     why in one line. Either way continue to question 1 in chat.

2. **Question loop** (repeated once per level, in fixed order, never regressing — FR-006):
   - Present the question. Format is `multiple-choice` for levels 1-2 only when plausible,
     mutually exclusive options with exactly one correct answer exist; `free-text` otherwise for
     1-2, and always for levels 3-5 (FR-005).
   - Wait for the developer's answer before presenting anything else (FR-004).
   - Judge the answer on semantic understanding, not exact wording (FR-007). An answer that
     strays into implementation detail (code, frameworks, libraries, schema, endpoints) is
     out-of-scope-for-this-checkpoint, not gradable as-is — coach back toward spec-level content
     and re-ask (Edge Cases).
   - If correct/complete: mark the question `passed`, advance to the next level.
   - If incorrect/incomplete: explain the specific gap without revealing the full expected
     answer, point to `source_heading`, and present a newly-worded question at the *same* level
     (FR-008). When the spec page is open, the pointer includes a link to that heading on the
     page (FR-020). Repeat with no attempt limit (FR-009) until the developer either succeeds or
     explicitly invokes skip/reveal for that one question (FR-010), which marks it `skipped` and
     advances to the next level.
   - The developer may exit the session entirely at any point; if they do, the command ends
     immediately with nothing left behind — no partial summary is written anywhere (FR-014).

3. **Completion** (after level 5 is resolved, passed or skipped):
   - Present a concise, session-only completion summary distinguishing passed questions from
     skipped ones (FR-013). This summary is spoken in the conversation only — never written to
     `spec.md` or any other file (FR-012).
   - If the spec page was started, stop it — at completion and on early exit alike (FR-022).

## Postconditions / invariants

- **Non-blocking**: the command's outcome never gates or is required by any other Spec Kit
  command; a project behaves identically at every other stage whether or not this command has
  ever been run (FR-016, SC-004).
- **No bookkeeping persistence**: a repository diff taken after a session contains, at most, an
  approved `spec.md` content repair from step 1 — never questions, answers, scores, or completion
  markers (FR-012, SC-005). The spec page adds or changes nothing in the project (FR-022,
  SC-007).
- **The page changes only where the spec is read**: the questions asked and how they are judged
  are the same with and without it (SC-006).
- **Traceability**: every question actually asked is traceable to specific, established `spec.md`
  content at the moment it was asked (SC-002).
- **No silent advancement**: a level is only ever left via an answer actually judged to
  demonstrate understanding, or an explicit skip/reveal — never silently and never on an
  unaddressed wrong answer (SC-003).
