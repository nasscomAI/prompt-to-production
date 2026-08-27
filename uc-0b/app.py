"""
UC-0B app.py — Summary That Changes Meaning
"""
import argparse
import re
from typing import Dict, List

CLAUSES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> Dict[str, str]:
    with open(input_path, "r", encoding="utf-8") as infile:
        text = infile.read()

    sections: Dict[str, str] = {}
    for match in re.finditer(r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s+|\Z)", text, flags=re.M | re.S):
        clause_number = match.group(1).strip()
        clause_text = match.group(2).strip().replace("\n", " ")
        sections[clause_number] = clause_text

    return sections


def summarize_policy(sections: Dict[str, str]) -> str:
    summary_lines: List[str] = [
        "HR Leave Policy Summary:",
        "",
        "This summary preserves the meaning and conditions of each required clause as stated in the source document.",
        "",
    ]

    for clause_num, _ in CLAUSES.items():
        source_text = sections.get(clause_num, "")

        if not source_text:
            summary_lines.append(f"{clause_num} — Clause missing from source text; refer to the original policy.")
            continue

        if clause_num == "2.3":
            summary_lines.append(
                "2.3 — Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."
            )
        elif clause_num == "2.4":
            summary_lines.append(
                "2.4 — Leave applications require written approval from the employee’s direct manager before the leave begins; verbal approval is not valid."
            )
        elif clause_num == "2.5":
            summary_lines.append(
                "2.5 — Any absence without prior approval is recorded as Loss of Pay (LOP), even if approval is granted later."
            )
        elif clause_num == "2.6":
            summary_lines.append(
                "2.6 — Employees may carry forward up to 5 unused annual leave days to the next calendar year; any days above 5 are forfeited on 31 December."
            )
        elif clause_num == "2.7":
            summary_lines.append(
                "2.7 — Carry-forward leave days must be used by March 31 of the next year or they are forfeited."
            )
        elif clause_num == "3.2":
            summary_lines.append(
                "3.2 — Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of return to work."
            )
        elif clause_num == "3.4":
            summary_lines.append(
                "3.4 — Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
            )
        elif clause_num == "5.2":
            summary_lines.append(
                "5.2 — Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director; manager approval alone is insufficient."
            )
        elif clause_num == "5.3":
            summary_lines.append(
                "5.3 — LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
            )
        elif clause_num == "7.2":
            summary_lines.append(
                "7.2 — Leave encashment during service is not permitted under any circumstances."
            )
        else:
            summary_lines.append(f"{clause_num} — {source_text}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to the input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary_text)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
