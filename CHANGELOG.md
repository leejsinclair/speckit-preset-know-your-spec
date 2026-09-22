# Changelog

## 1.0.0 - 2026-09-22

Initial release.

- `speckit.know-your-spec.check` command (alias `speckit.kys-check`): a five-question
  Comprehension Checkpoint against `spec.md`, at fixed increasing difficulty (Recognise → Explain
  → Apply → Trace → Evaluate), judged semantically, coached with uncapped retries, explicit
  per-question skip/reveal, and a session-only completion summary.
- Mandatory `after_specify` hook — fires automatically immediately after a spec is finished, with
  no confirmation prompt.
- Developer-approval-gated repair/clarification flow for `spec.md` sections too thin or ambiguous
  to truthfully support a question, batched as one consolidated request before question 1.
- Zero persistence: nothing about a checkpoint session is ever written to `spec.md` or any other
  repository file, aside from an explicitly approved content repair.
- No config file, no companion preset — the checkpoint's mechanics are fixed by design.
