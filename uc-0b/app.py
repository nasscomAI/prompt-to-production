import argparse
import re


def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as file:
        return file.read()


def summarize_policy(policy_text):
    clauses = []

    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"

    matches = re.finditer(pattern, policy_text, re.DOTALL)

    for match in matches:
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses.append(f"{clause_number}: {clause_text}")

    return "\n\n".join(clauses)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()