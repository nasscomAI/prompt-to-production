"""
UC-0B — Summary That Changes Meaning

Reads the HR leave policy and produces a clause-complete summary.
"""

import argparse
import re


GROUND_TRUTH_CLAUSES = [
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
    """Load the policy document."""
    with open(input_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_clause(policy_text, clause_number):
    """
    Extract only the requested numbered clause.
    Stops before the next numbered clause or section heading.
    """

    pattern = rf"(?ms)^\s*{re.escape(clause_number)}\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*\d+\.\s+|^\s*$)"

    match = re.search(pattern, policy_text)

    if match:
        return " ".join(match.group(1).split())

    return None


def summarize_policy(policy_text):
    """
    Create a summary containing all ten required clauses.

    If a clause cannot be safely extracted, flag it instead of inventing
    information.
    """

    lines = [
        "HR LEAVE POLICY SUMMARY",
        "========================",
        "",
    ]

    for clause_number in GROUND_TRUTH_CLAUSES:

        clause_text = extract_clause(policy_text, clause_number)

        if clause_text:
            lines.append(
                f"Clause {clause_number}: {clause_text}"
            )
        else:
            lines.append(
                f"Clause {clause_number}: "
                "[NEEDS_REVIEW — clause could not be safely extracted]"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary_hr_leave.txt"
    )

    args = parser.parse_args()

    try:
        policy_text = retrieve_policy(args.input)

        if not policy_text.strip():
            raise ValueError("Policy file is empty.")

        summary = summarize_policy(policy_text)

        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write(summary)

        print(f"Done. Summary written to {args.output}")

    except Exception as error:
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()