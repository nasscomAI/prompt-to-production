import argparse
import re


def summarize_policy(text):
    lines = text.splitlines()
    clauses = []
    current_clause = []

    for line in lines:
        # Capture numbered policy clauses such as 2.3, 2.4, 3.2, 5.2, etc.
        if re.match(r"^\d+\.\d+\s+", line):
            if current_clause:
                clauses.append(" ".join(current_clause))
            current_clause = [line.strip()]
        elif line.startswith(" ") or line.startswith("\t"):
            if current_clause and line.strip():
                current_clause.append(line.strip())
        else:
            if current_clause:
                clauses.append(" ".join(current_clause))
                current_clause = []

    if current_clause:
        clauses.append(" ".join(current_clause))

    if not clauses:
        return "No numbered policy clauses were found."

    output = [
        "HR LEAVE POLICY SUMMARY",
        "========================",
        "",
        "The following numbered policy clauses must be preserved:",
        ""
    ]

    for clause in clauses:
        output.append(f"- {clause}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary"
    )

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        policy = f.read()

    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()