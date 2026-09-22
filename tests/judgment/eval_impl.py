#!/usr/bin/env python3
"""
Judgment-tier eval implementation for the Know Your Spec extension (research.md §13).

Two independent passes:

1. Derivation-quality eval — for each fixtures/<name>/spec.md, asks `claude -p` to run the
   command's Step 0-2 derivation against that spec (producing the five questions, formats,
   headings, expected answers, and any proposed repairs) as structured JSON, then asks a second
   `claude -p` call to grade that output against the hand-authored tests/judgment/expected/
   <name>.json ground truth. Mirrors the reference precedent's single-shot JSON-schema-diff
   pattern (research.md §13).

2. Behavioral probes — for each probes/<name>.md, builds the `given`/`when` scenario from its
   frontmatter, asks `claude -p` to respond as the command would, then asks a second `claude -p`
   call to grade the response against every line in `assert`.

Exit code is non-zero if the derivation agreement rate falls below 80% (mirroring the reference
precedent's SC-016 target) or any probe assertion fails.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
JUDGMENT_DIR = ROOT / "tests" / "judgment"
FIXTURES_DIR = JUDGMENT_DIR / "fixtures"
EXPECTED_DIR = JUDGMENT_DIR / "expected"
PROBES_DIR = JUDGMENT_DIR / "probes"
COMMAND_FILE = ROOT / "commands" / "speckit.know-your-spec.check.md"

DERIVATION_SCHEMA = {
    "type": "object",
    "properties": {
        "repairs_proposed": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "string"},
                    "reason": {"type": "string"},
                    "proposed_repair": {"type": "string"},
                },
                "required": ["level", "reason", "proposed_repair"],
            },
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "string"},
                    "format": {"type": "string"},
                    "text": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Required and non-empty when format is multiple-choice; omit/empty for free-text.",
                    },
                    "correct_option_index": {"type": "integer"},
                    "source_heading": {"type": "string"},
                    "expected_answer": {"type": "string"},
                },
                "required": ["level", "format", "text", "source_heading", "expected_answer"],
            },
        },
    },
    "required": ["repairs_proposed", "questions"],
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "per_question_agreement": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "string"},
                    "agrees": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["level", "agrees", "notes"],
            },
        },
        "repairs_agree": {"type": "boolean"},
        "overall_agreement_pct": {"type": "number"},
        "summary": {"type": "string"},
    },
    "required": ["per_question_agreement", "repairs_agree", "overall_agreement_pct", "summary"],
}

PROBE_JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "assertion_results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "assertion": {"type": "string"},
                    "holds": {"type": "boolean"},
                    "notes": {"type": "string"},
                },
                "required": ["assertion", "holds", "notes"],
            },
        },
        "all_hold": {"type": "boolean"},
    },
    "required": ["assertion_results", "all_hold"],
}


def claude_json(prompt, schema):
    result = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--json-schema", json.dumps(schema), prompt],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed: {result.stderr}")
    try:
        outer = json.loads(result.stdout)
        return outer["structured_output"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError(f"claude -p returned no structured_output: {result.stdout[:500]}") from exc


def run_derivation_eval(fixture_names, out_dir):
    command_text = COMMAND_FILE.read_text()
    results = []
    for name in fixture_names:
        spec_path = FIXTURES_DIR / name / "spec.md"
        expected_path = EXPECTED_DIR / f"{name}.json"
        if not spec_path.exists() or not expected_path.exists():
            print(f"  skip {name}: missing spec.md or expected/{name}.json", file=sys.stderr)
            continue

        spec_text = spec_path.read_text()
        expected = json.loads(expected_path.read_text())

        derive_prompt = (
            "You are running ONLY Step 0, Step 1, and Step 2 (derivation and repair-proposal, "
            "not the question loop itself) of the following command's instructions against the "
            "given spec.md. Do not present anything to a developer — just output your derivation "
            "as structured JSON matching the schema.\n\n"
            "IMPORTANT — these are two separate documents with different roles: the command "
            "instructions below tell you HOW to derive questions; only the spec.md section after "
            "it is a valid source for a question's content or source_heading. Never cite a "
            "heading, section name, or phrase from the command instructions themselves (e.g. "
            "'Invariants', 'Step 2', 'Never persist') as if it were spec.md content — every "
            "source_heading and expected_answer must be traceable only to the spec.md text.\n\n"
            f"## Command instructions (HOW to derive — not a source of quiz content)\n\n{command_text}\n\n"
            f"## spec.md to derive against (the ONLY valid source of quiz content)\n\n{spec_text}\n\n"
            "Output the five questions (one per fixed difficulty level, in order) and any "
            "repairs you would propose before asking them. For any question with "
            "format=\"multiple-choice\", you MUST populate a non-empty `options` array (2-5 "
            "plausible, mutually exclusive choices) and `correct_option_index`; never label a "
            "question multiple-choice without options to back it."
        )
        got = claude_json(derive_prompt, DERIVATION_SCHEMA)

        judge_prompt = (
            "Grade a model's derived checkpoint questions for the given spec.md. IMPORTANT: the "
            "attached ground truth is ONE valid derivation, not the only correct one — spec.md "
            "content, especially at the Explain/Apply/Evaluate levels, can truthfully support "
            "multiple different valid questions. Do NOT mark a question wrong merely because it "
            "is grounded in different spec.md content than the ground truth chose; only mark it "
            "wrong if it violates one of these rules:\n"
            "  - Wrong difficulty level or wrong order (must be Recognise, Explain, Apply, "
            "Trace, Evaluate in that exact sequence).\n"
            "  - Indefensible format (multiple-choice used where no genuinely plausible, "
            "mutually exclusive options exist, OR multiple-choice with a missing/empty `options` "
            "array; or an Apply/Trace/Evaluate question that isn't free-text).\n"
            "  - source_heading or expected_answer cites content, section names, or phrases that "
            "only exist in the command-instructions document (e.g. 'Invariants', 'Step 2') rather "
            "than in spec.md itself — that is a fabricated citation, not a valid derivation.\n"
            "  - source_heading doesn't name real content that actually exists in the given "
            "spec.md, or doesn't topically match the question.\n"
            "  - expected_answer is factually wrong, unsupported by spec.md, or self-"
            "contradictory.\n"
            "  - The question asks about code, frameworks, libraries, database schema, or "
            "endpoint definitions (FR-011) rather than spec-level content.\n"
            "For each question, set agrees=true unless one of these rules is actually violated, "
            "and explain your reasoning (including when you're accepting a different-from-GT but "
            "still valid derivation) in notes. Also check whether any repairs the model proposed "
            "are defensible given the spec content (not whether they textually match ground "
            "truth's proposed repairs).\n\n"
            f"## spec.md\n\n{spec_text}\n\n"
            f"## Ground truth (ONE valid derivation, for reference only)\n\n{json.dumps(expected, indent=2)}\n\n"
            f"## Model output to grade\n\n{json.dumps(got, indent=2)}"
        )
        verdict = claude_json(judge_prompt, JUDGE_SCHEMA)

        (out_dir / f"{name}.got.json").write_text(json.dumps(got, indent=2))
        (out_dir / f"{name}.verdict.json").write_text(json.dumps(verdict, indent=2))

        results.append((name, verdict["overall_agreement_pct"]))
        print(f"  {name}: {verdict['overall_agreement_pct']:.0f}% agreement — {verdict['summary']}")

    return results


def run_probes(probe_names):
    all_pass = True
    for name in probe_names:
        probe_path = PROBES_DIR / f"{name}.md"
        if not probe_path.exists():
            print(f"  skip {name}: no such probe file", file=sys.stderr)
            continue

        raw = probe_path.read_text()
        _, fm_text, _ = raw.split("---", 2)
        frontmatter = yaml.safe_load(fm_text)

        command_text = COMMAND_FILE.read_text()
        response_prompt = (
            "You are acting as the following command mid-session. Prior state:\n"
            f"{frontmatter['given']}\n\n"
            f"The developer's next message is:\n{frontmatter['when']}\n\n"
            f"## Command instructions\n\n{command_text}\n\n"
            "Respond exactly as the command's instructions direct you to, given this state and "
            "this developer message."
        )
        response = subprocess.run(
            ["claude", "-p", response_prompt], capture_output=True, text=True
        )
        if response.returncode != 0:
            raise RuntimeError(f"claude -p failed for probe {name}: {response.stderr}")
        response_text = response.stdout

        judge_prompt = (
            "Grade whether each assertion below holds true of the response text.\n\n"
            f"## Assertions\n\n{json.dumps(frontmatter['assert'], indent=2)}\n\n"
            f"## Response to grade\n\n{response_text}"
        )
        verdict = claude_json(judge_prompt, PROBE_JUDGE_SCHEMA)

        status = "PASS" if verdict["all_hold"] else "FAIL"
        print(f"  {name}: {status}")
        if not verdict["all_hold"]:
            all_pass = False
            for a in verdict["assertion_results"]:
                if not a["holds"]:
                    print(f"    - FAILED: {a['assertion']} ({a['notes']})", file=sys.stderr)

    return all_pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--derivation-only", action="store_true")
    parser.add_argument("--probes-only", action="store_true")
    parser.add_argument("--fixture", action="append", default=None)
    parser.add_argument("--probe", action="append", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    out_dir = Path(args.out) if args.out else Path(
        subprocess.run(["mktemp", "-d"], capture_output=True, text=True, check=True).stdout.strip()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    ok = True

    if not args.probes_only:
        fixture_names = args.fixture or sorted(p.name for p in FIXTURES_DIR.iterdir() if p.is_dir())
        print(f"Derivation-quality eval ({len(fixture_names)} fixtures, results in {out_dir}):")
        results = run_derivation_eval(fixture_names, out_dir)
        if results:
            avg = sum(pct for _, pct in results) / len(results)
            print(f"Average agreement: {avg:.1f}%")
            if avg < 80:
                print("FAIL: average agreement below the 80% target", file=sys.stderr)
                ok = False

    if not args.derivation_only:
        probe_names = args.probe or sorted(p.stem for p in PROBES_DIR.glob("*.md") if p.stem != "README")
        print(f"Behavioral probes ({len(probe_names)}):")
        if not run_probes(probe_names):
            ok = False

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
