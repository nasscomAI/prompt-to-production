"""
UC-0B — Summary That Changes Meaning

Reads a policy document and creates a clause-complete summary.
"""

import argparse
import re


def retrieve_policy(input_path):
    """
    Read the policy document and extract numbered clauses.

    Returns:
        list of tuples: [(clause_number, clause_text), ...]
    """

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            content = infile.read()

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Policy file not found: {input_path}"
        )

    except OSError as error:
        raise OSError(
            f"Could not read policy file: {error}"
        )

    # Match numbered clauses such as:
    # 2.3
    # 2.4
    # 5.2
    # 7.2
    #
    # The clause text may continue over multiple lines.
    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)",
        re.DOTALL
    )

    matches = pattern.findall(content)

    clauses = []

    for clause_number, clause_text in matches:
        # Clean whitespace while preserving the meaning.
        cleaned_text = " ".join(
            line.strip()
            for line in clause_text.splitlines()
            if line.strip()
        )

        if cleaned_text:
            clauses.append(
                (clause_number, cleaned_text)
            )

    return clauses


def summarize_policy(clauses):
    """
    Produce a clause-complete summary.

    Every numbered clause is preserved.
    No clause is silently omitted.
    """

    if not clauses:
        raise ValueError(
            "No numbered policy clauses were found."
        )

    lines = []

    lines.append(
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY SUMMARY"
    )
    lines.append("")
    lines.append(
        "This summary preserves every numbered clause from the supplied policy document."
    )
    lines.append("")

    for clause_number, clause_text in clauses:
        lines.append(
            f"{clause_number}: {clause_text}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary Generator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the summary output file."
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        summary = summarize_policy(clauses)

        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as outfile:
            outfile.write(summary)

        print(
            f"Done. Summary written to {args.output}"
        )

        print(
            f"Clauses preserved: {len(clauses)}"
        )

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()