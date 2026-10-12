# Phase 0 Research: Checkpoint After Clarify

The spec left no open product questions (both were settled in the clarify session of
2026-10-11). What remained were facts about Spec Kit itself, which decide how FR-025, FR-032 and
FR-033 can be met. Each was checked against two sources: the Spec Kit CLI installed on the
development machine (`specify-cli 1.0.2.dev0`, commit `51e52be`) and the upstream
`github/spec-kit` history, read at the `v1.0.0` and `v1.0.2` tags.

Sections here are cited as `specs/002-checkpoint-after-clarify/research.md §N`. A bare
`research.md §N` in a code comment still means the decision log of spec 001.

## 1. The trigger: a mandatory `after_clarify` hook

- **Decision**: Replace the manifest's `after_specify` hook with an `after_clarify` hook that
  names the same command and keeps `optional: false`.
- **Rationale**: The `/speckit-clarify` command template ends with a "Mandatory Post-Execution
  Hooks" section that reads `hooks.after_clarify` from `.specify/extensions.yml` and, for a hook
  with `optional: false`, emits `EXECUTE_COMMAND:` and runs it with no confirmation. That is the
  same mechanism the checkpoint uses today at the end of `/speckit-specify`, so FR-025 needs a
  one-key change in the manifest and no new code. The hook section sits after the "Behavior
  rules" of clarify and before its completion report, and it is listed in the template's "Done
  When" checklist, so it is reached on the three paths FR-028 names: a run that asked no
  questions, a run the developer ended early, and a repeat run.
- **Alternatives considered**:
  - Keep `after_specify` and add `after_clarify` (rejected: FR-026 says nothing happens after
    specify, and the back-to-back interruption is the problem being fixed).
  - Keep `after_specify` but make it optional, as an offer (rejected in the clarify session:
    "There is no offer").
  - A `before_plan` hook, so the checkpoint runs on the spec that is about to be planned even
    when clarification was skipped (rejected: the spec's Assumptions say no second automatic
    trigger is added, and a quiz in front of `/speckit-plan` reads as a gate, which FR-016
    forbids in spirit).

## 2. Required Spec Kit version: `>=1.0.0`, unchanged

- **Decision**: Keep `requires.speckit_version: ">=1.0.0"`. No bump is needed.
- **Rationale**: FR-033 requires a Spec Kit version that can act when `/speckit-clarify`
  finishes. Upstream history shows:
  - `hooks.after_clarify` was added to the clarify template in commit `1a9e4d1` (2026-04-07,
    "Git extension stage 1: bundled `extensions/git` with hooks on all core commands"), first
    released in `v0.5.1`.
  - The directive wording that makes a mandatory post-hook run reliably ("Mandatory
    Post-Execution Hooks", "You MUST emit `EXECUTE_COMMAND:`") arrived in commit `7a7843b`
    (2026-05-26), first released in `v0.8.15`.
  - Both are present at `v1.0.0` (2026-08-21).

  So every Spec Kit version the extension already accepts can act at the end of clarify. The
  floor FR-033 asks for is the floor that is already declared.
- **Housekeeping**: spec 001's `plan.md` says `>=1.0.2` while both manifests say `>=1.0.0`. The
  manifests are right; the plan line is corrected as part of this feature.
- **Alternatives considered**: Raising the floor to `>=1.0.2` to match the version this was
  developed on (rejected: it would refuse installs on 1.0.0 and 1.0.1 for no functional reason).

## 3. Refusal on an older Spec Kit (FR-033) is done by the CLI

- **Decision**: Rely on the Spec Kit CLI's own compatibility check. Add nothing to the extension.
- **Rationale**: `ExtensionManager.check_compatibility` compares the installed version with
  `requires.speckit_version` and raises `CompatibilityError`:
  `Extension requires spec-kit >=1.0.0, but <installed> is installed.` followed by the upgrade
  command. `specify extension add` prints it as "Compatibility Error" and exits 1. That message
  names the required version, as FR-033 asks.
  For upgrades, `specify extension update` builds the new manifest in a temporary directory and
  runs the same check "while the existing extension is still untouched", before it removes
  anything. So a refused upgrade leaves the installed version as it was. This pre-check is
  present at `v1.0.0`. The other upgrade route, `specify extension add ... --force` (the one the
  README's install line leads to, since this extension is installed from a tag zip), is safe for
  the same reason: `install_from_directory` calls `check_compatibility` before it looks at
  whether the extension is installed and before the forced removal.
- **Limit worth recording**: the check reads the version of the `specify` CLI, not the age of the
  command files already rendered into a project. A project initialised long ago and never
  refreshed could pass the check with a clarify command that predates hooks. This is the same
  exposure the `after_specify` hook has today, the fix is the normal Spec Kit upgrade, and the
  spec's Assumptions already say such a project upgrades Spec Kit first. No detection is added.
- **Alternatives considered**: A check inside the command file that inspects the project's
  clarify command (rejected: the command only runs once a hook has already fired, so it cannot
  detect a hook that never fires).

## 4. Upgrade drops the old trigger with no manual step (FR-032)

- **Decision**: No migration step, script or documentation of one. Removing `after_specify` from
  the manifest is enough.
- **Rationale**: Two independent mechanisms in the CLI remove the old registration, both present
  at `v1.0.0`:
  - `specify extension update` (and `specify extension add --force`) calls `manager.remove()`,
    which calls `unregister_hooks(extension_id)` and deletes every hook entry owned by the
    extension, then installs the new version.
  - `register_hooks` itself purges "this extension's entries from events the new manifest no
    longer declares", so even a reinstall over the top leaves no orphaned `after_specify` entry.

  After an upgrade, `.specify/extensions.yml` has one entry for this extension, under
  `hooks.after_clarify`.
- **Alternatives considered**: A note telling upgraders to edit `.specify/extensions.yml` by hand
  (rejected: unnecessary, and FR-032 forbids a manual step).

## 5. Coexistence with other extensions (FR-030)

- **Decision**: Declare the hook with no `priority` and no `condition`.
- **Rationale**: Each event in `.specify/extensions.yml` is a list. `register_hooks` only adds,
  replaces and removes entries whose `extension` is `know-your-spec`, so entries from other
  extensions on `after_clarify` or `after_specify` are untouched. The clarify template runs
  every executable hook in the list. The spec's Assumptions accept the default ordering, so no
  priority is set. The checkpoint's "never block" invariant already covers what happens after it
  ends.
- **Alternatives considered**: A low priority so the checkpoint runs last (rejected: the spec
  says ordering does not matter, and a priority is one more thing to keep right).

## 6. Quizzing on the spec as clarified (User Story 1, scenario 2)

- **Decision**: Add one instruction to the command file's Step 0: read `spec.md` from disk at the
  start of every session, and derive from that reading, not from any earlier view of the spec in
  the same conversation.
- **Rationale**: When the hook fires, the conversation already holds the spec as it was before
  and during clarification. Clarify saves the file after each accepted answer, so the file on
  disk is the settled version. Stating the re-read removes any doubt about which version the
  questions come from. It also serves the edge case "ran the checkpoint by hand, then
  clarified".
- **Alternatives considered**: Saying nothing and trusting the agent (rejected: the acceptance
  scenario is explicit, and the instruction costs one sentence).

## 7. Command file wording

- **Decision**: Edit only the Purpose paragraph, the "Trigger awareness" paragraph and Step 0.
  Steps 1 to 5 and the three invariants are untouched.
- **Rationale**: FR-027 says session behaviour is unchanged, and `test-no-persistence.sh` greps
  the invariants for specific wording. The two paragraphs that mention `after_specify` and
  `/speckit-specify` are the only text that is now wrong. The existing argument in "Trigger
  awareness" (there is never a quiet no-op, because a spec always has content to quiz on) is
  also what FR-028 needs for a clarify run that asked no questions, so it is kept and restated
  for clarify.
- **Alternatives considered**: A leave-in-one-step reminder shown only on hook-triggered runs
  (rejected: FR-027 requires identical behaviour for both ways of starting).

## 8. Tests

- **Decision**:
  - `tests/deterministic/test-command-manifest.sh`: the hook assertion changes to
    `after_clarify` with `optional: false`, and three assertions are added: the manifest declares
    no `after_specify` hook, the command file does not mention `after_specify`, and the command
    file's Step 0 says to read `spec.md` from disk (§6).
  - One new judgment probe, `tests/judgment/probes/after-clarify-start.md` (FR-025, FR-028): the
    checkpoint was started by the hook after a clarify run that asked no questions; the response
    must start the session and must not ask whether to run, or say there is nothing to check.
    The probe harness supplies no spec, so the probe states that no repairs were needed, that
    the page helper is absent and what question 1 is; starting the session then means presenting
    question 1.
  - `tests/judgment/fixtures/own-spec/spec.md` is left as it is. It is a frozen copy of spec 001
    graded against `expected/own-spec.json`; it is a quiz subject, not documentation.
- **Rationale**: CLAUDE.md asks for a probe when the command file's behaviour changes. FR-026
  (nothing after specify) is a property of the manifest, so a deterministic check is the right
  tier for it. FR-032 and FR-033 are CLI behaviours and are exercised by hand in
  `quickstart.md`.
- **Alternatives considered**: A probe for "nothing after specify" (rejected: with no hook
  registered the command never runs, so there is no response to grade).

## 9. Release

- **Decision**: 1.2.0, a minor version, as the spec's Assumptions state. The version changes in
  the four places CLAUDE.md lists: `extension.yml`, the README install URL, `CHANGELOG.md` and
  `specs/001-know-your-spec/contracts/extension.yml`.
- **Rationale**: The trigger moves; the command, its alias and manual use are unchanged. The
  changelog entry says plainly that the automatic start has moved, since a developer who never
  runs `/speckit-clarify` will stop seeing the checkpoint unless they start it by hand.
