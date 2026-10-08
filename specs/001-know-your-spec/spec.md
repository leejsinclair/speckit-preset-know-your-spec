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
order: Recognise (one fact about the purpose, a canonical term, or the primary actor), Explain
(one documented business rule or happy-path ordering), Apply (one requirement applied to a
concrete scenario), Trace (one documented outcome for an edge case, failure condition, or
acceptance path), and Evaluate (one judgment about the clarity or implication of a specific
documented rule). Every question has one unambiguous answer supported by a specific spec heading;
it never combines facts or requires synthesizing multiple ideas. Questions 1 and 2 are
multiple-choice when exactly one correct option is plausible; questions 3 through 5 require a
free-text answer expressing one answer target.

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

### User Story 4 - Read the spec on a page while answering (Priority: P3)

Before the first question, the developer is offered the spec on a page in their browser: the
spec rendered, with every heading a link target and each requirement previewed where it is
referenced. The questions, answers and judging stay in the conversation; the page only changes
where the developer reads. When coaching points at a heading, the pointer is a link to that
heading on the page.

**Why this priority**: The checkpoint is complete without it (Stories 1-3). The page makes the
"go and re-read this section" step of coaching one click, and makes a long spec with diagrams and
cross-references readable — a convenience, not a prerequisite.

**Independent Test**: Can be fully tested by starting a checkpoint, choosing the page, and
confirming the spec is readable at the address given, that a coaching hint links to the right
heading, and that the repository is unchanged after the page stops.

**Acceptance Scenarios**:

1. **Given** a checkpoint is about to ask question 1, **When** the page is available, **Then**
   the developer is asked once whether to open the spec on a page or stay in chat, and is not
   asked again in that session.
2. **Given** the developer chose the page, **When** it starts, **Then** they are given its
   address, and the questions continue in the conversation exactly as in Stories 1-3.
3. **Given** the page is open and an answer is incorrect, **When** coaching points at a spec
   heading, **Then** the pointer includes a link that opens the page at that heading.
4. **Given** the page cannot be offered or cannot start, **When** the checkpoint begins,
   **Then** it proceeds in chat with question 1, and is not delayed or prevented.
5. **Given** a checkpoint that used the page has ended, **When** the repository is compared with
   its state before, **Then** the page has added or changed nothing in it.

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
- What happens when the page cannot be offered (what it needs to run is missing)? The offer is
  skipped without comment and the checkpoint runs in chat, exactly as without this story.
- What happens when the page cannot start (for example no free port)? The developer is told why
  in one line and the checkpoint carries on in chat.
- What happens when `spec.md` changes while the page is open (an approved repair, or an edit)?
  The page says the spec has changed and offers to reload; it does not change under the reader.
- What happens when the spec contains a diagram and the diagram cannot be drawn (no internet
  connection, or a diagram with an error in it)? The diagram's source is shown in its place.
- What happens when someone other than the developer reaches the page's port? Without the
  one-time key in the address they are refused and see none of the spec.
- What happens if the developer's temporary folder is inside the project? The page keeps its
  running-state file somewhere outside the project instead, and if there is no such place it
  does not start (and the checkpoint carries on in chat).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST derive every question solely from `spec.md`'s established content
  (its requirements, user stories, edge cases, or success criteria).
- **FR-002**: Before presenting any question, System MUST privately derive one unambiguous expected
  answer and the specific `spec.md` heading that supports it. Each question MUST target one fact,
  outcome, or judgment; MUST NOT be compound, combine separate requirements or ideas, or require
  synthesizing multiple facts. The expected answer MUST contain only that answer target, and a
  free-text response MUST NOT be expected to supply additional facts.
- **FR-003**: If the content needed to truthfully support a question at a given difficulty level
  is absent or ambiguous in `spec.md`, System MUST propose a repair or clarification to `spec.md`
  and obtain the developer's explicit approval before applying it, rather than testing the
  developer on information the spec does not establish or editing `spec.md` without their
  knowledge.
- **FR-004**: System MUST ask exactly five questions per checkpoint session, one at a time,
  waiting for and assessing each answer before presenting the next.
- **FR-005**: System MUST present questions 1 and 2 in multiple-choice format when the
  corresponding Recognise/Explain-level content supports plausible, mutually exclusive options,
  with exactly one correct option, and MUST fall back to a free-text answer for either of those
  questions when it does not. Questions 3 through 5 MUST always be free-text answers.
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
- **FR-018**: Before question 1, and after any approved repair, System MUST offer once per
  session to show `spec.md` on a page in the developer's browser. When what the page needs to
  run is missing, System MUST skip the offer silently; when the page cannot start, System MUST
  say why in one line; in both cases the checkpoint proceeds in chat (FR-016).
- **FR-019**: The page MUST be read-only: it MUST show `spec.md` as it currently is on disk and
  MUST NOT offer any way to change `spec.md` or to record anything about the session. The
  questions, answers and judging MUST stay in the conversation.
- **FR-020**: The page MUST render the spec with every heading as a link target and with each
  reference to a requirement the spec defines showing that requirement in place. When the page
  is open, a coaching pointer to a spec heading (FR-008) MUST include a link to that heading.
- **FR-021**: The page MUST be reachable only with the address given to the developer, which
  carries a one-time key; a request without the key MUST be refused and shown none of the spec.
  The page MUST be reachable through a port forwarded to the developer's own machine.
- **FR-022**: Running the page MUST NOT add or change any file in the project (FR-012). Any
  running-state it keeps MUST be outside the project and removed when the page stops. The page
  MUST stop when the checkpoint ends, and on its own after a period without use.
- **FR-023**: The page MUST draw the spec's diagrams. A page whose spec has no diagram MUST load
  nothing from outside the developer's machine; a page whose spec has one MAY load a single
  diagram-drawing script, and MUST show the diagram's source when it cannot be drawn.
- **FR-024**: The page MUST tell the reader when `spec.md` has changed since the page was loaded
  and offer to reload, and MUST tell the reader when the page has stopped.

### Key Entities

- **Quiz Question**: One of the five questions in a checkpoint session — its text, its format
  (multiple-choice or free-text for levels 1-2, always free-text for levels 3-5), its difficulty
  level (Recognise / Explain / Apply / Trace / Evaluate), the `spec.md` heading it was derived
  from, the privately-derived expected answer used to judge responses, and its outcome (passed /
  skipped). Exists only for the duration of the conversation; never persisted.
- **Comprehension Checkpoint Session**: The developer's single, ephemeral progression through
  the five fixed difficulty levels against one spec, in one sitting — including any retries
  needed to advance past a given level. Never written to any repository file.
- **Spec Page**: An optional, read-only view of one `spec.md` in the developer's browser, alive
  for at most one checkpoint session — its address (with a one-time key) and the link target of
  each heading. Holds nothing about the session; leaves nothing in the project.

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
- **SC-006**: A checkpoint run with the page and a checkpoint run without it ask the same
  questions and judge them the same way; the page changes only where the spec is read.
- **SC-007**: After a checkpoint that used the page, the project's files are identical to what
  they would be had the page not been used, and no page is left running.
- **SC-008**: With the page open, a developer coached toward a spec heading reaches that heading
  in one click.

## Assumptions

- The spec being quizzed is the standard `spec.md` produced by Spec Kit's `/speckit-specify`
  command.
- The checkpoint runs inside the same interactive AI coding-assistant session used to author or
  review the spec, so it can read `spec.md` directly and judge free-text answers using its own
  language understanding — no separate grading service or model is introduced.
- The spec page (User Story 4) is optional and needs a scripting runtime commonly present on a
  developer's machine; where it is absent the checkpoint is unaffected. Drawing a diagram needs
  an internet connection; nothing else about the page does.
- "Developer" means the single individual currently working the spec in their own session;
  multi-user or shared checkpoint sessions are out of scope for this feature.
- This feature is delivered using the same Spec Kit extension mechanism (manifest, commands,
  hooks) demonstrated by the reference Questmaster extension (`/home/lee/projects/proj-1`),
  rather than a new delivery mechanism.
- The checkpoint is advisory and never blocks progression to `/speckit-plan` or any other Spec
  Kit command — doubly so here, since it also never persists anything for another command to gate
  on.
