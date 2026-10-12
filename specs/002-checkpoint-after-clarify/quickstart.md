# Quickstart: validating Checkpoint After Clarify

How to prove the feature works once it is implemented. The trigger contract is in
[contracts/trigger.md](./contracts/trigger.md); the reasoning behind each expectation is in
[research.md](./research.md).

## Prerequisites

- Spec Kit CLI `>=1.0.0` (`specify version`).
- This repository checked out, with the change implemented.
- A throwaway Spec Kit project to install into. Do not use this repository: scenarios 4 and 5
  install and remove versions of the extension.

```bash
mkdir /tmp/kys-scratch && cd /tmp/kys-scratch && specify init --here --ai claude
```

`REPO` below is the path to this repository.

## 0. Automated checks

```bash
tests/run.sh --deterministic-only
tests/judgment/eval.sh --probes-only --probe after-clarify-start
```

**Expected**: the deterministic tier passes, including the new assertions that the manifest
declares `after_clarify` (`optional: false`) and no `after_specify`, that the command file does
not mention `after_specify`, and that its Step 0 says to read `spec.md` from disk. The probe
passes.

## 1. Fresh install registers the right hook (FR-025, FR-026)

```bash
cd /tmp/kys-scratch
specify extension add --dev "$REPO"
grep -n -B1 -A8 "know-your-spec" .specify/extensions.yml
```

**Expected**: exactly one hook entry with `extension: know-your-spec`. It is under
`after_clarify` and has `optional: false`. There is no `know-your-spec` entry under
`after_specify`.

## 2. Nothing after specify (User Story 2, SC-010)

In an agent session in the scratch project:

```text
/speckit-specify "a small test feature"
```

**Expected**: the spec is written and the command reports completion. No checkpoint question, no
offer and no message from Know Your Spec appears.

The case where another extension has an interactive `after_specify` step is scenario 8.

## 3. Checkpoint after clarify (User Story 1, SC-009)

```text
/speckit-clarify
```

Answer the questions it asks.

**Expected**: when clarification finishes, the checkpoint starts without asking whether to run.
Any proposed repairs come first, then the spec page offer, then question 1. The questions
reflect the clarified spec: at least one answer given during clarification should be visible in
what is asked or in the expected answers.

Then check the three variants in FR-028:

- Run `/speckit-clarify` again on the same spec. If it reports no critical ambiguities, the
  checkpoint still starts.
- Run `/speckit-clarify` and reply "done" at the first question. The checkpoint still starts.
- In each case, reply "stop" at question 1. The session ends at once and `git status` shows
  nothing from the checkpoint.

## 4. Upgrade from 1.1.2 drops the old trigger (FR-032)

```bash
cd /tmp/kys-scratch
specify extension remove know-your-spec --force
specify extension add know-your-spec --from https://github.com/leejsinclair/speckit-preset-know-your-spec/archive/refs/tags/v1.1.2.zip
grep -n -B1 -A8 "know-your-spec" .specify/extensions.yml    # entry is under after_specify
specify extension add --dev "$REPO" --force
grep -n -B1 -A8 "know-your-spec" .specify/extensions.yml
```

**Expected**: after the second `add`, the only `know-your-spec` entry is under `after_clarify`.
Nothing was edited by hand.

## 5. Refusal on a Spec Kit that is too old (FR-033)

Downgrading the CLI is not practical on a development machine, so the refusal is exercised with
a copy of the extension whose requirement the installed CLI cannot meet. Start from the state
scenario 4 left (1.2.0 installed).

```bash
cp -r "$REPO" /tmp/kys-too-new
sed -i 's/speckit_version: ">=1.0.0"/speckit_version: ">=99.0.0"/' /tmp/kys-too-new/extension.yml
cd /tmp/kys-scratch
cp .specify/extensions.yml /tmp/extensions-before.yml
specify extension add --dev /tmp/kys-too-new --force; echo "exit=$?"
diff /tmp/extensions-before.yml .specify/extensions.yml && echo unchanged
```

**Expected**: `Compatibility Error: Extension requires spec-kit >=99.0.0, but <installed> is
installed.`, `exit=1`, and `unchanged`. `/speckit-kys-check` still runs in the scratch project.

## 6. Manual start without clarifying (User Story 3)

Write a new spec with `/speckit-specify`, do not clarify, then:

```text
/speckit-kys-check
```

**Expected**: a full session runs.

## 7. Same session either way (SC-011), nothing else changed (SC-013)

- Compare the session from scenario 3 with the one from scenario 6: five questions, order
  Recognise, Explain, Apply, Trace, Evaluate, in both.
- After each, `git status --porcelain` in the scratch project lists nothing written by the
  checkpoint (an approved repair to `spec.md` is the one allowed difference).
- Run `/speckit-plan` after skipping or abandoning a checkpoint. It behaves as it does in a
  project without the extension.

## 8. Another extension at the same points (FR-030, SC-012)

A stand-in for a second extension: one throwaway command and two hand-written hook entries. Run
this last, from the state scenario 5 left (1.2.0 installed).

Create the command in the scratch project:

```bash
cd /tmp/kys-scratch
mkdir -p .claude/skills/speckit-other-ping
cat > .claude/skills/speckit-other-ping/SKILL.md <<'EOF'
---
name: "speckit-other-ping"
description: "Stand-in for another extension's interactive step."
---

Say exactly "OTHER EXTENSION RAN", then ask the developer to reply "ok", and wait for the reply.
EOF
```

In `.specify/extensions.yml`, add one entry under `hooks.after_specify` and one under
`hooks.after_clarify`. Copy the shape of the `know-your-spec` entry and change `extension` to
`other-ext`, `command` to `speckit.other.ping` and the description; keep `optional: false`.

**Registration is left alone:**

```bash
grep -B2 -A8 "other-ext" .specify/extensions.yml > /tmp/other-before.txt
specify extension add --dev "$REPO" --force
grep -B2 -A8 "other-ext" .specify/extensions.yml > /tmp/other-after.txt
diff /tmp/other-before.txt /tmp/other-after.txt && echo unchanged
```

**Expected**: `unchanged`. Both `other-ext` entries are as they were written, and the
`know-your-spec` entry is still the only one of its own, under `after_clarify`.

**Both run:** in an agent session in the scratch project:

```text
/speckit-specify "another small test feature"
```

**Expected**: "OTHER EXTENSION RAN" and its request for "ok" appear. That is the only
interactive step; no checkpoint follows it (SC-012).

```text
/speckit-clarify
```

**Expected**: when clarification finishes, "OTHER EXTENSION RAN" appears and the checkpoint
starts. Either order is acceptable. Leaving the checkpoint with "stop" does not prevent the other
step from running, and replying "ok" to the other step does not prevent the checkpoint.

If the stand-in entries are ignored because `other-ext` is not an installed extension, repeat
this scenario with any real extension that declares `after_specify` and `after_clarify` hooks,
and say so in the summary.

## Documentation check (FR-031)

```bash
grep -rn "after_specify" README.md CHANGELOG.md CLAUDE.md extension.yml commands \
  specs/001-know-your-spec
```

**Expected**: the only hits are history:

- `CHANGELOG.md`: the 1.0.0 entry, and the 1.2.0 entry if it names the old hook.
- `specs/001-know-your-spec/tasks.md`: completed tasks, which record what was built at the time.
- `specs/001-know-your-spec/research.md` §3: the original decision text and the note saying spec
  002 changed the hook event.

Spec 001 FR-015 describes the new timing and points to this spec.
