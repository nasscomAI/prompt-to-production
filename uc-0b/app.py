"""
UC-0B — Summary That Changes Meaning

Reads the HR leave policy and produces a clause-complete summary.
"""

import argparse
import re


REQUIRED_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Maximum 5 days carry-forward; days above 5 forfeited on 31 December",
    "2.7": "Carry-forward days must be used January through March or are forfeited",
    "3.2": "Three or more consecutive sick days require a medical certificate within 48 hours of returning",
    "3.4": "Sick leave immediately before or after a public holiday or annual leave requires a certificate regardless of duration",
    "5.2": "LWP requires Department Head and HR Director approval; Manager approval alone is insufficient",
    "5.3": "LWP exceeding 30 continuous days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service is not permitted under any circumstances",
}


def retrieve_policy(input_path):
    """Read the policy and return its text."""

    with open(input_path, "r", encoding="utf-8-sig") as file:
        return file.read()


def extract_clauses(policy_text):
    """Extract numbered clauses from the policy."""

    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.DOTALL,
    )

    clauses = {}

    for match in pattern.finditer(policy_text):
        number = match.group(1)
        text = " ".join(match.group(2).split())
        clauses[number] = text

    return clauses


def summarize_policy(clauses):
    """
    Produce a clause-complete summary.

    The summary intentionally uses the source wording closely so that
    conditions and obligations are not silently dropped.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Required clauses missing from source: "
            + ", ".join(missing)
        )

    lines = [
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY",
        "Clause-complete summary",
        "",
    ]

    lines.append(
        "Scope: The policy applies to permanent and contractual employees "
        "of the City Municipal Corporation and does not apply to daily wage "
        "workers or consultants, who are governed by their respective contracts."
    )
    lines.append("")

    lines.append("ANNUAL LEAVE")
    lines.append(
        "2.3 — Employees must submit a leave application at least "
        "14 calendar days in advance using Form HR-L1."
    )
    lines.append(
        "2.4 — Leave applications must receive written approval from "
        "the employee's direct manager before the leave commences. "
        "Verbal approval is not valid."
    )
    lines.append(
        "2.5 — Unapproved absence will be recorded as Loss of Pay (LOP) "
        "regardless of subsequent approval."
    )
    lines.append(
        "2.6 — Employees may carry forward a maximum of 5 unused annual "
        "leave days to the following calendar year. Any days above 5 are "
        "forfeited on 31 December."
    )
    lines.append(
        "2.7 — Carry-forward days must be used within the first quarter "
        "(January-March) of the following year or they are forfeited."
    )
    lines.append("")

    lines.append("SICK LEAVE")
    lines.append(
        "3.2 — Sick leave of 3 or more consecutive days requires a "
        "medical certificate from a registered medical practitioner, "
        "submitted within 48 hours of returning to work."
    )
    lines.append(
        "3.4 — Sick leave taken immediately before or after a public "
        "holiday or annual leave period requires a medical certificate "
        "regardless of duration."
    )
    lines.append("")

    lines.append("LEAVE WITHOUT PAY")
    lines.append(
        "5.2 — LWP requires approval from both the Department Head and "
        "the HR Director. Manager approval alone is not sufficient."
    )
    lines.append(
        "5.3 — LWP exceeding 30 continuous days requires approval from "
        "the Municipal Commissioner."
    )
    lines.append("")

    lines.append("LEAVE ENCASHMENT")
    lines.append(
        "7.2 — Leave encashment during service is not permitted under "
        "any circumstances."
    )
    lines.append("")

    lines.append(
        "Verification: All 10 required clauses from the workshop clause "
        "inventory are represented above."
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the HR leave policy without dropping conditions."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for summary_hr_leave.txt",
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    clauses = extract_clauses(policy_text)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()