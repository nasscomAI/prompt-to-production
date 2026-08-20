"""
UC-0B — Policy Summarizer
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


def retrieve_policy(input_path: str) -> list:
    """Load the policy and extract numbered clauses."""

    with open(input_path, "r", encoding="utf-8") as infile:
        text = infile.read()

    clauses = []

    for clause_number in REQUIRED_CLAUSES:
        pattern = rf"(?m)^\s*{re.escape(clause_number)}\s+(.+?)(?=^\s*\d+\.\d+\s+|\Z)"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            source_text = " ".join(match.group(1).split())
            clauses.append(
                {
                    "number": clause_number,
                    "text": source_text,
                }
            )

    if not clauses:
        raise ValueError("No required numbered policy clauses were found.")

    return clauses


def summarize_policy(clauses: list) -> str:
    """Create a clause-referenced summary without dropping conditions."""

    found = {clause["number"]: clause["text"] for clause in clauses}

    missing = [
        number for number in REQUIRED_CLAUSES
        if number not in found
    ]

    if missing:
        raise ValueError(
            "Required policy clauses are missing: "
            + ", ".join(missing)
        )

    lines = [
        "HR Leave Policy Summary",
        "",
    ]

    for number in REQUIRED_CLAUSES:
        lines.append(f"Clause {number}: {found[number]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary output file",
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

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