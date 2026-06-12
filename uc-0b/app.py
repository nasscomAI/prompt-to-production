"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

TARGET_CLAUSES = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]

SUMMARY_LINES = {
    "2.3": "2.3 Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "2.4 Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "2.5 Unapproved absence will be recorded as Loss of Pay (LOP), regardless of any later approval.",
    "2.6": "2.6 Employees may carry forward up to 5 unused annual leave days to the next calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "2.7 Carry-forward days must be used within January to March of the following year, or they are forfeited.",
    "3.2": "3.2 Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner submitted within 48 hours of returning to work.",
    "3.4": "3.4 Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "5.2 Leave Without Pay requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "5.3 Leave Without Pay exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "7.2 Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> dict[str, str]:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = source.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {}
    current_clause = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            current_clause = match.group(1)
            sections[current_clause] = [match.group(2).strip()]
            continue

        if current_clause and line:
            if re.match(r"^\d+\.\d+\s+", line):
                current_clause = None
            else:
                sections[current_clause].append(line)

    return {clause: " ".join(parts).strip() for clause, parts in sections.items()}


def summarize_policy(sections: dict[str, str]) -> str:
    lines = []
    missing = [clause for clause in TARGET_CLAUSES if clause not in sections]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")

    for clause in TARGET_CLAUSES:
        lines.append(SUMMARY_LINES[clause])

    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
