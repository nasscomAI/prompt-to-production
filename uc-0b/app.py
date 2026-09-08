
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
    """
    Load the policy document and extract numbered clauses.
    """

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read()

    except FileNotFoundError:
        raise ValueError(f"Policy file not found: {input_path}")

    except OSError as error:
        raise ValueError(f"Could not read policy file: {error}")

    if not content.strip():
        raise ValueError("Policy file is empty.")

    clauses = {}

    # Match numbered clauses such as 2.3, 2.4, 3.2, etc.
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL
    )

    for match in pattern.finditer(content):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_number] = clause_text

    return clauses


def summarize_policy(clauses):
    """
    Create a clause-referenced summary.

    The summary preserves the required clauses and does not
    introduce information outside the source document.
    """

    missing_clauses = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing_clauses:
        raise ValueError(
            "Required clauses could not be located: "
            + ", ".join(missing_clauses)
        )

    summary_lines = []

    for clause_number in REQUIRED_CLAUSES:
        clause_text = clauses[clause_number]

        summary_lines.append(
            f"Clause {clause_number}: {clause_text}"
        )

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary Generator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy .txt file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary .txt file"
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        summary = summarize_policy(clauses)

        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(summary)
            file.write("\n")

        print(
            f"Done. Summary written to {args.output}"
        )

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()

