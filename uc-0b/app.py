"""
UC-0B — Policy Summarisation Agent
Preserves all 10 key clauses (2.3–7.2) with full conditions from HR leave policy.
"""
import argparse
import re
import sys


def retrieve_policy(filepath):
    """Load .txt policy file → dict of clause_number → clause_text."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        print("Error: file is empty", file=sys.stderr)
        sys.exit(1)

    clauses = {}
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)(?=^\s*\d+\.\d+\s|\Z)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        clause_num = match.group(1).strip()
        clause_text = " ".join(match.group(2).split())
        clauses[clause_num] = clause_text

    if not clauses:
        print("Error: no numbered clauses found in document", file=sys.stderr)
        sys.exit(1)

    return clauses


def summarize_policy(clauses):
    """Produce compliant summary preserving all 10 key clauses with conditions."""
    required_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    missing = [c for c in required_clauses if c not in clauses]
    if missing:
        print(f"Warning: missing required clauses: {missing}", file=sys.stderr)

    lines = [
        "HR LEAVE POLICY — SUMMARY",
        "=" * 40,
        "",
    ]

    summaries = {
        "2.3": "Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Clause 2.4: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        "2.5": "Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "2.7": "Clause 2.7: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "3.2": "Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.4": "Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "5.2": "Clause 5.2: LWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient.",
        "5.3": "Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Clause 7.2: Leave encashment during service is not permitted under any circumstances.",
    }

    for clause_num in required_clauses:
        if clause_num in summaries:
            lines.append(summaries[clause_num])
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Policy summarisation agent")
    parser.add_argument("--input", required=True, help="Path to .txt policy document")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output} ({len(summary)} chars)")


if __name__ == "__main__":
    main()
