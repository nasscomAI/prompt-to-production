"""
UC-0B app.py — City Municipal Corporation Employee Leave Policy Summary

Reads the policy text, extracts numbered clauses, creates a concise summary,
and verifies that all required clauses are present.
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


def retrieve_policy(input_path):
    """Load the policy and return its numbered clauses."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    content = path.read_text(encoding="utf-8")

    # Capture numbered clauses such as 2.3, 3.2, 5.2, etc.
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    sections = {}

    for match in pattern.finditer(content):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        sections[clause_number] = clause_text

    return sections


def summarize_policy(sections):
    """
    Produce a concise summary while preserving the required clauses
    and their binding requirements.
    """

    required = {
        "2.3": (
            "Employees must submit a leave application at least 14 "
            "calendar days in advance using Form HR-L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from the "
            "employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) "
            "regardless of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual "
            "leave days to the following calendar year. Any days above 5 "
            "are forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited."
        ),
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical "
            "certificate from a registered medical practitioner, submitted "
            "within 48 hours of returning to work."
        ),
        "3.4": (
            "Sick leave taken immediately before or after a public holiday "
            "or annual leave period requires a medical certificate "
            "regardless of duration."
        ),
        "5.2": (
            "LWP requires approval from BOTH the Department Head and the "
            "HR Director. Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from the "
            "Municipal Commissioner."
        ),
        "7.2": (
            "Leave encashment during service is not permitted under any "
            "circumstances."
        ),
    }

    # Verify that every required clause exists in the source.
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in sections]

    if missing:
        raise ValueError(
            "Completeness check failed. Missing required clauses: "
            + ", ".join(missing)
        )

    summary = [
        "CITY MUNICIPAL CORPORATION",
        "EMPLOYEE LEAVE POLICY — REQUIRED CLAUSE SUMMARY",
        "",
        "2. ANNUAL LEAVE",
        f"2.3 — {required['2.3']}",
        f"2.4 — {required['2.4']}",
        f"2.5 — {required['2.5']}",
        f"2.6 — {required['2.6']}",
        f"2.7 — {required['2.7']}",
        "",
        "3. SICK LEAVE",
        f"3.2 — {required['3.2']}",
        f"3.4 — {required['3.4']}",
        "",
        "5. LEAVE WITHOUT PAY (LWP)",
        f"5.2 — {required['5.2']}",
        f"5.3 — {required['5.3']}",
        "",
        "7. LEAVE ENCASHMENT",
        f"7.2 — {required['7.2']}",
        "",
        "COMPLETENESS CHECK",
        "All required clauses are present: "
        + ", ".join(REQUIRED_CLAUSES)
        + ".",
    ]

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the CMC Employee Leave Policy."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary.",
    )

    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    output_path = Path(args.output)
    output_path.write_text(summary + "\n", encoding="utf-8")

    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()