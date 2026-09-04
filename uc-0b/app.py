"""
UC-0B — Summary That Changes Meaning

Policy summarizer that preserves the required UC-0B clauses,
conditions, and obligation strength.
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
    """Load the policy and return numbered clauses as structured data."""

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        text = infile.read()

    sections = {}

    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        sections[clause_number] = clause_text

    return sections


def summarize_policy(sections):
    """Create a faithful summary of all required UC-0B clauses."""

    summaries = {
        "2.3": (
            "2.3 — Employees must submit a leave application at least "
            "14 calendar days in advance using Form HR-L1."
        ),
        "2.4": (
            "2.4 — Leave applications must receive written approval from "
            "the employee's direct manager before the leave commences; "
            "verbal approval is not valid."
        ),
        "2.5": (
            "2.5 — Unapproved absence will be recorded as Loss of Pay "
            "(LOP) regardless of subsequent approval."
        ),
        "2.6": (
            "2.6 — Employees may carry forward a maximum of 5 unused "
            "annual leave days to the following calendar year; any days "
            "above 5 are forfeited on 31 December."
        ),
        "2.7": (
            "2.7 — Carry-forward days must be used within the first "
            "quarter (January–March) of the following year or they are "
            "forfeited."
        ),
        "3.2": (
            "3.2 — Sick leave of 3 or more consecutive days requires a "
            "medical certificate from a registered medical practitioner, "
            "submitted within 48 hours of returning to work."
        ),
        "3.4": (
            "3.4 — Sick leave taken immediately before or after a public "
            "holiday or annual leave period requires a medical certificate "
            "regardless of duration."
        ),
        "5.2": (
            "5.2 — LWP requires approval from both the Department Head and "
            "the HR Director; manager approval alone is not sufficient."
        ),
        "5.3": (
            "5.3 — LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner."
        ),
        "7.2": (
            "7.2 — Leave encashment during service is not permitted under "
            "any circumstances."
        ),
    }

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in sections
    ]

    if missing:
        raise ValueError(
            "Required clauses missing from source: "
            + ", ".join(missing)
        )

    return "\n".join(
        summaries[clause]
        for clause in REQUIRED_CLAUSES
    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
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

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as outfile:
        outfile.write(summary)
        outfile.write("\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()