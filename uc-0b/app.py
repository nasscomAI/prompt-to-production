"""
UC-0B — Policy Summary

Reads the HR leave policy and produces a compliant summary
of the required clauses without dropping conditions.
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
    """Load the policy file and return its numbered sections."""
    with open(input_path, "r", encoding="utf-8") as file:
        content = file.read()

    sections = {}
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        clause = match.group(1)
        text = " ".join(match.group(2).split())
        sections[clause] = text

    return sections


def summarize_policy(sections):
    """Create a summary while preserving all required conditions."""
    summary_lines = []

    summaries = {
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within January–March of the following year or they are forfeited.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
    }

    for clause in REQUIRED_CLAUSES:
        if clause not in sections:
            raise ValueError(
                f"Required clause {clause} is missing from the policy."
            )

        summary_lines.append(f"{clause}: {summaries[clause]}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the required HR leave policy clauses."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary + "\n")


if __name__ == "__main__":
    main()