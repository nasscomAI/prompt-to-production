"""
UC-0B — Policy Summarizer
"""

import argparse
import re


def retrieve_policy(input_path):
    """
    Load the policy file and return all numbered clauses.
    Continuation lines are joined to the previous clause.
    Section headings and decorative separators are ignored.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    clauses = {}
    current_clause = None

    for line in content.splitlines():
        line = line.strip()

        # Ignore empty lines and decorative separators
        if not line or line.startswith("═"):
            continue

        # Ignore section headings such as:
        # 1. PURPOSE AND SCOPE
        # 2. ANNUAL LEAVE
        if re.match(r"^\d+\.\s+", line):
            continue

        # Match numbered clauses such as 1.1, 2.3, 5.2, 7.2
        match = re.match(r"^(\d+\.\d+)\s+(.*)", line)

        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()

        # Add continuation lines to the current clause
        elif current_clause:
            clauses[current_clause] += " " + line

    return clauses


def summarize_policy(clauses):
    """
    Produce a clause-referenced summary while preserving
    the complete meaning and conditions of every clause.
    """
    summary = []

    for clause, text in clauses.items():
        summary.append(f"{clause}: {text}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary file"
    )

    args = parser.parse_args()

    # Skill 1: retrieve_policy
    clauses = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    summary = summarize_policy(clauses)

    # Write the summary
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()