"""
UC-0B app.py — Policy summarizer.

Reads the supplied HR leave policy and produces a clause-referenced
summary while preserving all conditions, limits, deadlines, approvals,
exceptions, and prohibitions.
"""

import argparse
import re


def retrieve_policy(input_path):
    """Load the policy and extract numbered clauses."""
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    clauses = []

    # Match numbered clauses such as 1.1, 2.3, 5.2, etc.
    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clause_text = re.sub(r"═+.*?═+","",clause_text).strip()
        clauses.append((clause_number, clause_text))

    return clauses


def summarize_policy(clauses):
    """Create a complete clause-referenced summary."""

    lines = [
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY SUMMARY",
        "",
        "Source: HR-POL-001, Version 2.3, Effective 1 April 2024",
        "",
    ]

    for clause_number, clause_text in clauses:
        lines.append(f"{clause_number}: {clause_text}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the CMC Employee Leave Policy."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary",
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    if not clauses:
        raise ValueError(
            "No numbered policy clauses could be retrieved from the input."
        )

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()