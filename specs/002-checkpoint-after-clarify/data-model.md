# Phase 1 Data Model: Checkpoint After Clarify

This feature adds no entity and stores nothing. The two entities of spec 001 (Quiz Question and
Comprehension Checkpoint Session, `specs/001-know-your-spec/data-model.md`) keep every field and
rule. Two things change, and both are about how a session begins.

## Comprehension Checkpoint Session: lifecycle start

| | Before (1.1.2) | After (1.2.0) |
|---|---|---|
| Automatic start | when `/speckit-specify` finishes | when `/speckit-clarify` finishes (FR-025, FR-028) |
| At the end of `/speckit-specify` | a session starts | nothing from this extension (FR-026) |
| Manual start | any time, any existing spec | unchanged (FR-029) |
| `target_spec` content | the spec as written | the spec as read from disk when the session starts, so after any clarification (User Story 1, scenario 2) |

Everything after the start is the lifecycle in spec 001: repairs resolved, five questions in
fixed order, `completed` or `exited-early`, state discarded (FR-027).

More than one session per spec is normal: one after each clarify run, plus any started by hand.
Sessions share nothing, because nothing is kept between them.

## Hook registration (owned by Spec Kit, not by this extension)

The only stored data this feature touches is the entry Spec Kit writes to the consuming project's
`.specify/extensions.yml` at install. The extension declares it; the CLI writes, replaces and
removes it.

| Field | Value | Note |
|---|---|---|
| event key | `after_clarify` | was `after_specify` |
| `extension` | `know-your-spec` | the CLI uses this to find the extension's own entries |
| `command` | `speckit.know-your-spec.check` | unchanged |
| `optional` | `false` | no confirmation prompt (FR-025) |
| `enabled` | `true` | set by the CLI |
| `priority` | CLI default | not declared (research.md §5) |
| `condition` | none | the hook always runs (FR-028) |

**Rules**:

- After install or upgrade, the project has exactly one entry with `extension: know-your-spec`,
  and it is under `hooks.after_clarify` (FR-026, FR-032).
- Entries owned by other extensions, under any event, are never changed (FR-030).
- If the installed Spec Kit does not satisfy `requires.speckit_version`, no entry is written or
  removed (FR-033).
