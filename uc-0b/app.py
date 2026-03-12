"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def summarize_policy(policy_text):
    # Clause inventory from README
    clauses = [
        ("2.3", "14-day advance notice required", "must"),
        ("2.4", "Written approval required before leave commences. Verbal not valid.", "must"),
        ("2.5", "Unapproved absence = LOP regardless of subsequent approval", "will"),
        ("2.6", "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "may / are forfeited"),
        ("2.7", "Carry-forward days must be used Jan–Mar or forfeited", "must"),
        ("3.2", "3+ consecutive sick days requires medical cert within 48hrs", "requires"),
        ("3.4", "Sick leave before/after holiday requires cert regardless of duration", "requires"),
        ("5.2", "LWP requires Department Head AND HR Director approval", "requires"),
        ("5.3", "LWP >30 days requires Municipal Commissioner approval", "requires"),
    ]
    summary = []
    missing = []
    for clause_num, obligation, verb in clauses:
        if clause_num in policy_text:
            summary.append(f"Clause {clause_num}: {obligation} ({verb})")
        else:
            missing.append(clause_num)
    if missing:
        summary.append(f"NEEDS_REVIEW: Missing clauses: {', '.join(missing)}")
    return '\n'.join(summary)

def clause_inventory_check(summary_text):
    # Check for all clause numbers and binding verbs
    clauses = [
        ("2.3", "must"), ("2.4", "must"), ("2.5", "will"), ("2.6", "may"), ("2.6", "are forfeited"),
        ("2.7", "must"), ("3.2", "requires"), ("3.4", "requires"), ("5.2", "requires"), ("5.3", "requires")
    ]
    report = []
    for clause_num, verb in clauses:
        if clause_num not in summary_text or verb not in summary_text:
            report.append(f"NEEDS_REVIEW: Clause {clause_num} missing verb '{verb}'")
    if report:
        return '\n'.join(report)
    return "All clauses and verbs present."

def main():
    import sys
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
    check_report = clause_inventory_check(summary)
    try:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(summary + "\n\n" + check_report)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
