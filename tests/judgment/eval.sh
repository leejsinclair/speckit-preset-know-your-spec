#!/bin/sh
# eval.sh — Judgment tier (research.md §13: hybrid derivation-quality eval + single-turn
# behavioral probes, following the reference precedent's `claude -p --output-format json
# --json-schema` pattern for the derivation half).
#
# This tier is NOT dependency-free (unlike deterministic/): it requires the `claude` CLI with API
# access and costs real tokens per run — evaluating judgment inherently needs a judge.
#
# Usage:
#   eval.sh [--derivation-only] [--probes-only] [--fixture <name>] [--probe <name>]
#
# Exit code: non-zero if the derivation-quality agreement rate falls below 80% (mirroring the
# reference precedent's SC-016 target) or any probe assertion fails.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if ! command -v claude >/dev/null 2>&1; then
  echo "eval.sh: 'claude' CLI not found on PATH — the judgment tier requires it to run real evals" >&2
  exit 1
fi

exec python3 "$SCRIPT_DIR/eval_impl.py" "$@"
