# Phase 0 Research: Spec Comprehension Check

All unknowns below were resolved through a direct design-tree interview with the developer
(14 rounds, one question per round) rather than open-ended agent research, plus targeted
fact-finding against the installed Spec Kit CLI source and the official `extensions/` scaffold
where the interview needed a verified fact rather than a judgment call. Each entry gives the
decision, rationale, and rejected alternative(s).

## 1. Delivery mechanism: extension only, no companion preset

- **Decision**: Ship as a Spec Kit extension exclusively.
- **Rationale**: Extensions independently carry commands, hooks, and scripts. The only reason
  the reference precedent (Questmaster) needed a companion preset was its `prepend` addendum onto
  `spec-template.md` — a composable template strategy only presets support (extension-provided
  templates always resolve as `replace`, confirmed directly against
  `specify_cli/extensions/__init__.py`'s `_validate_provided_artifacts`). This feature adds no
  template at all, so no preset is needed.
- **Alternatives considered**: Preset+extension bundle (rejected — unnecessary given no
  composable-template requirement); preset-only (rejected — presets cannot register hooks or
  commands).

## 2. Identity

- **Decision**: id `know-your-spec`; name "Know Your Spec"; command
  `speckit.know-your-spec.check`, alias `speckit.kys-check`; author "Lee Sinclair"; MIT license.
- **Rationale**: `id` matches the validation pattern `^[a-z0-9-]+$` and doesn't collide with
  `CORE_COMMAND_NAMES`. Primary command name follows the mandatory `speckit.{ext-id}.{command}`
  form; aliases are confirmed free-form (no pattern enforcement in the CLI source) so the alias
  can be the friendlier short form.
- **Alternatives considered**: None seriously contended — this was a naming decision, not a
  tradeoff.

## 3. Trigger behavior

- **Decision**: Mandatory (`optional: false`) `after_specify` hook — fires automatically with no
  confirmation prompt.
- **Rationale**: Explicit developer correction during the interview: "Auto fire, that why
  developers will install this" — the unprompted, automatic nature of the checkpoint is the
  feature's value proposition, not an interruption to be gated behind an opt-in prompt.
- **Alternatives considered**: `optional: true` (my initial recommendation, reasoning the
  checkpoint is a heavier interruption than typical automated hooks) — explicitly rejected by the
  developer.

## 4. Scripts

- **Decision**: No new scripts. Reuse the core `check-prerequisites.sh` to locate `spec.md`.
- **Rationale**: The command needs only to find and read `spec.md`; no scoring, config
  resolution, or record-keeping logic exists (this feature persists nothing), so there is no
  deterministic-arithmetic surface that would justify a helper script the way Questmaster's
  scoring/digest/record scripts were justified.
- **Alternatives considered**: A dedicated helper script for spec-heading lookup (rejected as
  unnecessary — the command file's own instructions are sufficient for an interactive agent
  reading a single Markdown file).

## 5. Config

- **Decision**: No config file.
- **Rationale**: The checkpoint's mechanics (5 questions, fixed difficulty order, no retry cap,
  no persistence) are fully specified and fixed by spec.md — there is no rubric or threshold to
  make tunable, unlike Questmaster's banded scoring config.
- **Alternatives considered**: A config for e.g. question count or retry limits (rejected — the
  spec fixes these values; making them configurable would contradict FR-004/FR-009 as written).

## 6. Command content

- **Decision**: Reuse the developer's own existing, battle-tested Comprehension Checkpoint prompt
  near-verbatim as the command body, folding in the three `/speckit-clarify` refinements (repair
  approval, conditional MC, explicit skip/reveal).
- **Rationale**: The prompt was supplied as the authoritative behavioral spec and had already
  been used in practice; re-deriving its mechanics from scratch would risk reintroducing the two
  wrong defaults already corrected once (a 3-attempt reveal cap, and persisted results).
- **Alternatives considered**: Writing new command content from the FRs alone (rejected — higher
  risk of drifting from proven behavior for no benefit).

## 7. Repair-approval UX

- **Decision**: Derive all needed `spec.md` repairs upfront, present them as one consolidated
  approval request, before question 1 of the quiz begins.
- **Rationale**: FR-002/FR-003 require expected answers and supporting headings to be derived
  privately before any question is presented; batching the repair proposals avoids interrupting
  the quiz flow mid-session with individual approval prompts.
- **Alternatives considered**: Per-question, just-in-time repair proposals (rejected — spreads
  interruptions across the whole session instead of concentrating them before it starts).

## 8. Repository setup

- **Decision**: Initialize git locally now; no GitHub remote yet.
- **Rationale**: Developer confirmed no remote exists yet ("Sure, but I have not set it up on
  GitHub yet"). `repository:` in the manifest is still filled in for forward compatibility with
  eventual publishing, but nothing depends on the remote existing today.
- **Alternatives considered**: Deferring git init entirely until a remote exists (rejected —
  local version control has no reason to wait on remote setup).

## 9. Repository layout

- **Decision**: Flat-at-root layout (`extension.yml`, `commands/`, `README.md`, `LICENSE`,
  `CHANGELOG.md` all at repo root) with a single root-level `.extensionignore`.
- **Rationale**: Verified directly against the official `github/spec-kit` `extensions/template/`
  scaffold — its own setup instructions (`cp -r extensions/template my-extension; cd
  my-extension`) confirm the template directory *becomes* the new repo root for a standalone
  single-extension repo. The reference precedent's subdirectory layout
  (`extensions/questmaster/`) was only forced by also needing a root-level `preset.yml` for its
  companion preset — a constraint this feature doesn't have (see §1).
- **Alternatives considered**: Subdirectory layout mirroring the reference precedent (my initial
  recommendation) — corrected after the developer asked for direct verification against the real
  upstream `extensions/` directory rather than analogizing from the nearest example on hand.

## 10. Testing depth

- **Decision**: Full two-tier investment — deterministic tests plus judgment-tier evals — matching
  the reference precedent's approach.
- **Rationale**: Explicit developer correction ("c + b") after my initial recommendation
  (deterministic-only, reasoning judgment evals are expensive/hard to pin down for conversational
  behavior) was rejected.
- **Alternatives considered**: Deterministic-only (my initial recommendation — rejected).

## 11. Test tiers

- **Decision**: `deterministic/` + `judgment/` only; no `governance/` tier.
- **Rationale**: This repo's constitution is still the unratified placeholder template (confirmed
  by reading `.specify/memory/constitution.md`) — there are no ratified principles to check
  compliance against, so a governance tier would have nothing to assert.
- **Alternatives considered**: Including an empty/placeholder governance tier for structural
  parity with the precedent (rejected as pointless — nothing to check).

## 12. Judgment fixtures

- **Decision**: This repo's own `spec.md` plus 2-3 synthetic specs constructed specifically to
  force the repair-approval and MC-fallback code paths.
- **Rationale**: A single real fixture (this repo's own spec) doesn't exercise the conditional MC
  fallback (FR-005) or the repair-approval/decline paths (FR-003, and the "no alternative content
  exists" edge case) since this spec's own content is already complete and MC-friendly; synthetic
  fixtures are needed to force those branches.
- **Alternatives considered**: Real specs only, pulled from other projects (rejected — no
  guarantee of hitting the specific edge-case branches needed for full FR coverage).

## 13. Judgment eval design

- **Decision**: Hybrid — a single-shot derivation-quality eval (questions/answers/headings as
  structured JSON, graded by a second `claude -p` judge call against explicit rule-adherence
  criteria — level/order, format defensibility, heading traceability, factual accuracy — with the
  hand-authored expected output supplied as ONE illustrative valid derivation rather than the
  sole correct answer to diff against, following the reference precedent's `claude -p
  --output-format json --json-schema` pattern) plus isolated single-turn behavioral probes for
  the coaching/retry/skip/repair-approval rules — not a fully simulated multi-turn session
  end-to-end.
- **Correction (post-implementation)**: an initial exact-content-diff version of this judge
  graded a real run at only 55% agreement despite the derivation being independently sound,
  because the Explain/Apply/Evaluate levels legitimately support multiple different valid
  questions from the same spec, and the model chose different (but equally valid) source content
  than the hand-authored ground truth for 3 of 5 questions. Diffing against one hand-picked
  instantiation of an open-ended generation task produces false negatives; grading against the
  rules the command must actually satisfy, with ground truth as a reference rather than an
  answer key, is the correct design and is what's implemented in `eval_impl.py`.
- **Correction #2 (post-implementation, full-suite run)**: the first full run of all 4 fixtures +
  5 probes surfaced two more harness bugs, both fixed in `eval_impl.py`/the probe file, not the
  command: (a) `DERIVATION_SCHEMA` had no `options`/`correct_option_index` fields, so a
  legitimately multiple-choice derivation had nowhere to put its options and was then marked
  "MC-in-name-only" by the judge — fixed by adding those fields and requiring them when
  `format="multiple-choice"`; (b) the derivation prompt concatenated the command instructions and
  spec.md as one undifferentiated block, and the model once cited a phrase from the command
  file's own "Invariants" section as if it were a spec.md heading — fixed by explicitly labeling
  each document's role and telling the model spec.md is the only valid citation source. A third,
  smaller fix: the `out-of-scope-answer` probe originally asserted an internal bookkeeping fact
  (a redirect doesn't consume a retry slot) that a single-turn response has no reason to state
  out loud, making the assertion unfalsifiable from response text alone — reworded to assert the
  observable absence of retry/attempt-counting language instead. After all three fixes, the full
  suite (deterministic 2/2; judgment: 4/4 fixtures at 100% agreement, 5/5 probes passing) is
  green.
- **Rationale**: The reference precedent's judgment-eval design (single-shot JSON diff per
  fixture) doesn't transfer directly to a five-question, multi-turn, stateful interactive
  checkpoint. Decomposing into (a) "does the derivation step produce correct
  questions/answers/headings" and (b) "does a single coaching/retry/skip/repair decision behave
  correctly given a specific conversational state" makes each probe independently gradable
  without needing to simulate an entire session per eval run.
- **Alternatives considered**: Full multi-turn session simulation per fixture (rejected as
  intractable to score reliably); single-shot-only, ignoring the stateful behaviors entirely
  (rejected as insufficient coverage of FR-008/FR-009/FR-010).

## 14. Judgment eval ground truth authorship

- **Decision**: The extension author drafts and finalizes both fixtures and their expected
  answers, using the FRs as the standard, with no separate developer review/correction pass
  before they're locked in as eval ground truth.
- **Rationale**: Explicit developer choice ("b"), overriding the author's initial recommendation
  of a review-gated authoring process (which reasoned that skipping review risks a
  circular/self-graded eval). This decision stands as given and is not re-litigated.
- **Alternatives considered**: Author drafts, developer reviews and corrects before lock-in (the
  author's initial recommendation — explicitly not chosen).
