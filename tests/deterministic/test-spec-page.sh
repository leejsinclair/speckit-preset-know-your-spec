#!/bin/sh
# Unit tests for the read-only spec page helper (scripts/python/specpage.py): the copied Markdown
# renderer, the server's refusals, and that serving writes nothing to the project. Standard
# library only — no claude CLI, no tokens. Skipped with a message when python3 isn't available,
# since python3 is an optional tool for this extension (research.md §15).
set -eu

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "SKIP: test-spec-page.sh ('python3' not found on PATH)"
  exit 0
fi

if ! (cd "$ROOT" && python3 -m unittest discover -s tests/unit -t . 2>&1); then
  echo "FAIL: spec page unit tests failed — see above" >&2
  exit 1
fi

echo "PASS: test-spec-page.sh"
