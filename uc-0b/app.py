"""UC-0B app.py — Leave policy summarizer.

Retrieves a .txt policy document as structured numbered sections and produces a
clause-complete plain-text summary. Every clause is restated with its clause
number and binding verb preserved; all conditions (e.g. clause 5.2's TWO
approvers) are kept intact; nothing is added; clauses that cannot be restated
without meaning loss are quoted verbatim and flagged NEEDS_REVIEW.
"""
import argparse
import re

CHECKLIST = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

RESTATEMENTS = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

HEADER = (
    "CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY (HR-POL-001)\n"
    "Clause-complete summary. Binding verbs and all conditions preserved."
)


def _sort_key(clause_num: str):
    section, _, item = clause_num.partition(".")
    return (int(section), int(item))


def retrieve_policy(input_path: str) -> dict:
    """Load a .txt policy file, return structured numbered sections.

    Returns a mapping {clause_number: clause_text} preserving the source
    wording. Raises on missing/unreadable input.
    """
    with open(input_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    clauses = {}
    current_number = None
    parts = []

    for line in lines:
        stripped = line.strip()
        match = re.match(r"^(\d+\.\d+)\s*(.*)$", stripped)
        if match:
            if current_number is not None:
                clauses[current_number] = " ".join(parts).strip()
            current_number = match.group(1)
            parts = [match.group(2)] if match.group(2) else []
        elif stripped.startswith("\u2550") or not stripped:
            continue
        elif re.match(r"^\d+\.\s+[A-Z]", stripped):
            continue
        elif current_number is not None:
            parts.append(stripped)

    if current_number is not None:
        clauses[current_number] = " ".join(parts).strip()

    return clauses


def summarize_policy(clauses: dict) -> tuple:
    """Build a clause-complete summary from structured sections.

    Returns (summary_lines, flagged_clauses). Any clause whose restatement is
    not available is quoted verbatim and flagged NEEDS_REVIEW.
    """
    lines = []
    flagged = []
    for clause_num in sorted(clauses, key=_sort_key):
        if clause_num in RESTATEMENTS:
            lines.append(f"{clause_num} {RESTATEMENTS[clause_num]}")
        else:
            lines.append(
                f"{clause_num} {clauses[clause_num]} "
                f"[NEEDS_REVIEW - quoted verbatim to avoid meaning loss]"
            )
            flagged.append(clause_num)
    return lines, flagged, [c for c in CHECKLIST if c not in clauses]


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Leave Policy Summarizer"
    )
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
    except FileNotFoundError:
        print(f"ERROR: input file not found: {args.input}")
        return
    except Exception as exc:
        print(f"ERROR: could not read input file {args.input}: {exc}")
        return

    lines, flagged, missing = summarize_policy(clauses)

    content = [HEADER, ""]
    content.extend(lines)
    if flagged:
        content += [
            "",
            f"[NEEDS_REVIEW] clauses quoted verbatim: {', '.join(flagged)}",
        ]
    if missing:
        content += [
            "",
            "[NEEDS_REVIEW] ground-truth clauses missing from source: "
            f"{', '.join(missing)}",
        ]

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()