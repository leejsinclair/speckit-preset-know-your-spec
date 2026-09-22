#!/bin/sh
# Asserts the command file positively authors the "never persist" guard (FR-012, SC-005), and
# doesn't reference writing questions/answers/scores/completion markers anywhere outside the
# explicitly-approved spec.md repair path.
set -eu

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CMD_FILE="$ROOT/commands/speckit.know-your-spec.check.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$CMD_FILE" ] || fail "command file not found: $CMD_FILE"

# An explicit "never persist" instruction must exist (not merely emergent from omission).
grep -qiE 'never (write|persist)' "$CMD_FILE" \
  || fail "command file has no explicit 'never write/persist' instruction (FR-012)"

# The completion summary step must say it's conversation-only.
grep -qiE 'conversation.only|spoken.in.conversation' "$CMD_FILE" \
  || fail "command file doesn't mark the completion summary as conversation-only (FR-013)"

# The only sanctioned exception to the no-write rule must be named explicitly. Normalize
# whitespace first since the source is hand-wrapped Markdown and the phrase may span lines.
NORMALIZED=$(tr '\n' ' ' < "$CMD_FILE" | tr -s ' ')
echo "$NORMALIZED" | grep -qiE 'exception.{0,60}approved repair|approved repair.{0,60}exception' \
  || fail "command file doesn't scope the approved-repair exception explicitly (FR-003 vs FR-012)"

# No stray reference to a persistence mechanism this feature explicitly rejects.
if grep -qiE '(record|log|history)\s+(file|entity)|Comprehension Record' "$CMD_FILE"; then
  fail "command file references a persisted record/log entity — this feature is session-only"
fi

echo "PASS: test-no-persistence.sh"
