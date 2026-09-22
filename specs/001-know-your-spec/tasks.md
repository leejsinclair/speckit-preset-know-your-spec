---

description: "Task list for the Spec Comprehension Check extension"
---

# Tasks: Spec Comprehension Check

**Input**: Design documents from `/specs/001-know-your-spec/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Explicitly requested — full two-tier investment (deterministic + judgment), per
research.md §10. No governance tier (research.md §11).

**Organization**: Tasks are grouped by user story (spec.md P1/P2/P2) so each can be implemented
and tested independently. Every implementation task in US1/US2/US3 edits the same single command
file (`commands/speckit.know-your-spec.check.md`) — this extension has one command, so "different
files" parallelism within a story phase applies to test/fixture files, not the command file
itself.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single flat-at-root Spec Kit extension package (plan.md § Project Structure):
`extension.yml`, `commands/`, `tests/` at the repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository and package scaffolding, no behavior yet.

- [X] T001 Create the flat-at-root extension package skeleton (`commands/`, `tests/deterministic/`, `tests/judgment/fixtures/`, `tests/judgment/expected/`, `tests/judgment/probes/`) per plan.md § Project Structure
- [X] T002 Initialize git locally at the repository root (no remote yet — research.md §8)
- [X] T003 [P] Write `.extensionignore` at the repository root excluding `specs/`, `tests/`, `.specify/`, `.claude/`, `.gitignore` (research.md §9)

**Checkpoint**: Repo scaffolding exists; nothing installable yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest and command skeleton every user story's behavior gets layered onto.

**⚠️ CRITICAL**: No user story task can begin until this phase is complete.

- [X] T004 Write `extension.yml` at the repository root per `contracts/extension.yml`: id `know-your-spec`, command `speckit.know-your-spec.check` with alias `speckit.kys-check`, mandatory (`optional: false`) `after_specify` hook, no config/templates/scripts entries
- [X] T005 Create `commands/speckit.know-your-spec.check.md` with required frontmatter only (`description`) and a placeholder body, so `specify extension add --dev` can install it for iterative testing

**Checkpoint**: `specify extension add --dev <repo>` succeeds and registers the command + hook; the command does nothing useful yet.

---

## Phase 3: User Story 1 - Take the comprehension checkpoint on a finished spec (Priority: P1) 🎯 MVP

**Goal**: One question at a time, semantically judged, coached-and-retried with no cap, explicit skip/reveal, session-only completion summary, clean early exit.

**Independent Test**: Run the checkpoint against a completed `spec.md`, answer one question incorrectly, confirm a spec-specific coaching hint (no answer reveal) plus a newly-worded question at the same difficulty, then answer correctly and confirm advancement (spec.md's own Independent Test for this story).

- [X] T006 [US1] Author core question-loop instructions in `commands/speckit.know-your-spec.check.md`: locate `spec.md` via `check-prerequisites.sh`, present exactly one question at a time, wait for the developer's reply before continuing, judge on semantic understanding not exact wording (FR-004, FR-007)
- [X] T007 [US1] Add coaching-and-uncapped-retry logic to `commands/speckit.know-your-spec.check.md`: on an incorrect/incomplete answer, explain the specific gap without revealing the full answer, point to the relevant `spec.md` heading, present a newly-worded question at the same level, with no attempt limit (FR-008, FR-009)
- [X] T008 [US1] Add the explicit per-question skip/reveal option to `commands/speckit.know-your-spec.check.md`, recorded as `skipped` (not `passed`) and distinct from ending the whole session (FR-010)
- [X] T009 [US1] Add the session-only completion summary to `commands/speckit.know-your-spec.check.md`: after all five levels are resolved, report passed vs. skipped questions in the conversation only (FR-013, FR-012)
- [X] T010 [US1] Add early-exit handling to `commands/speckit.know-your-spec.check.md`: the developer can stop at any time, and since nothing is ever persisted there is no partial state to clean up (FR-014)
- [X] T011 [P] [US1] Write `tests/deterministic/test-command-manifest.sh` asserting `extension.yml` and `commands/speckit.know-your-spec.check.md` structure: primary command name matches `speckit.know-your-spec.check`, alias present, `after_specify` hook has `optional: false`, frontmatter `description` non-empty
- [X] T012 [US1] Add `tests/judgment/fixtures/own-spec/spec.md` — this repository's own finished `spec.md`, as fixture 1
- [X] T013 [US1] Author `tests/judgment/expected/own-spec.json` — hand-authored ground truth (5 questions, expected answers, source headings) for fixture 1, derived from spec.md's FRs (research.md §14: authored solely by the extension author, no separate review pass)
- [X] T014 [P] [US1] Write `tests/judgment/probes/coaching-retry.md` — single-turn behavioral probe: given a wrong/incomplete answer mid-session, confirm a coaching hint with no answer reveal and a reworded same-level question (FR-008, FR-009)
- [X] T015 [P] [US1] Write `tests/judgment/probes/skip-reveal.md` — single-turn probe confirming an explicit skip/reveal request marks the question `skipped` and advances without ending the session (FR-010)
- [X] T016 [P] [US1] Write `tests/judgment/probes/out-of-scope-answer.md` — single-turn probe confirming an answer that strays into implementation detail (code/frameworks/schema/endpoints) is coached back to spec-level content and re-asked rather than graded as-is (FR-011, Edge Cases). **Extended per /speckit-analyze finding E1**: FR-011 itself (the system never generating an implementation-detail question) is a distinct guarantee from this edge case (a developer's answer straying) — a second probe, `tests/judgment/probes/no-implementation-questions.md`, was added to cover FR-011 directly.

**Checkpoint**: User Story 1 is independently functional and testable — a single-level (or spec-content-permitting five-level) coached comprehension loop works end to end against a real spec.

---

## Phase 4: User Story 2 - Question difficulty progresses through five fixed levels (Priority: P2)

**Goal**: Exactly five questions in fixed Recognise → Explain → Apply → Trace → Evaluate order, never regressing; Q1-2 multiple-choice when plausible, free-text otherwise; Q3-5 always free-text.

**Independent Test**: Run a full checkpoint session and confirm the fixed five-level order, the Q1-2 format rule, and that difficulty never regresses (spec.md's own Independent Test for this story).

- [X] T017 [US2] Add the fixed five-level difficulty structure and strict non-regression ordering to `commands/speckit.know-your-spec.check.md`: Recognise, Explain, Apply, Trace, Evaluate (FR-006)
- [X] T018 [US2] Add conditional multiple-choice/free-text format logic for questions 1-2 to `commands/speckit.know-your-spec.check.md` (multiple-choice only when plausible, mutually exclusive options exist; free-text otherwise), and always-free-text for questions 3-5 (FR-005)
- [X] T019 [P] [US2] Add `tests/judgment/fixtures/mc-unfriendly/spec.md` — a synthetic spec whose Recognise/Explain-level content doesn't support plausible multiple-choice distractors
- [X] T020 [US2] Author `tests/judgment/expected/mc-unfriendly.json` — ground truth confirming the free-text fallback fires for questions 1-2 against fixture `mc-unfriendly`

**Checkpoint**: User Stories 1 AND 2 both work independently — the full five-level structure and format rule are verified on top of the US1 question/coaching loop.

---

## Phase 5: User Story 3 - The checkpoint never tests information the spec doesn't establish (Priority: P2)

**Goal**: Every question's expected answer and source heading are derived privately before it's asked; absent/ambiguous content triggers a developer-approved repair first, with a graceful decline path.

**Independent Test**: Run the checkpoint against a spec with a genuinely thin or ambiguous section and confirm that section is repaired/clarified (with explicit approval) before a question is asked from it (spec.md's own Independent Test for this story).

- [X] T021 [US3] Add private derivation-before-asking to `commands/speckit.know-your-spec.check.md`: for every level, derive the expected answer and supporting `spec.md` heading before presenting the question (FR-002)
- [X] T022 [US3] Add the repair-proposal-and-approval flow to `commands/speckit.know-your-spec.check.md`: detect absent/ambiguous content per level, batch all proposed repairs into one consolidated approval request before question 1, apply only what's approved (FR-003, research.md §7)
- [X] T023 [US3] Add decline-path handling to `commands/speckit.know-your-spec.check.md`: if a proposed repair is declined, substitute a question from different already-established content at that level, or state plainly that none exists rather than asking an untruthful question (Edge Cases)
- [X] T024 [P] [US3] Add `tests/judgment/fixtures/thin-section/spec.md` — a synthetic spec with one deliberately thin/ambiguous section, and an alternative already-established source for that same difficulty level
- [X] T025 [US3] Author `tests/judgment/expected/thin-section.json` — ground truth covering both the approve outcome (repair applied, question asked from it) and the decline-with-alternative outcome
- [X] T026 [P] [US3] Add `tests/judgment/fixtures/thin-section-no-alt/spec.md` — a synthetic spec with a thin/ambiguous section at one level and genuinely no alternative established content anywhere for that level
- [X] T027 [US3] Author `tests/judgment/expected/thin-section-no-alt.json` — ground truth confirming the decline-with-no-alternative path states this plainly rather than asking an untruthful question
- [X] T028 [P] [US3] Write `tests/judgment/probes/repair-approval.md` — single-turn probe verifying the consolidated proposal-before-question-1 gate, and the decline paths from T025/T027

**Checkpoint**: All three user stories work independently and together — the full checkpoint never quizzes on unestablished content.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Packaging, test orchestration, and whole-feature invariants (FR-012/SC-005 no-persistence, FR-016/SC-004 non-blocking) that span all three stories.

- [X] T029 [P] Write `README.md` at the repository root: what the extension does, install instructions (`specify extension add`), usage, repository layout (mirrors plan.md § Project Structure)
- [X] T030 [P] Add `LICENSE` (MIT) at the repository root
- [X] T031 [P] Write `CHANGELOG.md` at the repository root recording the 1.0.0 initial release
- [X] T032 Write `tests/run.sh` at the repository root orchestrating both test tiers: `tests/deterministic/*.sh` then `tests/judgment/eval.sh`
- [X] T033 Write `tests/judgment/eval.sh`: single-shot `claude -p --output-format json` derivation-quality harness diffing each `tests/judgment/fixtures/*/spec.md` run against its `tests/judgment/expected/*.json`, plus a runner for the `tests/judgment/probes/*.md` single-turn behavioral probes (research.md §13). **Live-validated and corrected through two full rounds** (research.md §13 corrections #1-#2): exact-content-diff grading replaced with rule-adherence grading; a probe-frontmatter parsing bug (missing closing `---`) fixed in all 5 probe files; `DERIVATION_SCHEMA` given a proper `options`/`correct_option_index` field for MC questions; the derivation prompt corrected to stop the model citing the command file's own section names as spec.md content; one probe assertion reworded from an unfalsifiable internal-bookkeeping claim to an observable one. Final state: deterministic 2/2, judgment 4/4 fixtures at 100% agreement, 5/5 probes passing.
- [X] T034 [P] Write `tests/deterministic/test-no-persistence.sh` asserting `commands/speckit.know-your-spec.check.md` contains no instruction to write questions/answers/scores/completion markers to `spec.md` or any repository file outside the approved-repair path (FR-012, SC-005)
- [X] T035 Executed what's automatable of the 8 `quickstart.md` scenarios: Scenario 1 (install) verified for real via `specify extension add --dev` into a scratch project — command, alias, and mandatory `after_specify` hook all registered correctly, `.extensionignore` correctly excluded dev-only content; the full `tests/run.sh` suite (the closest automated proxy for Scenarios 2-8's behavioral guarantees) is green. The literal live multi-turn conversational walkthrough of Scenarios 2-8 still needs a real interactive session — see `quickstart.md`'s Validation Status note.

**Checkpoint**: Feature complete, packaged, and validated against every FR/SC in spec.md. All 35 tasks complete.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)**: strict blocker — nothing installs before T004/T005 exist.
- **Phase 2 → Phase 3 (US1)**: strict blocker — US1 tasks edit the command file T005 created.
- **Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3)**: recommended sequential order, since all three stories' implementation tasks (T006-T010, T017-T018, T021-T023) edit the same single command file and each story's behavior layers on top of the previous one's. Each story is still independently *testable* per its own Independent Test criteria — this ordering is about avoiding merge churn on one file, not a testing dependency.
- **Test/fixture tasks** (T011-T016, T019-T020, T024-T028) have no dependency on their sibling implementation tasks landing first — fixtures and expected-output files can be authored any time after the relevant contracts/spec content exists, and probes can be drafted before the behavior they check is implemented.
- **Phase 6 (Polish)**: T029-T031 depend only on Phase 1-2 (package existing). T032-T034 depend on all fixtures/probes/deterministic tests existing (T011-T028). T035 depends on every prior phase being complete.

## Parallel Execution Examples

- Within Phase 1: T003 (`.extensionignore`) can run parallel to T002 (git init).
- Within Phase 3 (US1): T011, T014, T015, T016 (four different test/probe files) can all be written in parallel to each other, and in parallel to T006-T010 (different files).
- Within Phase 4 (US2): T019 (fixture file) can be written in parallel to T017-T018 (command file).
- Within Phase 5 (US3): T024 and T026 (two independent fixture files) can be written in parallel to each other and to T021-T023 (command file).
- Within Phase 6: T029, T030, T031, T034 are all independent files and can run in parallel.

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 only).** This delivers the core value: an
installed extension that auto-fires after `/speckit-specify` and runs a coached, one-at-a-time,
semantically-judged comprehension loop with skip/reveal and a clean completion summary — even
before the five-fixed-level structure (US2) or the repair-approval safety net (US3) are layered
in. Ship and validate US1 independently first, then add US2 (difficulty/format structure), then
US3 (never-test-unestablished-content guarantee), per spec.md's own priority ordering (P1, P2,
P2). Each checkpoint above confirms the increment is independently testable before moving on.
