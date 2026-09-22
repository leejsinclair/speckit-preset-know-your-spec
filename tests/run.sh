#!/bin/sh
# run.sh — Runs both test tiers for the Know Your Spec extension.
#
# deterministic/: dependency-free structural checks (no claude CLI, no tokens, always runs).
# judgment/: real claude -p evals against hand-authored ground truth (research.md §13); requires
#   the claude CLI with API access and costs real tokens, so it's skipped with a clear message
#   if the CLI isn't available, rather than failing the whole run.
#
# Usage: tests/run.sh [--deterministic-only]

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

echo "== Deterministic tier =="
FAILED=0
for t in "$SCRIPT_DIR"/deterministic/test-*.sh; do
  [ -e "$t" ] || continue
  if ! "$t"; then
    FAILED=1
  fi
done

if [ "$FAILED" -ne 0 ]; then
  echo "Deterministic tier FAILED — see above" >&2
  exit 1
fi

if [ "${1:-}" = "--deterministic-only" ]; then
  echo "Skipping judgment tier (--deterministic-only)"
  exit 0
fi

echo ""
echo "== Judgment tier =="
if ! command -v claude >/dev/null 2>&1; then
  echo "'claude' CLI not found on PATH — skipping judgment tier (deterministic tier passed)" >&2
  exit 0
fi

"$SCRIPT_DIR/judgment/eval.sh"
