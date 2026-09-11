"""
UC-0B Policy Summarizer

Reads the HR leave policy and creates a clause-referenced summary.
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
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    clauses = {}

    # Capture numbered clauses such as 2.3, 2.4, 3.2, etc.
    # Stop when the next numbered clause or section heading begins.
    pattern = (
        r"(?ms)^\s*(\d+\.\d+)\s+(.*?)"
        r"(?=^\s*\d+\.\d+\s+|^\s*\d+\.\s+|\Z)"
    )

    for match in re.finditer(pattern, text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())

        # Remove any accidental separator characters from source formatting.
        clause_text = re.sub(r"[^\x00-\x7F]+", " ", clause_text)
        clause_text = " ".join(clause_text.split())

        clauses[clause_number] = clause_text

    return clauses


def summarize_policy(clauses):
    lines = []

    for clause_number in REQUIRED_CLAUSES:
        if clause_number not in clauses:
            lines.append(
                f"[{clause_number}] FLAG: Required clause was not found in the source."
            )
        else:
            lines.append(
                f"[{clause_number}] {clauses[clause_number]}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize the HR leave policy."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy text file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary.",
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary)
            file.write("\n")

        print(
            f"Policy summary complete. Written to {args.output}"
        )

    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()