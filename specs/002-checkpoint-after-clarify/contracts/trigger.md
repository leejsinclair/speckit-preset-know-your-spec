# Trigger Contract: when the Comprehension Checkpoint starts

This is the interface this feature changes. The behaviour of a session once started is the
contract in `specs/001-know-your-spec/contracts/command-interface.md`, which stays in force
except for its "Invocation" section, replaced by the one below.

## Manifest (root `extension.yml`)

```yaml
extension:
  version: "1.2.0"

requires:
  speckit_version: ">=1.0.0"      # unchanged; see research.md §2

hooks:
  after_clarify:
    command: "speckit.know-your-spec.check"
    optional: false
    description: "Run the five-question Comprehension Checkpoint when clarification finishes"
```

- There is no `after_specify` key, and no other hook.
- No `priority` and no `condition` (research.md §5).
- `provides` (the command, its alias, the `specpage` script) is unchanged.
- `specs/001-know-your-spec/contracts/extension.yml` is kept in step, as CLAUDE.md requires.

## Invocation

| Point in the workflow | What this extension does | Requirement |
|---|---|---|
| `/speckit-specify` finishes | Nothing. No question, no offer, no message. | FR-026, SC-010 |
| `/speckit-clarify` finishes | The checkpoint starts, with no confirmation prompt. This holds for a run that asked no questions, a run ended early and a repeat run. | FR-025, FR-028, SC-009 |
| `/speckit-know-your-spec-check` or `/speckit-kys-check` typed by the developer | The checkpoint starts, whether or not clarification has been run. | FR-029 |
| Any other Spec Kit command | Nothing, as before. | SC-013 |

**Input**: none beyond the active feature (`.specify/feature.json`), as before.

**Spec version quizzed**: the command reads `spec.md` from disk when the session starts and
derives its questions from that reading (research.md §6). After clarify, that is the clarified
spec.

**Equivalence**: a session started by the hook and a session started by hand follow the same
steps and leave the project's files the same, apart from any repair the developer approved
(FR-027, SC-011). The command file does not branch on how it was started.

## Install and upgrade (performed by the Spec Kit CLI)

| Situation | Outcome | Requirement |
|---|---|---|
| Fresh install, Spec Kit `>=1.0.0` | `.specify/extensions.yml` gains one entry for `know-your-spec`, under `hooks.after_clarify`, `optional: false`. | FR-025 |
| Upgrade from 1.1.x, Spec Kit `>=1.0.0` | The `hooks.after_specify` entry for `know-your-spec` is removed and the `hooks.after_clarify` entry is added, with no manual step. | FR-032 |
| Install or upgrade, Spec Kit older than `1.0.0` | Refused with `Extension requires spec-kit >=1.0.0, but <installed> is installed.` and exit code 1. Any installed version of the extension, and its hook entry, are left as they were. | FR-033 |
| Other extensions' hook entries, any event | Never added to, changed or removed. | FR-030 |

## What must not change

- The JSON line printed by `specpage.py serve`, the anchors, and every step of the command file
  from Step 1 onward.
- The three invariants: never persist, never block, never advance silently.
- The wording `test-no-persistence.sh` looks for in the command file.
