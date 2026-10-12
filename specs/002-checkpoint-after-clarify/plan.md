# Implementation Plan: Checkpoint After Clarify

**Branch**: `002-checkpoint-after-clarify` (work is currently on git branch `spec-page`) | **Date**: 2026-10-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-checkpoint-after-clarify/spec.md`

## Summary

Move the automatic start of the Comprehension Checkpoint from the end of `/speckit-specify` to
the end of `/speckit-clarify`. The whole change to the shipped product is one key in the
manifest (`hooks.after_specify` becomes `hooks.after_clarify`, still `optional: false`) and three
paragraphs of the command file (purpose, trigger awareness, and a new instruction to read
`spec.md` from disk at the start of each session). Session behaviour, the spec page and zero
persistence are untouched.

Research found that nothing else is needed. Spec Kit has dispatched `after_clarify` hooks since
v0.5.1, so the version floor the extension already declares (`>=1.0.0`) satisfies FR-033 and the
CLI's own compatibility check produces the refusal. Upgrading removes the old `after_specify`
registration without help (FR-032). The rest of the work is tests, documentation and the 1.2.0
release bookkeeping.

## Technical Context

**Language/Version**: YAML manifest and a Markdown command file, interpreted by the installing
agent. `scripts/python/specpage.py` (Python 3.11+, standard library) is not changed.

**Primary Dependencies**: Spec Kit CLI `>=1.0.0`, unchanged. Its `/speckit-clarify` command
template dispatches `hooks.after_clarify` (research.md §1, §2).

**Storage**: N/A. The checkpoint still writes nothing. The only stored data involved is the hook
entry the Spec Kit CLI writes to the consuming project's `.specify/extensions.yml`
(data-model.md).

**Testing**: `tests/run.sh`. Deterministic tier: `test-command-manifest.sh` gets the changed and
new hook assertions. Judgment tier: one new probe, `after-clarify-start`. Install, upgrade and
refusal are CLI behaviours, validated by hand in quickstart.md scenarios 1, 4 and 5. Coexistence
with another extension (FR-030, SC-012) is validated by hand in scenario 8.

**Target Platform**: Any Spec Kit project on Spec Kit `>=1.0.0`. Authored and checked against
Claude's skills-mode rendering, as in spec 001.

**Project Type**: Spec Kit extension, flat at the repository root.

**Performance Goals**: N/A.

**Constraints**:

- FR-027: no change to Steps 1 to 5 or the invariants of the command file.
- `test-no-persistence.sh` greps the command file for specific wording; the edits stay clear of
  those passages (research.md §7).
- FR-032: no manual migration step.
- Docs and prose: no em dashes and no AI writing tells (CLAUDE.md working agreements).

**Scale/Scope**: 2 shipped files edited (`extension.yml`, the command file), 1 test script
edited, 1 probe added, about 10 documentation and spec-artifact files brought in step. No new
shipped file. `.extensionignore` gains `CLAUDE.md` and `insights/`, and `.gitignore` gains
`insights/`, so that neither development-only item reaches an install.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template; no principle has been
ratified. There is nothing to gate against, so the check passes before research and again after
design. The project's working agreements in CLAUDE.md are treated as constraints above.

## Project Structure

### Documentation (this feature)

```text
specs/002-checkpoint-after-clarify/
├── plan.md              # This file
├── research.md          # Phase 0: Spec Kit facts behind FR-025, FR-032, FR-033
├── data-model.md        # Phase 1: lifecycle start and the hook registration entry
├── quickstart.md        # Phase 1: validation scenarios
├── contracts/
│   └── trigger.md       # Phase 1: manifest hook, invocation table, install and upgrade outcomes
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks; not created by /speckit-plan)
```

### Source Code (repository root)

Files this feature changes, grouped by what they are:

```text
# Shipped
extension.yml                                   # hooks: after_specify -> after_clarify; version 1.2.0; comments
commands/speckit.know-your-spec.check.md        # Purpose, Trigger awareness, Step 0 (read spec.md from disk)

# Tests
tests/deterministic/test-command-manifest.sh    # after_clarify is mandatory; no after_specify in manifest or command file; Step 0 reads from disk
tests/judgment/probes/after-clarify-start.md    # new probe: FR-025, FR-028

# User-facing documentation (FR-031)
README.md                                       # "Why", stage table, usage note, install URL (v1.2.0)
CHANGELOG.md                                    # 1.2.0 entry
CLAUDE.md                                       # "What this is", the manifest bullet, the "What ships" bullet

# Packaging
.extensionignore                                # add CLAUDE.md and insights/
.gitignore                                      # add insights/

# Spec artifacts kept in step (FR-031, CLAUDE.md)
specs/001-know-your-spec/spec.md                          # FR-015 reworded, superseded-by note
specs/001-know-your-spec/contracts/extension.yml          # hook and version, matching the root manifest
specs/001-know-your-spec/contracts/command-interface.md   # "Invocation" section
specs/001-know-your-spec/data-model.md                    # session lifecycle line
specs/001-know-your-spec/plan.md                          # trigger wording; speckit floor corrected to >=1.0.0
specs/001-know-your-spec/quickstart.md                    # install expectation and scenario 2
specs/001-know-your-spec/research.md                      # §3 gains a "superseded by spec 002" note
```

Not changed, on purpose: `scripts/python/specpage.py`, `tests/unit/`, `test-no-persistence.sh`,
and `tests/judgment/fixtures/own-spec/spec.md` (a frozen quiz subject graded
against `expected/own-spec.json`, research.md §8). Also left as they are, because they record
what was true when written: `specs/001-know-your-spec/tasks.md` (completed tasks that name the
`after_specify` hook) and `specs/001-know-your-spec/checklists/requirements.md`.

**Structure Decision**: No structural change. The extension stays a flat-at-root package with one
command, one script and one hook; only which event the hook is attached to changes.

## Design decisions (from research.md)

| # | Decision | Serves |
|---|---|---|
| 1 | `hooks.after_clarify`, `optional: false`, replacing `after_specify` | FR-025, FR-026, FR-028 |
| 2 | `requires.speckit_version` stays `>=1.0.0` | FR-033 |
| 3 | Refusal on older Spec Kit comes from the CLI's compatibility check, which runs before anything is removed | FR-033 |
| 4 | No migration step; the CLI removes the old hook entry on upgrade | FR-032 |
| 5 | No `priority`, no `condition` on the hook | FR-030 |
| 6 | Command file Step 0 reads `spec.md` from disk every session | User Story 1, scenario 2 |
| 7 | Command file edits limited to Purpose, Trigger awareness and Step 0 | FR-027 |
| 8 | One changed and three new deterministic assertions, one new probe | SC-009, SC-010, User Story 1, scenario 2 |
| 9 | Release as 1.2.0, version updated in four places | Assumptions |

## Risks

- **Developers who never clarify stop seeing the checkpoint.** This is the accepted cost in the
  spec's Assumptions. The README and the changelog entry say so and point to the manual command.
- **A stale clarify command in an old project.** The version check looks at the CLI, not at the
  command files already rendered into a project (research.md §3). The same is true of the
  current hook. Not addressed beyond the Spec Kit upgrade the spec already assumes.
- **Hook dispatch depends on the agent following the clarify template.** SC-009 asks for 100%.
  The template's directive wording and "Done When" item make this as reliable as the present
  `after_specify` behaviour, which is the baseline. Quickstart scenario 3 checks the three
  clarify endings by hand.

## Post-design Constitution Check

Unchanged: no ratified principles, no violations.

## Complexity Tracking

No constitution violations. This section does not apply.
