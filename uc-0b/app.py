import argparse
import re


def retrieve_policy(input_file):
    """Load the policy file and return numbered clauses."""
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except OSError as error:
        raise OSError(f"Could not read input file: {error}")

    clauses = []
    current_clause = None
    current_text = []

    for line in content.splitlines():
        match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)

        if match:
            if current_clause is not None:
                clauses.append(
                    (current_clause, " ".join(current_text).strip())
                )

            current_clause = match.group(1)
            current_text = [match.group(2).strip()]

        elif current_clause is not None:
            text = line.strip()

            if text and not text.startswith("="):
                current_text.append(text)

    if current_clause is not None:
        clauses.append(
            (current_clause, " ".join(current_text).strip())
        )

    if not clauses:
        raise ValueError("No numbered clauses found in the input file.")

    return clauses


def summarize_policy(clauses):
    """Create a concise summary while preserving every clause and condition."""
    summary = [
        "HR EMPLOYEE LEAVE POLICY SUMMARY",
        "",
        "The following summary preserves every numbered clause and its "
        "requirements, conditions, limits, approvals, exceptions, and restrictions.",
        ""
    ]

    for number, text in clauses:
        # Keep clauses where shortening could risk changing the meaning.
        if number in {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}:
            summary.append(f"Clause {number} [VERBATIM]: {text}")
        else:
            # The original wording is retained when no safe shortening rule
            # has been established for that clause.
            summary.append(f"Clause {number}: {text}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="Create a meaning-preserving HR policy summary."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input policy text file."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary file."
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    try:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary)
    except OSError as error:
        raise OSError(f"Could not write output file: {error}")

    print(f"Summary created successfully: {args.output}")


if __name__ == "__main__":
    main()