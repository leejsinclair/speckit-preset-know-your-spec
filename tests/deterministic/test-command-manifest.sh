#!/bin/sh
# Structural checks on extension.yml and the command file — no LLM invocation, pure text/YAML
# assertions. Exit 0 on success, non-zero with a message on the first failure.
set -eu

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$ROOT/extension.yml"
CMD_FILE="$ROOT/commands/speckit.know-your-spec.check.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$MANIFEST" ] || fail "extension.yml not found at repo root"
[ -f "$CMD_FILE" ] || fail "command file not found: $CMD_FILE"

# extension.yml: primary command name matches speckit.<id>.<cmd>
grep -q 'name: "speckit.know-your-spec.check"' "$MANIFEST" \
  || fail "extension.yml missing primary command name speckit.know-your-spec.check"

# extension.yml: alias present
grep -q 'speckit.kys-check' "$MANIFEST" \
  || fail "extension.yml missing alias speckit.kys-check"

# extension.yml: id matches ^[a-z0-9-]+$
EXT_ID=$(grep -m1 '^\s*id:' "$MANIFEST" | sed -E 's/.*id:\s*"?([a-z0-9-]+)"?.*/\1/')
echo "$EXT_ID" | grep -Eq '^[a-z0-9-]+$' \
  || fail "extension id '$EXT_ID' does not match ^[a-z0-9-]+\$"

# extension.yml: after_specify hook is mandatory (optional: false)
awk '/after_specify:/{found=1} found && /optional:/{print; exit}' "$MANIFEST" \
  | grep -q 'optional: false' \
  || fail "after_specify hook is not optional: false (mandatory auto-fire is required — research.md §3)"

# extension.yml: the spec page helper is declared, shipped, and never required (research.md §15)
grep -q 'file: "scripts/python/specpage.py"' "$MANIFEST" \
  || fail "extension.yml does not declare scripts/python/specpage.py under provides.scripts"
[ -f "$ROOT/scripts/python/specpage.py" ] \
  || fail "scripts/python/specpage.py is declared in extension.yml but missing"
awk '/name: "python3"/{found=1; next} found{print; exit}' "$MANIFEST" \
  | grep -q 'required: false' \
  || fail "python3 must be an optional tool (required: false) — the checkpoint works without the spec page"
grep -q '.specify/extensions/know-your-spec/scripts/python/specpage.py' "$CMD_FILE" \
  || fail "command file does not call the spec page helper at its installed path"

# command file: frontmatter present and closed, description non-empty
FIRST_LINE=$(head -n1 "$CMD_FILE")
[ "$FIRST_LINE" = "---" ] || fail "command file does not start with YAML frontmatter delimiter"

FRONTMATTER=$(awk '/^---$/{n++; next} n==1' "$CMD_FILE")
echo "$FRONTMATTER" | grep -Eq '^description:\s*".+"' \
  || fail "command file frontmatter missing a non-empty description"

# command file: any line instructing a write to spec.md/a file must be part of the explicitly-
# approved repair path, never generic session bookkeeping (FR-012 / SC-005 — see also
# test-no-persistence.sh for the more thorough version of this check)
WRITE_LINES=$(grep -iE '(write|save|append).{0,40}(spec\.md|to (a|the) file)' "$CMD_FILE" || true)
if [ -n "$WRITE_LINES" ]; then
  BAD_LINES=$(echo "$WRITE_LINES" | grep -viE 'approved repair|developer-approved|never write|do not write' || true)
  [ -z "$BAD_LINES" ] || fail "command file appears to instruct writing to spec.md/a file outside the approved-repair path: $BAD_LINES"
fi

echo "PASS: test-command-manifest.sh"
