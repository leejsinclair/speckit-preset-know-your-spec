# Implementation Plan: Spec Comprehension Check

**Branch**: `001-know-your-spec` | **Date**: 2026-09-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-know-your-spec/spec.md`

## Summary

Deliver "Know Your Spec" as a standalone, flat-at-root Spec Kit extension. Its single command
(`speckit.know-your-spec.check`, alias `speckit.kys-check`) runs a five-question Comprehension
Checkpoint against a finished `spec.md`, fixed at increasing difficulty (Recognise → Explain →
Apply → Trace → Evaluate), judged semantically, coached-and-retried with no attempt cap, with an
explicit per-question skip/reveal, and a session-only completion summary — nothing is ever
persisted to the repo except developer-approved `spec.md` repairs made before a question is
asked. The command fires automatically via a mandatory (`optional: false`) `after_specify` hook
and can also be run manually at any time. One optional script — the read-only spec page helper
(User Story 4, added in 1.1.0; research.md §15) — beyond the core `check-prerequisites.sh`; no
config file, no companion preset — every decision below was settled directly with the developer
in a design-tree interview (14 rounds) before this plan was written; this plan formalizes those
decisions rather than re-deriving them.

## Technical Context

**Language/Version**: The checkpoint itself is a YAML manifest plus a Markdown command file,
interpreted by the installing agent at runtime. The optional spec page (User Story 4) is one
Python file, `scripts/python/specpage.py`, Python 3.11+, standard library only.

**Primary Dependencies**: Spec Kit CLI `>=1.0.2` (the extension/hook mechanism itself). No
external services, libraries, or models — the checkpoint runs inside the same interactive AI
session that authored the spec (assumption in spec.md) and reuses core `check-prerequisites.sh`
to locate `spec.md`. The spec page needs `python3` (declared optional in the manifest) and, only
to draw a diagram, loads `mermaid@11` from the jsDelivr CDN in the developer's browser.

**Storage**: N/A by design. FR-012 / SC-005 require the checkpoint to write nothing to the repo
except an approved `spec.md` content repair (FR-003) made before a question is asked — never
questions, answers, scores, or completion markers. The spec page keeps one runtime file (its
address and process id) outside the project, removed when it stops (FR-022).

**Testing**: A bash test runner (`tests/run.sh`), mirroring the reference precedent's structure —
`tests/deterministic/` (manifest/command-file structural assertions, e.g. shellcheck-style
validation of frontmatter, hook wiring, alias safety) and `tests/judgment/` (single-shot `claude
-p --output-format json` evals diffed against hand-authored `expected/*.json`, plus isolated
single-turn behavioral probes). The spec page adds `tests/unit/` (Python `unittest`: the Markdown
renderer and the page server), run by `tests/deterministic/test-spec-page.sh`. No governance tier — this repo's constitution is still the
unfilled template, so there is nothing ratified to check compliance against.

**Target Platform**: Any Spec Kit project with the extension installed. The manifest and command
file are agent-neutral per the extension schema; this repo's own `.specify/init-options.json`
targets Claude (`ai_skills: true`, `integration: claude`), so the command is authored and
hand-verified against Claude's skills-mode rendering first.

**Project Type**: Spec Kit extension — single flat-at-root package (manifest + one command +
tests), matching the official `extensions/template/` scaffold. No companion preset, since nothing
here needs a `prepend`/`append`/`wrap` template strategy (extension-provided templates are always
`replace`, which is sufficient — this feature adds no template at all).

**Performance Goals**: N/A in the systems sense (no throughput/latency target — this is a
conversational feature). SC-001 gives the relevant target: a full five-question session completes
in under 10 minutes assuming no more than one or two retries per level.

**Constraints**: Zero persistence (FR-012, SC-005, and FR-022 for the page); zero blocking of any
other Spec Kit command (FR-016, SC-004); no required external tool/service dependency
(Assumptions — `python3` is optional and its absence changes nothing); no attempt cap on retries
(FR-009); mandatory auto-fire on `after_specify` with no confirmation prompt (`optional: false` —
the automatic, unprompted nature is the feature's core value proposition, not an interruption to
soften).

**Scale/Scope**: One extension, one command (+ one alias), one mandatory hook, zero config
surface, one optional script (the spec page helper), zero additional templates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled `[PROJECT_NAME] Constitution` template —
no principles have been ratified for this project. There is nothing to gate against, so this
check trivially passes and is not re-evaluated post-design. (This is also why the test suite in
this plan has no governance tier — see Technical Context › Testing.)

## Project Structure

### Documentation (this feature)

```text
specs/001-know-your-spec/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/            # Phase 1 output (/speckit-plan command)
│   ├── extension.yml     # Design-phase copy of the manifest to be shipped at repo root
│   └── command-interface.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

The shipped extension is flat at the repository root — this is the canonical layout for a
standalone single-extension repo (confirmed against the official `extensions/template/` scaffold,
not analogized from a multi-artifact monorepo precedent):

```text
extension.yml                              # Manifest: id, commands, scripts, hooks, tags
commands/
└── speckit.know-your-spec.check.md        # The Comprehension Checkpoint command
scripts/
└── python/
    └── specpage.py                        # The read-only spec page helper (User Story 4)
.extensionignore                            # Excludes specs/, tests/, .specify/, .claude/, .git/, caches from installs
README.md
LICENSE                                     # MIT
CHANGELOG.md
tests/
├── run.sh
├── deterministic/                          # Manifest/command-file structural checks; runs tests/unit/
├── unit/                                   # Python unit tests for the spec page helper
└── judgment/
    ├── eval.sh
    ├── fixtures/                           # This repo's own spec.md + 2-3 synthetic specs
    └── expected/                           # Hand-authored ground truth (authored solely by
                                             # the extension author, no separate review pass)
specs/                                      # This project's own Spec Kit artifacts — dev-only,
                                             # excluded from installs via .extensionignore
```

**Structure Decision**: Single flat-at-root Spec Kit extension package, no companion preset. The
one script lives at `scripts/python/specpage.py` and is declared under `provides.scripts`. `.extensionignore` keeps `specs/`, `tests/`, `.specify/`, and `.claude/` out
of what `specify extension add` copies into a consumer's `.specify/extensions/know-your-spec/`.

## Complexity Tracking

*No constitution violations — this section is not applicable.*
