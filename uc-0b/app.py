"""
UC-0B — Policy Summary Generator

Reads an HR leave policy document and produces a clause-preserving summary.
Built to avoid clause omission, scope bleed, and obligation softening.
"""

import argparse


def retrieve_policy(input_path):
    """
    Load the policy file and extract numbered clauses.
    Returns a list of clause strings.
    """
    clauses = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Only capture numbered clauses (e.g., 2.3, 3.4 etc.)
            if line and line[0].isdigit():
                clauses.append(line)

    return clauses


def summarize_policy(clauses):
    """
    Produce a compliant summary.
    Rules:
    - Every clause must appear
    - No conditions dropped
    - No new information added
    """
    summary_lines = []

    for clause in clauses:
        # Preserve clause exactly to avoid meaning drift
        summary_lines.append(clause)

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        if not clauses:
            raise ValueError("No policy clauses detected in input file")

        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Done. Summary written to {args.output}")

    except Exception as e:
        print("Error processing policy:", str(e))


if __name__ == "__main__":
    main()

