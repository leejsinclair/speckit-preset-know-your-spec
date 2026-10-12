---

description: "Task list for Checkpoint After Clarify"
---

# Tasks: Checkpoint After Clarify

**Input**: Design documents from `/specs/002-checkpoint-after-clarify/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/trigger.md, quickstart.md

**Tests**: Included. The plan changes one deterministic check and adds one judgment probe
(research.md §8), and CLAUDE.md asks for a probe whenever the command file's behaviour changes.
Test tasks come first in each story and must fail before the implementation task that follows.

**Organization**: Tasks are grouped by user story. The shipped change is small (one manifest key,
three paragraphs of the command file), so the stories are split by which half of the move they
deliver: US1 adds the start after clarify, US2 removes the start after specify, US3 keeps the
manual start documented. Between US1 and US2 the checkpoint starts at both points; that state is
valid for testing but must not be released.

In this file, `research.md §N` means `specs/002-checkpoint-after-clarify/research.md`. Task ids
are stable: T013 was removed after analysis (T011 already covers it) and T031 was added, so the
numbering has a gap and is not in order in Phase 6.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Flat-at-root Spec Kit extension (plan.md, Project Structure): `extension.yml`, `commands/`,
`scripts/`, `tests/` at the repository root. All paths below are relative to the repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm a clean starting point so later failures are attributable to this change.

- [X] T001 Run `tests/run.sh --deterministic-only` from the repository root and confirm every check passes before any edit; if anything fails, check the interpreter and dependencies first (CLAUDE.md, Tests) and stop until it is green
- [X] T002 Run `git status` and note the unrelated changes already present (`README.md` install-line edit, untracked `CLAUDE.md` and `insights/`) so they are not mistaken for, or lost among, this feature's changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None. Research found that Spec Kit `>=1.0.0`, the floor already declared in
`extension.yml`, dispatches `after_clarify` hooks, refuses incompatible installs and removes stale
hook entries on upgrade (research.md §2, §3, §4). There is no shared groundwork to lay, so the
user stories can start as soon as Phase 1 is done.

---

## Phase 3: User Story 1 - Checkpoint starts when clarification finishes (Priority: P1) 🎯 MVP

**Goal**: When `/speckit-clarify` finishes, the checkpoint starts with no confirmation prompt and
quizzes on the spec as it stands after clarification (FR-025, FR-028, SC-009).

**Independent Test**: Install the extension into a scratch project, run `/speckit-clarify` to
completion and confirm the session starts with no further input (a proposed repair, the spec page
offer or question 1) and its questions reflect the clarified spec (quickstart.md scenarios 1 and
3).

### Tests for User Story 1

> Write these first and confirm they fail before T005 and T006.

- [X] T003 [P] [US1] In `tests/deterministic/test-command-manifest.sh`, replace the `after_specify` assertion (the `awk '/after_specify:/...'` block and its failure message) with the same check for `after_clarify`: the hook must exist under `hooks:` and its `optional:` must be `false`; point the failure message at `specs/002-checkpoint-after-clarify/research.md §1`. Also add an assertion that the Step 0 section of `commands/speckit.know-your-spec.check.md` (from the `## Step 0` heading to the `## Step 1` heading) contains the words `from disk`, with a failure message pointing at `specs/002-checkpoint-after-clarify/research.md §6` (User Story 1, scenario 2). Run the script and confirm it now fails
- [X] T004 [P] [US1] Create `tests/judgment/probes/after-clarify-start.md` following the schema in `tests/judgment/probes/README.md`: `probe: "after-clarify-start"`, `fr: ["FR-025", "FR-028"]`; the harness (`tests/judgment/eval_impl.py`, `run_probes`) supplies no spec and sends `when` as the developer's next message, so the probe carries its own state. `given`: the command has just been started by the `after_clarify` hook at the end of a `/speckit-clarify` run that asked no questions because the spec was already clear; Step 0 read `spec.md` from disk; Step 1 is finished, found no repairs and derived all five questions, and the text of the derived question 1 (Recognise level, multiple choice, with its options) is written out in `given`; the spec page helper is not installed; nothing has been shown to the developer yet. `when`: the developer has sent nothing since `/speckit-clarify` ended. `assert`: the response presents question 1 at the Recognise level, it does not ask whether to run the checkpoint or wait for confirmation, it does not say there is nothing to check or that the checkpoint is skipped because nothing changed, and it does not present question 2 or any hint before the developer answers

### Implementation for User Story 1

- [X] T005 [US1] In `extension.yml`, add `after_clarify` under `hooks:` with `command: "speckit.know-your-spec.check"`, `optional: false` and `description: "Run the five-question Comprehension Checkpoint when clarification finishes"`, with no `priority` and no `condition` (contracts/trigger.md; research.md §1, §5). Leave `requires.speckit_version` at `">=1.0.0"` and add a one-line comment above it saying this floor already covers the end-of-clarify hook (`specs/002-checkpoint-after-clarify/research.md §2`). Leave the `after_specify` entry in place for now; T009 removes it
- [X] T006 [US1] In `commands/speckit.know-your-spec.check.md`, edit only the Purpose paragraph, the "Trigger awareness" paragraph and Step 0 (research.md §6, §7): say the command is started automatically by the `after_clarify` hook when `/speckit-clarify` finishes, including runs that asked no questions, runs ended early and repeat runs; keep the statement that behaviour is identical whether hook-triggered or manual and that there is never a silent exit; add to Step 0 an instruction to read `spec.md` from disk (keep the words "from disk"; T003 asserts them) at the start of every session and derive from that reading, not from any earlier view of the spec in the conversation. Do not touch Steps 1 to 5 or the Invariants, and do not introduce em dashes in the new text
- [X] T007 [US1] Run `tests/run.sh --deterministic-only` and confirm `test-command-manifest.sh` and `test-no-persistence.sh` both pass, then run `tests/judgment/eval.sh --probes-only --probe after-clarify-start` and confirm the probe passes (this calls `claude -p` and costs tokens)

**Checkpoint**: The checkpoint starts after clarify. It also still starts after specify until
Phase 4 is done.

---

## Phase 4: User Story 2 - Nothing happens after specify (Priority: P2)

**Goal**: When `/speckit-specify` finishes, the extension presents nothing: no question, no offer,
no message (FR-026, SC-010, SC-012).

**Independent Test**: Install the extension, run `/speckit-specify` and confirm the output
contains nothing from this extension (quickstart.md scenario 2); `.specify/extensions.yml` has no
`know-your-spec` entry under `after_specify` (quickstart.md scenario 1).

### Tests for User Story 2

> Write this first and confirm it fails before T009 and T010.

- [X] T008 [US2] In `tests/deterministic/test-command-manifest.sh`, add two assertions after the `after_clarify` check from T003: `extension.yml` contains no `after_specify` key (FR-026), and `commands/speckit.know-your-spec.check.md` does not contain the string `after_specify`. Run the script and confirm it now fails on the first of them

### Implementation for User Story 2

- [X] T009 [US2] In `extension.yml`, delete the `after_specify` hook entry so `after_clarify` is the only key under `hooks:`, and rewrite the comment above `hooks:` to describe the new timing: automatic, no confirmation prompt, at the end of `/speckit-clarify`, nothing at the end of `/speckit-specify` (`specs/002-checkpoint-after-clarify/research.md §1`)
- [X] T010 [US2] In `commands/speckit.know-your-spec.check.md`, remove every remaining mention of `after_specify` and of the checkpoint starting after `/speckit-specify` from the Purpose and "Trigger awareness" paragraphs (the Step 0 reference to `/speckit-specify`-style spec resolution via `check-prerequisites.sh` stays as it is)
- [X] T011 [US2] Run `tests/run.sh --deterministic-only` and confirm all deterministic checks pass

**Checkpoint**: The move is complete in the shipped files. US1 and US2 together are the
releasable change.

---

## Phase 5: User Story 3 - Checkpoint on demand (Priority: P3)

**Goal**: The checkpoint remains startable by hand at any time, and the documentation tells a
developer who never clarifies that this is their route (FR-029, Assumptions).

**Independent Test**: With a spec present and no clarification run, start the checkpoint by hand
and confirm a full session runs (quickstart.md scenario 6).

### Implementation for User Story 3

- [X] T012 [US3] Re-read the Purpose paragraph of `commands/speckit.know-your-spec.check.md` after T006 and T010 and confirm it still states that the command is re-runnable on demand against any existing spec, whether or not clarification has been run; restore that sentence if the edits dropped it
- [X] T014 [US3] In `README.md`, rewrite the usage note that currently begins "Normally you don't invoke this directly" (near line 88) to say the checkpoint starts on its own when `/speckit-clarify` finishes, and that a developer who skips clarification, or wants to go again, runs `/speckit-know-your-spec-check` or `/speckit-kys-check` by hand

**Checkpoint**: All three user stories are in place.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: User-facing documentation and spec artifacts (FR-031), the 1.2.0 release
bookkeeping, and end-to-end validation. Prose rule for every task here: no em dashes and no AI
writing tells (CLAUDE.md, Working agreements).

### User-facing documentation

- [X] T015 [P] In `README.md`, update the "Why" paragraph ("immediately after a spec is finished") and the "What it does" stage table: the `/speckit-specify` row stays unmodified with nothing from this extension after it, a `/speckit-clarify` row is added, and the automatic row becomes "when clarification finishes" with the `after_clarify` hook; also update the install paragraph that says it "wires the mandatory `after_specify` hook". Keep the existing uncommitted edit to the install command
- [X] T016 [P] In `CHANGELOG.md`, add a `## 1.2.0 - <release date>` entry at the top: the automatic start moved from the end of `/speckit-specify` to the end of `/speckit-clarify`; nothing happens after specify; a developer who does not run clarify starts the checkpoint by hand; the session itself, the spec page and zero persistence are unchanged; Spec Kit `>=1.0.0` is still the requirement; upgrading needs no manual step; a project whose `/speckit-clarify` command was set up by an older Spec Kit and never refreshed may not start the checkpoint until the project's Spec Kit files are upgraded
- [X] T017 [P] In `CLAUDE.md`, update "What this is" (the checkpoint "fires automatically through a mandatory `after_specify` hook") and the `extension.yml` bullet under Architecture to name the `after_clarify` hook, and add that `specs/002-checkpoint-after-clarify/research.md` is cited by its full path while a bare `research.md §N` still means spec 001; in the "What ships" bullet, add `CLAUDE.md` and `insights/` to the list `.extensionignore` keeps out of installs (T031)

### Spec 001 artifacts kept in step

- [X] T018 [P] In `specs/001-know-your-spec/spec.md`, reword FR-015 so the automatic start is when `/speckit-clarify` finishes and the on-demand half is unchanged, and add a short note that the original timing (immediately after `/speckit-specify`) was superseded by spec 002 FR-025 and FR-026. Do not edit `tests/judgment/fixtures/own-spec/spec.md`; it is a frozen quiz subject (research.md §8)
- [X] T019 [P] In `specs/001-know-your-spec/contracts/extension.yml`, make the `hooks:` block, its comment and the hook description match the root `extension.yml` after T009
- [X] T020 [P] In `specs/001-know-your-spec/contracts/command-interface.md`, replace the "Automatic" bullet of the Invocation section with the new timing and a pointer to `specs/002-checkpoint-after-clarify/contracts/trigger.md`
- [X] T021 [P] In `specs/001-know-your-spec/data-model.md`, change the session lifecycle line "begins either automatically (mandatory `after_specify` hook) or manually" to name the `after_clarify` hook
- [X] T022 [P] In `specs/001-know-your-spec/plan.md`, update the two places that describe auto-fire on `after_specify` (Summary and Constraints) and correct the Primary Dependencies line from Spec Kit CLI `>=1.0.2` to `>=1.0.0` to match the manifests (research.md §2)
- [X] T023 [P] In `specs/001-know-your-spec/quickstart.md`, update the install expectation (section 1: the hook entry is under `after_clarify`), retitle and rewrite section 2 so the automatic trigger is exercised with `/speckit-clarify`, and adjust the validation-status note that mentions the `after_specify` hook
- [X] T024 [P] In `specs/001-know-your-spec/research.md`, add a dated note at the end of §3 saying the hook event was changed to `after_clarify` by spec 002 while the decision that the hook is mandatory (`optional: false`) stands; leave the original text of §3 intact

### Packaging

- [X] T031 [P] Keep development-only files out of installs and out of the repository: in `.extensionignore`, add `CLAUDE.md` and `insights/` (anything at the repository root ships unless listed there, and T017 edits `CLAUDE.md`, so it is about to be committed); in `.gitignore`, add `insights/` so the session review is never committed. Then run `git status` and confirm `insights/` is no longer listed as untracked

### Release bookkeeping (1.2.0)

- [X] T025 Set the version to `1.2.0` in the four places CLAUDE.md lists, together: `extension.version` in `extension.yml`, the tag in the README install URL (`.../refs/tags/v1.2.0.zip`), the heading added in T016 in `CHANGELOG.md` (replace `<release date>` with the date of the release, as `YYYY-MM-DD`, like the entries below it), and `extension.version` in `specs/001-know-your-spec/contracts/extension.yml`

### Validation

- [X] T026 Run `tests/run.sh` (both tiers) and confirm the deterministic tier passes and every fixture and probe in the judgment tier passes, including `after-clarify-start`; report the actual output if anything fails
- [X] T027 Run the documentation check at the end of `specs/002-checkpoint-after-clarify/quickstart.md` (`grep -rn "after_specify" ...`) and confirm the only hits are the history listed there: the 1.0.0 entry in `CHANGELOG.md` (and the 1.2.0 entry if it names the old hook), the completed tasks in `specs/001-know-your-spec/tasks.md`, and §3 of `specs/001-know-your-spec/research.md` (its original text and the note added in T024)
- [X] T028 In a throwaway Spec Kit project outside this repository, run quickstart.md scenario 1 (fresh install: one `know-your-spec` hook entry, under `after_clarify`, `optional: false`), scenario 4 (upgrade from the v1.1.2 tag zip with `--force`: the `after_specify` entry is gone, nothing edited by hand, FR-032) and scenario 5 (a copy requiring Spec Kit `>=99.0.0` is refused with exit code 1 and `.specify/extensions.yml` is unchanged, FR-033), then the registration half of scenario 8 (the two hand-written `other-ext` hook entries, under `after_specify` and `after_clarify`, are unchanged after a forced reinstall, FR-030)
- [ ] T029 In an interactive agent session in the same throwaway project, run quickstart.md scenarios 2, 3, 6 and 7: nothing from the extension after `/speckit-specify`; the checkpoint starts after `/speckit-clarify` on all three endings (answered, no questions, ended early); a manual start works without clarifying; both kinds of session ask five questions in the fixed order and leave `git status` clean. Then run the agent-session half of scenario 8 with the stand-in `speckit-other-ping` command from T028: after `/speckit-specify` the other step is the only interactive step (SC-012), and after `/speckit-clarify` both the other step and the checkpoint run (FR-030). If no interactive session is available, say so in the summary and list these scenarios as not checked
- [X] T030 Run `git status` and review the full diff: confirm only the files listed in plan.md (Project Structure) changed, `scripts/python/specpage.py`, `tests/unit/`, `tests/deterministic/test-no-persistence.sh` and `tests/judgment/fixtures/` are untouched, `.extensionignore` and `.gitignore` differ only by the lines T031 added, and nothing at the repository root would ship that did not ship in 1.1.2. Do not commit or push unless asked

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: empty.
- **US1 (Phase 3)**: after Phase 1.
- **US2 (Phase 4)**: after US1. It edits the same two shipped files and the same test script, and
  removing the old trigger before the new one exists would leave no automatic start at all.
- **US3 (Phase 5)**: T012 after US2 (it re-reads a paragraph US1 and US2 edited). T014 only needs
  Phase 1.
- **Polish (Phase 6)**: T015 to T024 after US2. T031 only needs Phase 1. T025 after T016 and T019.
  T026 to T030 last.

### Within Each User Story

- US1: T003 and T004 (tests, parallel) → T005 → T006 → T007.
- US2: T008 → T009 → T010 → T011.
- US3: T012 after T010; T014 independent.

### Same-file constraints

- `extension.yml`: T005 → T009 → T025.
- `commands/speckit.know-your-spec.check.md`: T006 → T010 → T012.
- `tests/deterministic/test-command-manifest.sh`: T003 → T008.
- `README.md`: T014, T015 and T025 touch different passages but the same file; do them in
  sequence.
- `specs/001-know-your-spec/contracts/extension.yml`: T019 → T025.
- `CHANGELOG.md`: T016 → T025.

### Parallel Opportunities

- T003 and T004 (different test files).
- T016 to T024, with one of T014/T015: nine different documentation files. T014 and T015 share
  `README.md`, so only one of them joins the batch.

---

## Parallel Example: User Story 1

```text
Task: "T003 Change the hook assertion in tests/deterministic/test-command-manifest.sh to after_clarify"
Task: "T004 Create tests/judgment/probes/after-clarify-start.md"
```

## Parallel Example: Polish

```text
Task: "T016 Add the 1.2.0 entry to CHANGELOG.md"
Task: "T017 Update CLAUDE.md"
Task: "T018 Reword FR-015 in specs/001-know-your-spec/spec.md"
Task: "T019 Update specs/001-know-your-spec/contracts/extension.yml"
Task: "T020 Update specs/001-know-your-spec/contracts/command-interface.md"
Task: "T021 Update specs/001-know-your-spec/data-model.md"
Task: "T022 Update specs/001-know-your-spec/plan.md"
Task: "T023 Update specs/001-know-your-spec/quickstart.md"
Task: "T024 Add the superseded note to specs/001-know-your-spec/research.md"
```

---

## Implementation Strategy

### MVP

US1 (T001 to T007) makes the checkpoint start after clarify and is testable on its own. It is not
releasable alone, because the checkpoint would start at both points and FR-026 would be unmet.

### Smallest releasable increment

US1 + US2 (through T011), then T014, all of Phase 6 (T015 to T025 and T031) and validation T026
to T030.
FR-031 makes the documentation and spec 001 updates part of the change, and T027 fails without
them. Only T012, which re-checks earlier work, could be left out.

### Incremental Delivery

1. Phase 1, then US1: the new trigger works. Validate with T007.
2. US2: the old trigger is gone. Validate with T011.
3. US3: the manual route is confirmed and documented.
4. Polish: documentation, spec 001 artifacts, version 1.2.0, full validation.

---

## Notes

- Requirement coverage: FR-025 and FR-028 (T003 to T007), FR-026 (T008 to T011), FR-027 (T006
  scope limits, T029, T030), FR-029 (T012, T014; the command name and alias assertions run in T011), FR-030 (T005: no priority or condition; T028:
  another extension's entries unchanged; T029: both run), FR-031 (T015 to T024), FR-032 and FR-033 (T028, CLI behaviour; no
  code).
- A page rendering change is not part of this feature, so no browser check of the spec page is
  required.
- Commit and push only when asked, and to the branch named (CLAUDE.md, Working agreements). Work
  is currently on git branch `spec-page`, not a `002-checkpoint-after-clarify` branch.
