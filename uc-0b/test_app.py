"""Test UC-0B policy summarizer against agents.md enforcement rules."""
import os
import sys

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected to",
    "usually",
    "in most cases",
    "it is common",
    "generally"
]

def test_summary(summary_path):
    with open(summary_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # Rule 1: Every critical clause must be present
    for clause in CRITICAL_CLAUSES:
        if clause not in content:
            errors.append(f"MISSING: Critical clause {clause} not found in summary")

    # Rule 2: Check multi-condition obligations preserved
    if "Department Head" not in content or "HR Director" not in content:
        errors.append("CONDITION DROP: Clause 5.2 missing one of two required approvers")
    if "Department Head and" not in content and "Department Head and the" not in content:
        errors.append("CONDITION DROP: Clause 5.2 'AND' condition not preserved")

    # Rule 3: No scope bleed
    content_lower = content.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in content_lower:
            errors.append(f"SCOPE BLEED: Found forbidden phrase '{phrase}'")

    # Rule 4: VERBATIM flag present
    if "[VERBATIM]" not in content:
        warnings.append("No [VERBATIM] flag found — check if complex clauses were quoted")

    # Rule 5: Refusal condition - file should not be empty
    if len(content.strip()) < 100:
        errors.append("Summary too short — possible refusal condition triggered incorrectly")

    return errors, warnings, len(content)


if __name__ == "__main__":
    summary_path = "summary_hr_leave.txt"

    print("=" * 60)
    print("UC-0B ENFORCEMENT RULE TEST")
    print("=" * 60)

    if not os.path.exists(summary_path):
        print(f"FAIL: Summary file not found: {summary_path}")
        sys.exit(1)

    errors, warnings, content_len = test_summary(summary_path)

    print(f"\nFile: {summary_path} ({content_len} chars)\n")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  FAIL: {e}")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  WARN: {w}")

    print(f"\n{'='*60}")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} errors, {len(warnings)} warnings")
        sys.exit(1)
    else:
        print(f"RESULT: PASS — {len(warnings)} warnings")
        sys.exit(0)
