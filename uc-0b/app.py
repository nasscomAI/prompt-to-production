import argparse
import re


def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    clauses = {}

    pattern = r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s|\Z)"

    for match in re.finditer(pattern, content, re.DOTALL):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_number] = clause_text

    return clauses


def summarize_policy(clauses):
    required_clauses = [
        "2.3",
        "2.4",
        "2.5",
        "2.6",
        "2.7",
        "3.2",
        "3.4",
        "5.2",
        "5.3",
        "7.2"
    ]

    summary = []

    for clause in required_clauses:
        if clause in clauses:
            summary.append(f"Clause {clause}: {clauses[clause]}")
        else:
            summary.append(
                f"Clause {clause}: [FLAGGED - clause missing from source]"
            )

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary written to: {args.output}")


if __name__ == "__main__":
    main()