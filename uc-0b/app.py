"""
UC-0B — Policy Summary Generator
Ensures every numbered clause from the policy document appears in the summary.
"""

import argparse


def summarize_policy(text: str) -> str:
    """
    Generate a summary while preserving every numbered clause.
    """

    lines = text.split("\n")
    summary_lines = []

    for line in lines:
        line = line.strip()

        # Keep numbered clauses
        if line and line[0].isdigit():
            summary_lines.append(line)

    if not summary_lines:
        raise ValueError("No numbered clauses found in policy document")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")

    args = parser.parse_args()

    with open(args.input, "r") as f:
        text = f.read()

    summary = summarize_policy(text)

    with open(args.output, "w") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()