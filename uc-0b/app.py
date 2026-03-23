"""
UC-0B — HR Leave Policy Clause-Preserving Summarizer
"""

import argparse
import re
import sys


def retrieve_policy(file_path):
    """
    Reads the policy document and returns its contents.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Error: Input policy file not found.")
        sys.exit(1)


def extract_clauses(policy_text):
    """
    Extract numbered clauses such as 2.3, 2.4 etc.
    """
    clause_pattern = r"(\d+\.\d+)\s+(.*)"
    matches = re.findall(clause_pattern, policy_text)

    if not matches:
        print("Error: No numbered clauses found in the policy document.")
        sys.exit(1)

    clauses = []
    for number, text in matches:
        clauses.append((number.strip(), text.strip()))

    return clauses


def summarize_policy(clauses):
    """
    Produce clause-preserving summary.
    """
    summary = []

    for clause_number, text in clauses:
        summary.append(f"Clause {clause_number}: {text}")

    return "\n".join(summary)


def write_output(summary_text, output_path):
    """
    Write summary to output file.
    """
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(summary_text)


def main():
    parser = argparse.ArgumentParser(description="HR Leave Policy Summarizer")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input policy file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary file"
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    clauses = extract_clauses(policy_text)

    summary = summarize_policy(clauses)

    write_output(summary, args.output)

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()
