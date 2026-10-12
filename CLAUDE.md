# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A [Spec Kit](https://github.com/github/spec-kit) extension, `know-your-spec`. It adds one command, the Comprehension Checkpoint, which quizzes the developer on a finished `spec.md` (five questions, fixed order Recognise → Explain → Apply → Trace → Evaluate) and fires automatically through a mandatory `after_clarify` hook. There is no build step: the shipped product is a manifest, a prompt file and one standard-library Python script.

## Commands

```bash
tests/run.sh                        # deterministic tier, then judgment tier
tests/run.sh --deterministic-only   # no claude CLI, no tokens; run this after every change

# One deterministic check
tests/deterministic/test-command-manifest.sh

# Spec page unit tests (run from the repo root; -t . is required)
python3 -m unittest discover -s tests/unit -t .
python3 -m unittest tests.unit.test_page_server
python3 -m unittest tests.unit.test_markdown.<Class>.<test_name>

# Judgment tier, narrowed (calls `claude -p`, costs real tokens)
tests/judgment/eval.sh --derivation-only --fixture thin-section
tests/judgment/eval.sh --probes-only --probe coaching-retry

# Install into a Spec Kit project to try it
specify extension add --dev /path/to/speckit-preset-know-your-spec

# Run the spec page by hand from this repo
python3 scripts/python/specpage.py serve --spec specs/001-know-your-spec/spec.md
python3 scripts/python/specpage.py serve --spec specs/001-know-your-spec/spec.md --status
python3 scripts/python/specpage.py serve --spec specs/001-know-your-spec/spec.md --stop
```

## Architecture

Three shipped pieces, and they are coupled by text, not by imports:

- `extension.yml`: the manifest. Declares the command (`speckit.know-your-spec.check`, alias `speckit.kys-check`), the `specpage` script, the `after_clarify` hook (`optional: false`), and `python3` as an optional tool.
- `commands/speckit.know-your-spec.check.md`: the checkpoint itself. This is a prompt, and it is the product's behaviour. Steps 0 to 5 plus three invariants (never persist, never block, never advance silently).
- `scripts/python/specpage.py`: the optional read-only spec page. One file, standard library only, Python 3.11+. It contains a Markdown renderer (copied from the engineer-in-the-loop extension's `eil/pagerender.py`; the module docstring records provenance and adaptations), the page template, and an `HTTPServer` with a `Host` check and a one-time token on every request.

Things that span files and are easy to break:

- **Installed path.** The command file calls the helper as `python3 .specify/extensions/know-your-spec/scripts/python/specpage.py serve ...`, the path it has after install, not its path in this repo. `test-command-manifest.sh` fails on any call that omits `python3` or the installed path.
- **Zero persistence.** Nothing about a checkpoint session may be written to the repository; the only exception is a developer-approved repair to `spec.md`. `test-no-persistence.sh` greps the command file for specific wording (`never write/persist`, `conversation-only`, the approved-repair exception), so rewording the prompt can fail tests even when the meaning is unchanged. The spec page keeps its runtime file (address, token) in the OS temp directory and refuses to start (`no-runtime-dir`) rather than write inside the project.
- **Page and command contract.** `serve` prints one JSON line with `address` and `anchors`; the command file uses `anchors` to build links to headings in coaching hints. Changing the JSON shape or anchor generation means changing the command file too.
- **Defaults that are deliberate.** The page binds `0.0.0.0` so a forwarded port from a container works; Mermaid (`mermaid@11` from jsDelivr) is loaded only when the spec has a diagram, with the source shown as fallback. The mechanics (five questions, fixed order, uncapped retries) are fixed, so there is no config file.
- **What ships.** `.extensionignore` keeps `specs/`, `tests/`, `.specify/`, `.claude/`, `CLAUDE.md` and `insights/` out of installs. Anything new at the repo root ships unless added there. `CLAUDE.md` and `insights/` are listed too.
- **Two research logs.** A bare `research.md §N` means spec 001's. Spec 002's is cited by its full path, `specs/002-checkpoint-after-clarify/research.md`.

`specs/001-know-your-spec/` holds this project's own Spec Kit artifacts. `research.md` is the decision log that code comments cite as `research.md §N` (§13 covers the test design, §15 the spec page). `contracts/extension.yml` is a design-phase copy kept for traceability; the root `extension.yml` is the live one. Keep the spec artifacts in step with behaviour changes (FR and SC ids are referenced from tests and probes).

## Tests

Two tiers. The deterministic tier is shell checks on the manifest and command file plus the `tests/unit/` suite for the page. The judgment tier (`tests/judgment/eval_impl.py`) runs `claude -p` twice per case, once to produce output and once to grade it: fixtures in `fixtures/<name>/spec.md` are graded against hand-authored `expected/<name>.json` (fails under 80% agreement), and single-turn probes in `probes/*.md` are graded against their `assert` lines (schema in `probes/README.md`). A behaviour change in the command file usually needs a new or updated probe.

`eval_impl.py` imports `yaml`, so the judgment tier needs PyYAML in whichever `python3` is on PATH. If many tests fail at once, check the interpreter and dependencies before concluding the code is broken.

## Releasing

The version lives in `extension.yml`, the README install URL, `CHANGELOG.md` and `specs/001-know-your-spec/contracts/extension.yml`; update them together. Releases are git tags (`v1.1.2`) installed from the GitHub tag zip.

## Working agreements

These come from a review of past sessions (`insights/claude-code-insights-2026-10-10.md`).

- **Stopping servers.** Stop the spec page with `serve --spec <path> --stop`. Never use `pkill -f <pattern>`: it has matched and killed Claude's own shell. For anything else, find the PID by port (`lsof -ti:<port>`) and kill that PID in a separate command from whatever must run next. After a restart, confirm the page is serving the new code before testing.
- **Verification.** For any change to the page's rendering, layout or Mermaid handling, open the page in a real browser and look at it, in addition to the unit tests. If no browser is available, say so in the summary and list what was not checked visually. Do not report something as working on the strength of scripts alone.
- **Git.** Commit and push only when asked, and push to the branch named. Do not create a new branch unless asked; if pushing to `main` seems risky, ask first. Check `git status` for unrelated changes and ignored files before committing or rebasing.
- **Scope.** Do what was asked: do not leave out part of a requested feature (for example when porting code from another extension) or add extras without flagging it first. In docs and prose, no em dashes and no AI writing tells.
- **Diagnosis.** If a diagnosis stalls or the user disagrees with it, restate their point in your own words before defending the current theory.
