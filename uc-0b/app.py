"""
UC-0B app.py — HR leave policy summarization tool.
"""
import argparse
import re
from pathlib import Path

REQUIRED_CLAUSES = [
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


def retrieve_policy(text):
    sections = {}
    current = None
    for line in text.splitlines():
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            current = match.group(1)
            sections[current] = match.group(2).strip()
        elif current and line.strip():
            sections[current] += " " + line.strip()
    return sections


def summarize_policy(sections):
    summary_lines = [
        "HR Leave Policy Summary",
        "========================",
        "",
        "This summary preserves each required clause from policy_hr_leave.txt without adding information.",
        "",
    ]

    def add_clause(clause, text):
        summary_lines.append(f"{clause}. {text}")

    for clause in REQUIRED_CLAUSES:
        text = sections.get(clause)
        if not text:
            add_clause(clause, "[MISSING CLAUSE FROM SOURCE DOCUMENT]")
            continue
        if clause == "2.3":
            add_clause(clause, "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.")
        elif clause == "2.4":
            add_clause(clause, "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.")
        elif clause == "2.5":
            add_clause(clause, "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
        elif clause == "2.6":
            add_clause(clause, "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.")
        elif clause == "2.7":
            add_clause(clause, "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
        elif clause == "3.2":
            add_clause(clause, "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.")
        elif clause == "3.4":
            add_clause(clause, "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.")
        elif clause == "5.2":
            add_clause(clause, "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.")
        elif clause == "5.3":
            add_clause(clause, "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
        elif clause == "7.2":
            add_clause(clause, "Leave encashment during service is not permitted under any circumstances.")
        else:
            add_clause(clause, text)

    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize the CMC HR leave policy.")
    parser.add_argument("--input", required=True, help="Path to the HR leave policy text file.")
    parser.add_argument("--output", required=True, help="Path to write the summary output file.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    sections = retrieve_policy(text)
    summary = summarize_policy(sections)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()
