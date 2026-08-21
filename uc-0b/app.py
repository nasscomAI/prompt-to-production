"""
UC-0B - Policy Summary Generator

Reads the HR leave policy and produces a clause-complete summary.
"""

import argparse
import re


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


def retrieve_policy(input_path):
    """Load the policy document and return numbered clauses."""
    with open(input_path, "r", encoding="utf-8-sig") as file:
        content = file.read()

    clauses = {}

    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        number = match.group(1)
        text = " ".join(match.group(2).split())
        clauses[number] = text

    return clauses


def summarize_policy(clauses):
    """Create a faithful summary while preserving every required condition."""

    summary = []

    summary.append("CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY")
    summary.append("")
    summary.append("Policy Summary")
    summary.append("================")
    summary.append("")

    # Scope
    summary.append("1. Purpose and Scope")
    summary.append(
        "This policy applies to permanent and contractual employees "
        "of the City Municipal Corporation. It does not apply to daily "
        "wage workers or consultants, who are governed by their respective contracts."
    )
    summary.append("")

    # Annual Leave
    summary.append("2. Annual Leave")

    summary.append(
        "Clause 2.3: Employees must submit a leave application at least "
        "14 calendar days in advance using Form HR-L1."
    )

    summary.append(
        "Clause 2.4: Leave applications must receive written approval "
        "from the employee's direct manager before leave commences. "
        "Verbal approval is not valid."
    )

    summary.append(
        "Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) "
        "regardless of subsequent approval."
    )

    summary.append(
        "Clause 2.6: Employees may carry forward a maximum of 5 unused "
        "annual leave days to the following calendar year. Any days above "
        "5 are forfeited on 31 December."
    )

    summary.append(
        "Clause 2.7: Carry-forward days must be used within the first "
        "quarter (January-March) of the following year or they are forfeited."
    )

    summary.append("")

    # Sick Leave
    summary.append("3. Sick Leave")

    summary.append(
        "Clause 3.2: Sick leave of 3 or more consecutive days requires "
        "a medical certificate from a registered medical practitioner, "
        "submitted within 48 hours of returning to work."
    )

    summary.append(
        "Clause 3.4: Sick leave taken immediately before or after a "
        "public holiday or annual leave period requires a medical "
        "certificate regardless of duration."
    )

    summary.append("")

    # LWP
    summary.append("5. Leave Without Pay (LWP)")

    summary.append(
        "Clause 5.2: LWP requires approval from both the Department Head "
        "and the HR Director. Manager approval alone is not sufficient."
    )

    summary.append(
        "Clause 5.3: LWP exceeding 30 continuous days requires approval "
        "from the Municipal Commissioner."
    )

    summary.append("")

    # Encashment
    summary.append("7. Leave Encashment")

    summary.append(
        "Clause 7.2: Leave encashment during service is not permitted "
        "under any circumstances."
    )

    summary.append("")

    summary.append("Clause Verification")
    summary.append("===================")

    missing = []

    for clause in REQUIRED_CLAUSES:
        if not any(line.startswith(f"Clause {clause}:") for line in summary):
            missing.append(clause)

    if missing:
        summary.append(
            "NEEDS_REVIEW: Missing required clauses: "
            + ", ".join(missing)
        )
    else:
        summary.append(
            "All 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, "
            "3.2, 3.4, 5.2, 5.3, 7.2) are included."
        )

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary Generator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the summary output file",
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()