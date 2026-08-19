"""
UC-0B - Summary That Changes Meaning
"""

import argparse
import re


# These clauses are the ground truth required by the workshop.
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
    """
    Read the policy document and extract its numbered clauses.
    Returns a dictionary: clause number -> clause text.
    """
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    clauses = {}

    pattern = re.compile(
    r"(?ms)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|^\d+\.\s+[A-Z]|^$|\Z)"
   )

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_number] = clause_text

    return clauses


def summarize_policy(clauses):
    """
    Create a summary containing every required clause.

    The original clause wording is retained so that conditions,
    numbers, deadlines, approvers, and obligations are not lost.
    """
    lines = []

    for clause in REQUIRED_CLAUSES:
        if clause not in clauses:
            lines.append(
                f"{clause}: [REVIEW REQUIRED - clause missing from source]"
            )
        else:
            lines.append(f"{clause}: {clauses[clause]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the summary output file"
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary + "\n")

        print(f"Done. Summary written to {args.output}")

    except Exception as exc:
        print(f"Error: {exc}")
        raise


if __name__ == "__main__":
    main()