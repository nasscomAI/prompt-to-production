"""
UC-0B — Summary That Changes Meaning
Summarize HR leave policy preserving all obligations, binding verbs, and scope.
"""
import argparse
import re
import sys

CLAUSE_INVENTORY = [
    ("2.3", "must"),
    ("2.4", "must"),
    ("2.5", "will"),
    ("2.6", "may"),
    ("2.7", "must"),
    ("3.2", "requires"),
    ("3.4", "requires"),
    ("5.2", "requires"),
    ("5.3", "requires"),
]


def extract_clauses(policy_text):
    """Extract numbered clause text from policy document."""
    clauses = {}
    matches = list(re.finditer(r'(\d+\.\d+)\b', policy_text))
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(policy_text)
        clauses[sec_num] = policy_text[start:end].strip()
    return clauses


def summarize_policy(policy_text):
    """
    Extract and summarize each clause in the inventory.
    Flags any clause that is missing from the policy text.
    """
    clauses = extract_clauses(policy_text)
    summary_lines = []
    missing = []
    for clause_num, required_verb in CLAUSE_INVENTORY:
        if clause_num in clauses:
            clause_text = clauses[clause_num]
            summary_lines.append(f"--- Clause {clause_num} ---")
            summary_lines.append(clause_text)
            summary_lines.append("")
        else:
            missing.append(clause_num)
            summary_lines.append(f"--- Clause {clause_num} --- MISSING IN DOCUMENT")
            summary_lines.append("")
    if missing:
        summary_lines.append(f"NEEDS_REVIEW: Clauses not found in document: {', '.join(missing)}")
    return '\n'.join(summary_lines)


def clause_inventory_check(policy_text):
    """
    Verify all required clauses and their binding verbs are present.
    Returns a validation report.
    """
    clauses = extract_clauses(policy_text)
    issues = []
    for clause_num, required_verb in CLAUSE_INVENTORY:
        if clause_num not in clauses:
            issues.append(f"FAIL: Clause {clause_num} — not found in document")
        elif required_verb not in clauses[clause_num].lower():
            issues.append(f"FAIL: Clause {clause_num} — binding verb '{required_verb}' not found in clause text")
    if issues:
        return "Inventory Check — ISSUES FOUND:\n" + '\n'.join(issues)
    return "Inventory Check — PASSED: All clauses and binding verbs present."


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    try:
        with open(args.input, "r", encoding="utf-8") as infile:
            policy_text = infile.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    summary = summarize_policy(policy_text)
    check_report = clause_inventory_check(policy_text)
    try:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(summary)
            outfile.write("\n\n" + "=" * 60 + "\n")
            outfile.write(check_report + "\n")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

