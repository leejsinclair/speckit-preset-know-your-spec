# Quickstart: Validating the Spec Comprehension Check Extension

This is a runnable validation guide, not an implementation walkthrough — it proves the feature
works end-to-end against the contracts in `contracts/` and the requirements in `spec.md`. Full
implementation detail belongs in `tasks.md` and the extension's own files, not here.

## Validation status (T035)

What's been validated automatically as part of implementation, and what still needs a live
interactive session (this checkpoint is conversational — no shell script can simulate a
multi-turn developer/agent exchange):

- **Step 1 (Install)** — validated for real: `specify extension add --dev` into a scratch
  project registered `speckit.know-your-spec.check` / `speckit.kys-check`, a mandatory
  (`optional: false`) `after_specify` hook, and rendered both Claude skill files correctly, with
  `.extensionignore` correctly keeping `specs/`, `tests/`, `.specify/`, `.claude/` out of the
  installed copy.
- **Automated test suite** (`tests/run.sh`) — validated for real, full green as of last run:
  deterministic tier 2/2, judgment tier 4/4 fixtures at 100% derivation agreement and 5/5
  behavioral probes passing. Re-run `tests/run.sh` for the current, authoritative result rather
  than trusting this as a permanent snapshot — it will drift if `commands/speckit.know-your-spec.
  check.md` changes later.
- **Steps 2-8 (the conversational scenarios)** — the judgment-tier behavioral probes
  (`tests/judgment/probes/*.md`) are the closest automated proxy for these: `coaching-retry`
  covers step 2, `skip-reveal` covers step 5, `out-of-scope-answer` and
  `no-implementation-questions` cover FR-011/Edge Cases, `repair-approval` covers step 4. A full
  live walkthrough of an actual multi-turn `/speckit-know-your-spec-check` session (steps 2, 3,
  6, 7, 8 exactly as narrated below) still needs a real interactive agent session — that's outside
  what any script in `tests/` can execute, and is the one piece of T035 left for a human (or a
  live agent session) to run.

## Prerequisites

- Spec Kit CLI installed (`specify`, confirmed at v1.0.2.dev0 for this project).
- A checkout of this repository with the extension package built at its root (`extension.yml`,
  `commands/speckit.know-your-spec.check.md`, `.extensionignore`).
- A second, throwaway Spec Kit project (or this repo's own `.specify/` setup) to install the
  extension into for testing — installing into the same repo that authors it is fine for
  dev-loop validation, since `.extensionignore` keeps the dev-only content out either way.

## 1. Install the extension (dev mode)

```bash
specify extension add --dev /home/lee/projects/speckit-preset-know-your-spec
```

**Expected outcome**: `speckit.know-your-spec.check` (and alias `speckit.kys-check`) are
registered; `.specify/extensions.yml` in the target project gains an `after_specify` hook entry
with `optional: false`. No config file is materialized (this extension ships none).

## 2. Automatic trigger — Scenario: Take the comprehension checkpoint on a finished spec (User Story 1)

```bash
/speckit-specify "some small test feature description"
```

**Expected outcome**: immediately after the spec is written, the checkpoint fires automatically
(no confirmation prompt — `optional: false`) and presents question 1, derived from specific
content in the just-written `spec.md`.

- Answer question 1 incorrectly/incompletely.
- **Expected**: a coaching hint naming the specific gap (without revealing the full answer),
  pointing at a `spec.md` heading, followed by a *newly-worded* question at the same difficulty
  level (FR-008).
- Answer the reworded question correctly.
- **Expected**: the checkpoint advances to question 2 — the retry did not count as, or replace,
  one of the five levels (FR-009, Acceptance Scenario 3).

## 3. Difficulty progression (User Story 2)

Continue the session from step 2 through all five questions.

**Expected outcome**:
- Questions appear in fixed order: Recognise → Explain → Apply → Trace → Evaluate, never
  regressing to an earlier level (FR-006).
- Question 1/2 are multiple-choice when the underlying content supports plausible, mutually
  exclusive options; free-text otherwise. Questions 3-5 are always free-text (FR-005).

To exercise the free-text fallback for questions 1-2, run against a synthetic fixture spec whose
Recognise/Explain-level content doesn't lend itself to plausible distractors (see
`tests/judgment/fixtures/`) and confirm a free-text question is presented instead of forcing
implausible multiple-choice options.

## 4. Repair-approval path (User Story 3)

Run the checkpoint against a spec with a deliberately thin or ambiguous section (a
`tests/judgment/fixtures/` synthetic case) at one of the five difficulty levels.

**Expected outcome**:
- Before question 1, the command presents a consolidated repair/clarification proposal for that
  section and waits for explicit approval (FR-003, research.md §7).
- **Approve**: confirm the repair is applied to `spec.md`, then a question is asked from the
  now-established content.
- **Decline** (run again, decline this time): confirm the command substitutes a question from
  different already-established content at that level, or — for a fixture with genuinely no
  alternative content at that level — confirm it says so plainly rather than asking an untruthful
  question (Edge Cases).
- In both the approve and decline paths, confirm `git diff` shows **no** new questions, answers,
  scores, or completion markers anywhere in the repo — only the approved content repair itself,
  if any was approved (FR-012, SC-005).

## 5. Skip/reveal (FR-010)

During any question, answer incorrectly several times, then explicitly ask to skip/reveal that
question.

**Expected outcome**: the session records that question as `skipped` (not `passed`) and advances
to the next level without ending the whole session.

## 6. Early exit (FR-014)

Start a session, answer one question, then explicitly ask to stop.

**Expected outcome**: the session ends immediately. `git status`/`git diff` show nothing new
anywhere in the repo related to the checkpoint (no partial summary, no partial record).

## 7. Non-blocking behavior (FR-016, SC-004)

With the extension installed but *without* ever running the checkpoint manually or letting the
automatic hook run to completion (exit early per step 6), run the full remaining Spec Kit
lifecycle:

```bash
/speckit-plan
/speckit-tasks
/speckit-implement
```

**Expected outcome**: every command behaves exactly as it would with the extension not installed
at all — no blocking, no required checkpoint completion, no altered output.

## 8. Completion summary (FR-013)

Run a full five-question session to completion (mixing at least one `passed` and one `skipped`
outcome).

**Expected outcome**: a concise, session-only summary is presented distinguishing passed
questions from skipped ones — spoken in the conversation only, never written to any file.

## 9. The spec page (User Story 4)

Needs `python3`. Start a checkpoint and, when asked "Open the spec on a page in your browser, or
stay in chat?", choose the page.

**Expected outcome**: the agent gives an address ending in `?t=…` and does not claim to have
opened it; opening it shows the spec rendered, read-only, with any diagram drawn. Question 1
follows in the conversation. Answer a question wrongly: the coaching pointer includes a link that
opens the page at the heading. Edit `spec.md`: within a few seconds the page says the spec has
changed and offers to reload. End the session: `git status` shows nothing from the page, and
`python3 .specify/extensions/know-your-spec/scripts/python/specpage.py serve --spec <spec.md>
--status` reports that no page is running.

Without `python3` on `PATH`, the question is not asked and the checkpoint is as in steps 2-8.

## Automated test suite

```bash
tests/run.sh
```

Runs both tiers: `tests/deterministic/` (manifest and command-file structural checks, and the
spec page's Python unit tests in `tests/unit/`) and
`tests/judgment/` (single-shot derivation-quality evals against `tests/judgment/expected/`, plus
isolated single-turn behavioral probes for the coaching/retry/skip/repair-approval rules — see
research.md §13 for why this feature uses a hybrid eval design rather than the reference
precedent's single-shot-only approach).
