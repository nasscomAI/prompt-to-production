"""
UC-0B — Policy Summary

Deterministic, extract-and-preserve digest of a single HR leave policy. Enforces
the contract in agents.md / skills.md: the 10 binding clauses are reproduced
condition-complete, clauses that cannot be shortened without losing a condition
are quoted verbatim and tagged [VERBATIM], binding verbs are never softened, and
no fact absent from the source is introduced. No runtime LLM — every guarantee
is a verifiable string check. If a required clause or condition is missing from
the source, the agent refuses to emit a summary rather than fabricate content.

The verification report is printed to stdout only; the summary file stays pure
policy text.
"""
import argparse
import re
import sys
from collections import OrderedDict

# The 10 binding clauses that must appear, in source order (ground truth).
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Per-clause conditions. Each condition PASSES if any of its accepted substrings
# is present in the (lower-cased) source clause text. A clause with 2+ conditions
# is treated as multi-condition and quoted verbatim with a [VERBATIM] tag.
CONDITION_CHECKS = {
    "2.3": [
        ("14 calendar days advance notice", ["14 calendar days"]),
    ],
    "2.4": [
        ("written approval before leave", ["written approval"]),
        ("verbal approval not valid", ["not valid"]),
    ],
    "2.5": [
        ("recorded as Loss of Pay", ["loss of pay", "lop"]),
        ("regardless of subsequent approval", ["regardless"]),
    ],
    "2.6": [
        ("maximum 5 carry-forward days", ["maximum of 5", "5 unused"]),
        ("excess forfeited on 31 December", ["31 december"]),
    ],
    "2.7": [
        ("must be used January-March", ["january", "first quarter"]),
        ("otherwise forfeited", ["forfeited"]),
    ],
    "3.2": [
        ("medical certificate required", ["medical certificate"]),
        ("triggered by 3+ consecutive days", ["3 or more"]),
        ("submitted within 48 hours", ["48 hours"]),
    ],
    "3.4": [
        ("medical certificate required", ["medical certificate"]),
        ("before or after holiday/leave", ["before or after"]),
        ("regardless of duration", ["regardless of duration"]),
    ],
    "5.2": [
        ("Department Head approval", ["department head"]),
        ("HR Director approval", ["hr director"]),
    ],
    "5.3": [
        ("Municipal Commissioner approval", ["municipal commissioner"]),
        ("threshold exceeding 30 continuous days", ["30 continuous days"]),
    ],
    "7.2": [
        ("not permitted", ["not permitted"]),
        ("under any circumstances", ["any circumstances"]),
    ],
}

# Binding verb(s) each clause must retain — the softening guard checks the
# emitted clause still carries its original binding force.
BINDING_VERBS = {
    "2.3": ["must"],
    "2.4": ["must"],
    "2.5": ["will"],
    "2.6": ["forfeited"],
    "2.7": ["must", "forfeited"],
    "3.2": ["requires"],
    "3.4": ["requires"],
    "5.2": ["requires"],
    "5.3": ["requires"],
    "7.2": ["not permitted"],
}

# Phrases that signal information not present in the source (scope bleed).
SCOPE_BLEED_PHRASES = [
    "standard practice", "typically", "generally", "as is common",
    "as is standard", "employees are generally expected", "usually",
    "in general", "commonly", "as a rule",
]

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*\d+\.\s")   # e.g. "2. ANNUAL LEAVE" (section header)
DIVIDER_RE = re.compile(r"[\u2550=]{3,}")  # heavy/equals rule lines


def retrieve_policy(input_path):
    """Load the policy .txt and split it into an ordered clause_number -> text
    mapping, preserving source wording. Returns (clauses, raw_text)."""
    try:
        with open(input_path, "r", encoding="utf-8") as fh:
            raw_text = fh.read()
    except OSError as exc:
        raise RuntimeError("Cannot read policy file '%s': %s" % (input_path, exc))

    clauses = OrderedDict()
    current_num = None
    current_parts = []

    def flush():
        if current_num is not None:
            clauses[current_num] = " ".join(p for p in current_parts if p).strip()

    for raw in raw_text.splitlines():
        line = raw.rstrip()
        match = CLAUSE_RE.match(line)
        if match:
            flush()
            current_num = match.group(1)
            current_parts = [match.group(2).strip()]
            continue

        stripped = line.strip()
        if not stripped or DIVIDER_RE.search(line) or SECTION_RE.match(line):
            flush()
            current_num = None
            current_parts = []
            continue

        if current_num is not None:
            current_parts.append(stripped)

    flush()
    return clauses, raw_text


def _condition_pass(clause_text, accepted):
    low = clause_text.lower()
    return any(sub in low for sub in accepted)


def summarize_policy(clauses, required=REQUIRED_CLAUSES):
    """Build a condition-complete digest of the required binding clauses plus a
    separate verification report. Returns (summary_text, report_lines, ok).

    Never invents text and never softens a binding verb: every clause body is
    reproduced verbatim from the source. `ok` is False when any required clause
    is absent, any condition is missing from the source, a binding verb is lost,
    or a scope-bleed phrase appears — in which case the caller must refuse.
    """
    report = []
    ok = True

    # 1. Clause presence.
    report.append("Clause presence:")
    for num in required:
        present = num in clauses and bool(clauses[num])
        report.append("  %-5s %s" % (num, "PRESENT" if present else "MISSING"))
        if not present:
            ok = False

    # 2. Condition completeness (verified against the source clause text).
    report.append("Condition checks:")
    multi_condition = set()
    for num in required:
        text = clauses.get(num, "")
        conditions = CONDITION_CHECKS.get(num, [])
        if len(conditions) >= 2:
            multi_condition.add(num)
        for label, accepted in conditions:
            passed = bool(text) and _condition_pass(text, accepted)
            report.append("  %-5s %-45s %s" % (num, label, "PASS" if passed else "FAIL"))
            if not passed:
                ok = False

    # Build the summary body — verbatim clause text; tag multi-condition clauses.
    lines = [
        "CITY MUNICIPAL CORPORATION — HR LEAVE POLICY",
        "BINDING-CLAUSE SUMMARY (source: policy_hr_leave.txt)",
        "",
        "The 10 binding clauses below are reproduced with every condition",
        "preserved. Clauses marked [VERBATIM] are quoted exactly from the source",
        "because they cannot be shortened without losing a condition.",
        "",
    ]
    for num in required:
        text = clauses.get(num, "").strip()
        if not text:
            continue
        tag = "[VERBATIM] " if num in multi_condition else ""
        lines.append("%s %s%s" % (num, tag, text))
    summary_text = "\n".join(lines) + "\n"

    # 3. Binding-verb (obligation-softening) guard on the emitted clauses.
    report.append("Binding-verb checks:")
    for num in required:
        text = clauses.get(num, "").lower()
        verbs = BINDING_VERBS.get(num, [])
        kept = bool(text) and any(v in text for v in verbs)
        report.append("  %-5s expects {%s}: %s"
                      % (num, ", ".join(verbs), "PASS" if kept else "FAIL"))
        if not kept:
            ok = False

    # 4. Scope-bleed scan over the emitted summary body.
    body_low = summary_text.lower()
    found = [p for p in SCOPE_BLEED_PHRASES if p in body_low]
    report.append("Scope-bleed scan: %s" % ("CLEAN" if not found else "DIRTY " + str(found)))
    if found:
        ok = False

    return summary_text, report, ok


def main():
    parser = argparse.ArgumentParser(description="UC-0B deterministic policy summariser")
    parser.add_argument("--input", required=True, help="Path to the source policy .txt")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt")
    args = parser.parse_args()

    try:
        clauses, _ = retrieve_policy(args.input)
    except RuntimeError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 1

    summary_text, report, ok = summarize_policy(clauses)

    print("=== VERIFICATION REPORT (not written to summary) ===")
    for line in report:
        print(line)

    if not ok:
        missing = [n for n in REQUIRED_CLAUSES if n not in clauses or not clauses[n]]
        print("RESULT: REFUSED — summary NOT written.", file=sys.stderr)
        if missing:
            print("Missing clauses: %s" % ", ".join(missing), file=sys.stderr)
        else:
            print("A required condition or binding verb could not be verified in the source.",
                  file=sys.stderr)
        return 1

    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(summary_text)
    except OSError as exc:
        print("REFUSED: cannot write output '%s': %s" % (args.output, exc), file=sys.stderr)
        return 1

    print("RESULT: ALL CHECKS PASSED — summary written to %s" % args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
