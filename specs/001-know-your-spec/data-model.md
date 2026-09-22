# Phase 1 Data Model: Spec Comprehension Check

Both entities below are conversational/ephemeral only — per FR-012 and SC-005, neither is ever
serialized to `spec.md` or any other repository file. This model documents their shape purely to
pin down what the command's instructions must track *in-session* (i.e., in the running
conversation's own working state) to satisfy the functional requirements; it is not a database or
file schema.

## Quiz Question

One of the five questions asked in a single checkpoint session.

| Field | Type | Description | Source FR |
|---|---|---|---|
| `level` | enum: `Recognise` \| `Explain` \| `Apply` \| `Trace` \| `Evaluate` | Fixed difficulty level, strictly increasing across the session, never regressing. | FR-006 |
| `format` | enum: `multiple-choice` \| `free-text` | `Recognise`/`Explain` (questions 1-2) are `multiple-choice` when the underlying content supports plausible, mutually exclusive options, else `free-text`. `Apply`/`Trace`/`Evaluate` (questions 3-5) are always `free-text`. | FR-005 |
| `text` | string | The question as presented to the developer. Re-worded on each retry at the same level — never the same phrasing twice in a row. | FR-008 |
| `source_heading` | string | The specific `spec.md` heading the question is derived from. Must exist and be traceable — never invented. | FR-001, FR-002, SC-002 |
| `expected_answer` | string (private) | Derived before the question is presented; never shown to the developer, even on failure — only a coaching hint pointing at `source_heading` is shown. | FR-002, FR-008 |
| `attempts` | integer | Count of incorrect/incomplete attempts at this level so far in the session. Uncapped — no maximum enforced. | FR-009 |
| `outcome` | enum: `passed` \| `skipped` | `passed` once an answer is judged to demonstrate understanding; `skipped` if the developer explicitly invokes the skip/reveal option instead. Never silently advanced. | FR-010, SC-003 |

**Lifecycle**: created when its difficulty level is reached → held in-session through zero or more
re-worded retries at the same level → resolved to `passed` or `skipped` → session advances to the
next level (or ends, at question 5). Never instantiated outside a running checkpoint session;
discarded when the conversation ends.

**Validation rules**:
- `source_heading` must reference content that exists in `spec.md` at question-presentation time
  (after any approved repairs — see User Story 3 / FR-003).
- A question's `level` must never be earlier than the `level` of the question immediately before
  it in the same session (FR-006, SC-003).
- `format` is `free-text` unconditionally for `level` in `{Apply, Trace, Evaluate}`; conditional
  on content shape for `level` in `{Recognise, Explain}` (FR-005).

## Comprehension Checkpoint Session

The developer's single, ephemeral progression through all five difficulty levels against one
`spec.md`, in one sitting.

| Field | Type | Description | Source FR |
|---|---|---|---|
| `target_spec` | path | The `spec.md` this session is checking comprehension of. | Assumptions |
| `questions` | ordered list of up to 5 Quiz Question | One per difficulty level, in fixed `Recognise → Explain → Apply → Trace → Evaluate` order. Shorter than 5 only if the developer exits early (FR-014). | FR-004, FR-006 |
| `pending_repairs` | list of proposed `spec.md` edits | Derived upfront (before question 1) wherever a difficulty level's needed content is absent or ambiguous; each entry requires explicit developer approval before being applied, and before the corresponding question is asked. If declined, the session must either substitute already-established alternative content for that level or say plainly that none exists — never ask an untruthful question or silently pad. | FR-003, User Story 3, Edge Cases |
| `status` | enum: `in-progress` \| `completed` \| `exited-early` | `completed` once all 5 levels are resolved (passed or skipped); `exited-early` if the developer stops before that; never a `failed` status, since nothing is graded pass/fail at the session level. | FR-013, FR-014 |

**Lifecycle**: begins either automatically (mandatory `after_specify` hook) or manually
(on-demand command invocation) → `pending_repairs` derived and resolved (approved/declined) →
questions asked and resolved one at a time in fixed order → ends in `completed` (with a
passed/skipped summary per FR-013) or `exited-early` (no summary persisted, nothing left behind
per FR-014) → the entire session state is discarded when the conversation ends; nothing survives
to a next run.

**Validation rules**:
- Exactly one session's worth of state exists at a time — no concurrent/interleaved sessions
  (Assumptions: single individual, no multi-user scenario).
- `questions` length is always ≤ 5; a `completed` session has exactly 5.
- No field of either entity is ever written to `spec.md` or any other repository file. The only
  repository mutation this feature can ever produce is an *approved* `pending_repairs` edit
  applied to `spec.md` itself — that edit becomes part of `spec.md`'s own content, not checkpoint
  bookkeeping (FR-012's parenthetical).
