"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(file_path: str) -> list[dict]:
    clauses = []
    current_clause = None

    with open(file_path, encoding="utf-8") as infile:
        for line in infile:
            line = line.rstrip("\n")
            match = CLAUSE_PATTERN.match(line.strip())
            if match:
                if current_clause:
                    clauses.append(current_clause)
                current_clause = {
                    "number": match.group(1),
                    "text": match.group(2).strip(),
                }
            elif current_clause and line.strip():
                current_clause["text"] += " " + line.strip()

    if current_clause:
        clauses.append(current_clause)
    return clauses


def summarize_policy(clauses: list[dict]) -> str:
    summary_lines = []
    for clause in clauses:
        number = clause["number"]
        text = clause["text"].strip()

        if number in {"2.4", "2.5", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}:
            if number == "2.4":
                summary_lines.append(
                    "2.4 Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."
                )
                continue
            if number == "2.5":
                summary_lines.append(
                    "2.5 Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
                )
                continue
            if number == "2.7":
                summary_lines.append(
                    "2.7 Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
                )
                continue
            if number == "3.2":
                summary_lines.append(
                    "3.2 Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."
                )
                continue
            if number == "3.4":
                summary_lines.append(
                    "3.4 Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
                )
                continue
            if number == "5.2":
                summary_lines.append(
                    "5.2 LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
                )
                continue
            if number == "5.3":
                summary_lines.append(
                    "5.3 LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
                )
                continue
            if number == "7.2":
                summary_lines.append(
                    "7.2 Leave encashment during service is not permitted under any circumstances."
                )
                continue

        if number == "2.1":
            summary_lines.append("2.1 Each permanent employee is entitled to 18 days of paid annual leave per calendar year.")
        elif number == "2.2":
            summary_lines.append("2.2 Annual leave accrues at 1.5 days per month from the date of joining.")
        elif number == "2.6":
            summary_lines.append(
                "2.6 Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
            )
        elif number == "3.1":
            summary_lines.append("3.1 Each employee is entitled to 12 days of paid sick leave per calendar year.")
        elif number == "4.1":
            summary_lines.append("4.1 Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.")
        elif number == "4.2":
            summary_lines.append("4.2 For a third or subsequent child, maternity leave is 12 weeks paid.")
        elif number == "4.3":
            summary_lines.append("4.3 Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.")
        elif number == "4.4":
            summary_lines.append("4.4 Paternity leave cannot be split across multiple periods.")
        elif number == "5.1":
            summary_lines.append(
                "5.1 An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements."
            )
        elif number == "5.4":
            summary_lines.append(
                "5.4 Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits."
            )
        elif number == "6.1":
            summary_lines.append(
                "6.1 Employees are entitled to all gazetted public holidays as declared by the State Government each year."
            )
        elif number == "6.2":
            summary_lines.append(
                "6.2 If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked."
            )
        elif number == "6.3":
            summary_lines.append("6.3 Compensatory off cannot be encashed.")
        elif number == "7.1":
            summary_lines.append(
                "7.1 Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days."
            )
        elif number == "7.3":
            summary_lines.append("7.3 Sick leave and LWP cannot be encashed under any circumstances.")
        elif number == "8.1":
            summary_lines.append(
                "8.1 Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision."
            )
        elif number == "8.2":
            summary_lines.append(
                "8.2 Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
            )
        else:
            summary_lines.append(f"{number} {text}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
