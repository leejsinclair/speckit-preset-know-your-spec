# Feature Specification: Spec Comprehension Check

**Feature Branch**: `001-know-your-spec`

**Created**: 2026-09-22

**Status**: Draft

**Input**: User description: "i want to build a skepkit preset that asks the developer questions about the spec that has just been finished to test their comprehension of it. the questions should start multiple choice and switch to short and then slightly longer. a maximum of 5 questions. the developer should be coached until they get the answer right. refer to /home/lee/projects/proj-1 for how to create a speckit preset"

## Clarifications

### Session 2026-09-22

- Q: When the checkpoint needs to repair or clarify spec.md before asking a question (FR-003), should it tell the developer what it changed, or make the edit silently? → A: Require the developer's explicit approval before applying the repair.
- Q: Must questions 1 and 2 always be multiple-choice, or can the checkpoint use free-text for one of them when the Recognise-level content doesn't lend itself to plausible multiple-choice options? → A: MC when it fits well; free-text otherwise, at the assessor's discretion.
- Q: If a developer can't get a single question right after several retries, should they be able to explicitly skip or reveal just that one question, or is fully exiting the whole session the only way out? → A: Allow an explicit per-question skip/reveal, distinct from exiting the whole session.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Take the comprehension checkpoint on a finished spec (Priority: P1)

A developer has just finished a feature spec (whether they wrote it themselves or an AI assistant
drafted it from their description). Before moving on to planning, they answer five questions
about what the spec actually says, one at a time. Each answer is judged on semantic
understanding, not exact wording. A wrong or incomplete answer gets a coaching hint pointing to
the relevant part of the spec (without revealing the answer) and a newly-worded question at the
same difficulty level; this continues until the developer demonstrates understanding, then the
checkpoint advances.

**Why this priority**: This is the entire point of the feature — without it, there is no
comprehension check at all. Every other story refines this one.

**Independent Test**: Can be fully tested by running the checkpoint against a completed
`spec.md`, answering one question incorrectly, confirming a spec-specific coaching hint is shown
and a newly-worded question at the same difficulty is asked, then answering correctly and
confirming the checkpoint advances to the next difficulty level.

**Acceptance Scenarios**:

1. **Given** a feature spec has just been completed, **When** the developer starts the
   comprehension checkpoint, **Then** the first question is presented in multiple-choice format
   and is based on specific, established content from that spec.
2. **Given** a checkpoint question has been answered incorrectly or incompletely, **When** the
   system evaluates the answer, **Then** the developer sees a coaching hint that explains the
   specific gap and points to the relevant spec heading (without stating the full correct answer)
   and is asked a newly-worded question at the same difficulty level.
3. **Given** a checkpoint question is eventually answered correctly (whether on the first attempt
   or after coaching), **When** the system evaluates the answer, **Then** the checkpoint advances
   to the next difficulty level — a retry never counts as, or replaces, one of the five levels.

---

### User Story 2 - Question difficulty progresses through five fixed levels (Priority: P2)

The checkpoint asks exactly five questions, one per difficulty level, in a fixed increasing
order: Recognise (purpose, a canonical term, or the primary actor), Explain (a documented
user-story relationship, business rule, or happy-path ordering), Apply (the requirements applied
to a concrete scenario), Trace (an edge case, failure condition, or acceptance path through
documented behavior), and Evaluate (reconciling an implication or potential inconsistency across
requirements, scenarios, and success criteria). Questions 1 and 2 are multiple-choice; questions 3
through 5 require a free-text explanation.

**Why this priority**: The requested question progression, and the specific difficulty
structure behind it, is a defining, explicit part of the request; without it this is just an
undifferentiated quiz, not the feature described.

**Independent Test**: Can be fully tested by running a full checkpoint session and confirming the
five questions appear in the fixed Recognise → Explain → Apply → Trace → Evaluate order, with
questions 1-2 multiple-choice and questions 3-5 free-text, and that difficulty never regresses to
an earlier level later in the session.

**Acceptance Scenarios**:

1. **Given** a new checkpoint session starts, **When** the first question is generated and the
   Recognise-level content supports plausible multiple-choice options, **Then** it is presented
   as multiple-choice; **When** that content does not support plausible options, **Then** it is
   presented as a free-text explanation instead.
2. **Given** the checkpoint has advanced past questions 1 and 2, **When** later questions are
   generated, **Then** they always require a free-text explanation and progress through Apply,
   Trace, and Evaluate in that order.
3. **Given** the checkpoint is underway, **When** any question is generated, **Then** its
   difficulty level is never earlier than the level of the question before it.

---

### User Story 3 - The checkpoint never tests information the spec doesn't establish (Priority: P2)

Before asking any question, the answer each question will be judged against — and the spec
heading that supports it — is worked out privately. If the spec lacks the established content
needed to truthfully ask a question at some difficulty level, the spec itself is repaired or
clarified first, so the developer is never quizzed on information the specification never
actually established.

**Why this priority**: Without this, the checkpoint risks penalizing the developer for gaps that
are the spec's fault, not their comprehension — undermining the entire premise of the feature.
It's a prerequisite for Story 1 and 2 producing trustworthy questions.

**Independent Test**: Can be fully tested by running the checkpoint against a spec with a
genuinely thin or ambiguous section and confirming that section is repaired or clarified before
a question is asked from it, rather than a question being asked against absent information.

**Acceptance Scenarios**:

1. **Given** a spec section needed for a given difficulty level is absent or ambiguous, **When**
   the checkpoint prepares its questions, **Then** it proposes a repair or clarification and
   obtains the developer's explicit approval before applying it to `spec.md`, prior to asking the
   corresponding question.
2. **Given** every question has been derived, **When** the developer is asked any question,
   **Then** its expected answer is traceable to specific, established content in `spec.md`.

---

### Edge Cases

- What happens when a developer's free-text answer is factually correct but phrased differently
  than anticipated? Grading must judge semantic understanding, not exact wording.
- What happens when a developer's answer strays into implementation detail (code, frameworks,
  libraries, database schema, endpoint definitions) instead of addressing the spec-level
  question? That is out of scope for this checkpoint (it belongs to planning); the answer should
  be coached back toward spec-level content and re-asked rather than graded as-is.
- What happens when a developer answers the same question incorrectly many times in a row?
  Coaching and retrying continues at that same difficulty level — with a newly-worded question
  each time — for as long as it takes; there is no attempt limit and no automatic reveal, but the
  developer can explicitly ask to skip or reveal that single question at any point without ending
  the session.
- What happens if a developer wants to stop a checkpoint session partway through? They can stop
  at any time; since nothing about the session is ever recorded, there is no partial or failed
  result left behind.
- What happens when the spec lacks the established content needed for a question at some
  difficulty level? See User Story 3 — the spec is repaired or clarified first, not padded
  around, and only after the developer approves that specific repair.
- What happens if the developer declines to approve a needed spec.md repair? The checkpoint asks
  a question from different, already-established spec content for that difficulty level instead;
  if no such alternative content exists anywhere in the spec, the checkpoint says so plainly
  rather than asking an untruthful question or silently padding the session.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST derive every question solely from `spec.md`'s established content
  (its requirements, user stories, edge cases, or success criteria).
- **FR-002**: Before presenting any question, System MUST privately derive that question's
  expected answer and the `spec.md` heading that supports it.
- **FR-003**: If the content needed to truthfully support a question at a given difficulty level
  is absent or ambiguous in `spec.md`, System MUST propose a repair or clarification to `spec.md`
  and obtain the developer's explicit approval before applying it, rather than testing the
  developer on information the spec does not establish or editing `spec.md` without their
  knowledge.
- **FR-004**: System MUST ask exactly five questions per checkpoint session, one at a time,
  waiting for and assessing each answer before presenting the next.
- **FR-005**: System MUST present questions 1 and 2 in multiple-choice format when the
  corresponding Recognise/Explain-level content supports plausible, mutually exclusive options,
  and MUST fall back to a free-text explanation for either of those questions when it does not.
  Questions 3 through 5 MUST always be free-text explanations.
- **FR-006**: System MUST order the five questions by fixed increasing difficulty: Recognise,
  then Explain, then Apply, then Trace, then Evaluate, and MUST never present a question at an
  earlier difficulty level than the question before it.
- **FR-007**: System MUST judge each answer on semantic understanding of the spec's content, not
  on exact wording.
- **FR-008**: When an answer is incorrect or incomplete, System MUST explain the specific gap
  without revealing the complete answer, point the developer to the relevant `spec.md` heading,
  and ask a newly-worded question at the same difficulty level.
- **FR-009**: System MUST continue coaching and retrying at a given difficulty level, with no
  limit on the number of attempts, until the developer demonstrates understanding or explicitly
  invokes the skip/reveal option in FR-010 for that question, before advancing to the next level;
  a retry MUST NOT count as, or replace, one of the five levels.
- **FR-010**: System MUST let the developer explicitly skip or request the answer be revealed for
  a single question they are stuck on, without ending the checkpoint session. A skipped/revealed
  question MUST be recorded, in the session-only completion summary, as skipped rather than
  passed — this is distinct from exiting the entire session (FR-014).
- **FR-011**: System MUST NOT ask about code, frameworks, libraries, database schema names, or
  endpoint definitions — those belong to `plan.md`, not this checkpoint.
- **FR-012**: System MUST keep the checkpoint session-only: it MUST NOT write questions, answers,
  scores, or completion markers to `spec.md` or any other repository file. (This does not
  conflict with FR-003 — an approved repair or clarification of `spec.md`'s own content is a
  distinct action from writing checkpoint bookkeeping to it.)
- **FR-013**: After all five difficulty levels have been concluded (whether passed or skipped),
  System MUST give a concise, session-only completion summary that distinguishes passed
  questions from skipped ones.
- **FR-014**: System MUST allow a developer to exit a checkpoint session before completion at any
  time; since no session state is ever persisted, no partial or failed result can be left behind
  by doing so.
- **FR-015**: System MUST make the comprehension checkpoint available to run automatically
  immediately after a spec is finished via `/speckit-specify`, and MUST also allow the developer
  to run it manually on demand against any existing spec.
- **FR-016**: The comprehension checkpoint MUST be advisory only: it MUST NOT block, or be
  required by, any Spec Kit command (`/speckit-plan`, `/speckit-tasks`, `/speckit-implement`,
  etc.), and a project that has this preset installed but has not run the checkpoint MUST behave
  identically, at every other Spec Kit stage, to a project that does not have it installed at all.
- **FR-017**: System MUST be delivered as an installable Spec Kit preset/extension (its own
  manifest, commands, and hook registration), installable into a Spec Kit project the same way an
  existing precedent extension is installed, rather than as changes hand-made to Spec Kit's own
  files.

### Key Entities

- **Quiz Question**: One of the five questions in a checkpoint session — its text, its format
  (multiple-choice or free-text for levels 1-2, always free-text for levels 3-5), its difficulty
  level (Recognise / Explain / Apply / Trace / Evaluate), the `spec.md` heading it was derived
  from, the privately-derived expected answer used to judge responses, and its outcome (passed /
  skipped). Exists only for the duration of the conversation; never persisted.
- **Comprehension Checkpoint Session**: The developer's single, ephemeral progression through
  the five fixed difficulty levels against one spec, in one sitting — including any retries
  needed to advance past a given level. Never written to any repository file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can complete a full five-question comprehension checkpoint in under 10
  minutes when no more than one or two retries are needed per level.
- **SC-002**: Every question presented in a checkpoint session is traceable to specific,
  established content in the `spec.md` it was generated from — never to absent or ambiguous
  material.
- **SC-003**: In every checkpoint session, a developer advances past a difficulty level only
  after an answer at that level was actually judged to demonstrate understanding, or the
  developer explicitly invoked the skip/reveal option for that question — never silently, and
  never on an incorrect or incomplete answer that wasn't explicitly skipped.
- **SC-004**: A project can install this preset and run every existing Spec Kit command exactly
  as before; the only observable new behavior is the checkpoint itself when explicitly triggered.
- **SC-005**: A repository diff taken after running the checkpoint never contains new questions,
  answers, scores, or completion markers — the only `spec.md` changes possible are content
  repairs/clarifications made before the checkpoint began (FR-003), never checkpoint bookkeeping.

## Assumptions

- The spec being quizzed is the standard `spec.md` produced by Spec Kit's `/speckit-specify`
  command.
- The checkpoint runs inside the same interactive AI coding-assistant session used to author or
  review the spec, so it can read `spec.md` directly and judge free-text answers using its own
  language understanding — no separate grading service or model is introduced.
- "Developer" means the single individual currently working the spec in their own session;
  multi-user or shared checkpoint sessions are out of scope for this feature.
- This feature is delivered using the same Spec Kit extension mechanism (manifest, commands,
  hooks) demonstrated by the reference Questmaster extension (`/home/lee/projects/proj-1`),
  rather than a new delivery mechanism.
- The checkpoint is advisory and never blocks progression to `/speckit-plan` or any other Spec
  Kit command — doubly so here, since it also never persists anything for another command to gate
  on.
