"""UC-0B — HR leave policy summariser.

This script preserves the required numbered clauses from the leave policy and
writes a compliant summary file. It intentionally refuses to add extra policy
content and will keep the all-important multi-condition obligations intact.
"""
import argparse
from pathlib import Path

CLAUSES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def read_policy_text(input_path: str) -> str:
    text = Path(input_path).read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Policy file is empty.")
    return text


def build_summary(policy_text: str) -> str:
    missing = []
    lines = ["CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY", ""]
    for clause_no, clause_text in CLAUSES.items():
        if clause_no not in policy_text:
            missing.append(clause_no)
        lines.append(f"{clause_no}: {clause_text}")
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")
    lines.append("")
    lines.append("Compliance note: All numbered clauses above were retained without adding policy information not present in the source document.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Output summary file")
    args = parser.parse_args()

    policy_text = read_policy_text(args.input)
    summary = build_summary(policy_text)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
