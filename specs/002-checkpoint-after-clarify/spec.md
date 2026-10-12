# Feature Specification: Checkpoint After Clarify

**Feature Branch**: `002-checkpoint-after-clarify`

**Created**: 2026-10-11

**Status**: Draft

**Input**: User description: "this is conflicting with another extension, however it makes me wonder if the comprehension check should happen after clarify is that possible? https://github.com/github/spec-kit/tree/main/extensions"

## Background

Today the Comprehension Checkpoint starts on its own the moment `/speckit-specify` finishes
(spec 001, FR-015). Two problems follow from that timing:

- Another installed extension runs its own interactive quiz or review step at the same moment,
  so the developer is put through two interruptions back to back.
- The spec is not settled yet. `/speckit-clarify` can still change it, so the developer may be
  quizzed on content that is about to move.

Spec Kit does let an extension act when clarification finishes, so the checkpoint can move there.
Requirement and success criterion ids in this spec continue the numbering of spec 001 (which ends
at FR-024 and SC-008) so that ids stay unique across the project.

## Clarifications

### Session 2026-10-11

- Q: What should happen when the extension is installed in a project whose Spec Kit version is
  too old to trigger anything at the end of `/speckit-clarify`? → A: Require a Spec Kit version
  that supports the end-of-clarify trigger; install or upgrade is refused on older versions with
  a clear message.
- Q: After `/speckit-specify`, how does the developer accept the offer to run the checkpoint? →
  A: There is no offer. The checkpoint moves to the end of `/speckit-clarify`, and the extension
  does nothing when `/speckit-specify` finishes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Checkpoint starts when clarification finishes (Priority: P1)

A developer runs `/speckit-clarify` on a spec. When clarification finishes, the Comprehension
Checkpoint starts on its own, with no confirmation step, and quizzes the developer on the spec as
it stands after clarification.

**Why this priority**: This is the change itself. The checkpoint's value is that it happens
without being asked for, and the clarified spec is the one the developer will plan and build from.

**Independent Test**: Install the extension in a project, write a spec, run `/speckit-clarify` to
completion and confirm that the checkpoint session starts without any further input (a proposed
repair, the spec page offer or question 1), and that its questions reflect the clarified content.

**Acceptance Scenarios**:

1. **Given** a spec exists and the extension is installed, **When** the developer finishes
   `/speckit-clarify`, **Then** the checkpoint starts automatically with no confirmation prompt.
2. **Given** clarification changed the spec, **When** the checkpoint starts, **Then** its
   questions are derived from the spec as it is after those changes.
3. **Given** the checkpoint was started by the end of clarification, **When** the session runs,
   **Then** it behaves exactly as a manually started session: five questions, fixed order,
   coached retries with no cap, per-question skip or reveal, exit at any time.

---

### User Story 2 - Nothing happens after specify (Priority: P2)

A developer runs `/speckit-specify`. When the spec is written, the extension does nothing: no
checkpoint question, no offer and no message. The checkpoint has moved to the end of
clarification.

**Why this priority**: This removes the back-to-back interruption with the other extension, and
it stops the developer being quizzed on a spec that clarification is about to change.

**Independent Test**: Install the extension, run `/speckit-specify`, and confirm that the output
contains nothing from this extension.

**Acceptance Scenarios**:

1. **Given** the extension is installed, **When** `/speckit-specify` finishes, **Then** no
   checkpoint question, offer or message from this extension is presented.
2. **Given** another extension runs its own interactive step when `/speckit-specify` finishes,
   **When** that step ends, **Then** the developer is not placed into a checkpoint session.

---

### User Story 3 - Checkpoint on demand (Priority: P3)

A developer who skipped clarification, or who wants to go again, starts the checkpoint by hand at
any time, as they can today.

**Why this priority**: This already works. It is listed so that the change in timing does not
remove it, and because it is the only route for a developer who never clarifies.

**Independent Test**: With a spec present and no clarification run, start the checkpoint by hand
and confirm a full session runs.

**Acceptance Scenarios**:

1. **Given** a spec exists, **When** the developer starts the checkpoint by hand, **Then** a full
   session runs regardless of whether clarification has been run.

---

### Edge Cases

- Clarification is run more than once on the same spec: the checkpoint starts after each run. The
  developer can leave at any point at no cost (spec 001, FR-014).
- Clarification asks no questions because the spec is already clear, or the developer ends it
  early: the checkpoint still starts. One rule, and leaving takes one step.
- Clarification is run late, after planning has begun: the checkpoint still starts and still
  blocks nothing.
- Another extension also acts when clarification finishes: both run. The checkpoint must not
  prevent the other from running or change what it does.
- The developer ran the checkpoint by hand before clarifying and then runs clarification: the
  checkpoint starts again after clarification, against the changed spec.
- A project upgrades from a version where the checkpoint started after specify: after the
  upgrade the new timing applies with no manual setup, and the old automatic start is gone.
- The project's Spec Kit version cannot act when clarification finishes: installing or upgrading
  the extension is refused with a message naming the Spec Kit version required. The previously
  installed version, if any, keeps working as it did.
- The project's Spec Kit version is new enough, but its `/speckit-clarify` command was set up by
  an older version and never refreshed: the checkpoint may not start after clarification, and
  nothing reports it. The remedy is the normal Spec Kit upgrade of the project, and the
  checkpoint can be started by hand in the meantime. No detection is added.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-025**: System MUST start the Comprehension Checkpoint automatically, with no confirmation
  prompt, when `/speckit-clarify` finishes.
- **FR-026**: System MUST NOT start the checkpoint when `/speckit-specify` finishes, and MUST NOT
  offer it or present any other message at that point.
- **FR-027**: A checkpoint session MUST behave identically whether it was started by the end of
  clarification or by hand. Every requirement of spec 001 on session
  behaviour, the spec page and persistence (FR-001 to FR-014, FR-016, FR-018 to FR-024) continues
  to apply unchanged.
- **FR-028**: System MUST start the checkpoint after every `/speckit-clarify` run, including runs
  that asked no questions, runs the developer ended early and repeat runs on the same spec.
- **FR-029**: The checkpoint MUST remain startable by hand at any time against any existing spec.
- **FR-030**: The checkpoint MUST coexist with other extensions that act at the same points in
  the workflow: it MUST NOT prevent them from running or alter what they do.
- **FR-031**: This spec supersedes the first half of spec 001 FR-015 (automatic start
  immediately after `/speckit-specify`). Spec 001 and the project's user-facing documentation
  MUST be updated to describe the new timing.
- **FR-032**: A project that upgrades from an earlier version MUST get the new timing without any
  manual step beyond the normal upgrade, provided its Spec Kit version meets FR-033.
- **FR-033**: The extension MUST require a Spec Kit version that can act when `/speckit-clarify`
  finishes. On an older Spec Kit version, install and upgrade MUST be refused with a message
  that names the required version, and MUST leave any previously installed version of the
  extension unchanged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-009**: After every `/speckit-clarify` run, the checkpoint session starts with no
  additional action from the developer: its first step (a proposed repair, the spec page offer
  or question 1) is presented without being asked for. This is checked on each of the three
  ways a run can end: questions answered, no questions asked, and ended early by the developer.
- **SC-010**: In 100% of `/speckit-specify` runs, nothing from this extension is presented.
- **SC-011**: A session started after clarification and a session started by hand on the
  same spec both ask five questions in the same fixed order and
  leave the project's files identical, apart from any repair the developer approved.
- **SC-012**: With another extension that runs an interactive step after `/speckit-specify`
  installed, a developer finishing `/speckit-specify` goes through one interactive step, not two.
- **SC-013**: Every existing Spec Kit command produces the same result with the extension
  installed as before this change, other than when the checkpoint starts.

## Assumptions

- The other extension keeps its interactive step at the end of `/speckit-specify`. This feature
  does not coordinate with it or detect it.
- Developers who want the checkpoint without clarifying start it by hand, and the user-facing
  documentation says so. No second automatic trigger is added.
- When several extensions act as clarification finishes, the default ordering is acceptable. The
  checkpoint does not need to run before or after any particular extension.
- Starting the checkpoint after every clarify run, including repeat runs, is acceptable because
  leaving a session is immediate and free.
- The mechanics of a session are out of scope: five questions, fixed order, uncapped retries,
  the spec page and zero persistence are unchanged.
- A project on a Spec Kit version older than the one FR-033 requires upgrades Spec Kit first.
  No fallback timing is provided for older versions.
- This is released as a minor version, since the automatic trigger moves but the checkpoint
  itself and the ability to start it by hand are unchanged.
