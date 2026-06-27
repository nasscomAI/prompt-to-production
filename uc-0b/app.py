
import argparse
import re
import sys


def read_policy_file(file_path):
    """Read the policy file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except PermissionError:
        print(f"Error: Permission denied: {file_path}")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")

    return None


def write_summary_file(file_path, summary):
    """Write the summary safely."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary written to {file_path}")

    except PermissionError:
        print(f"Error: Permission denied: {file_path}")
    except Exception as e:
        print(f"Error writing file '{file_path}': {e}")


def split_clauses(text):
    """
    Extract numbered clauses while preserving numbering.

    Example:
    1. Employees must...
    2. Managers shall...

    Returns:
        [(number, clause_text), ...]
    """
    pattern = r'^\s*(\d+[\.\)])\s+(.*?)(?=^\s*\d+[\.\)]\s+|\Z)'
    matches = re.findall(pattern, text, flags=re.MULTILINE | re.DOTALL)

    return [(num.strip(), clause.strip()) for num, clause in matches]


def requires_verbatim(clause):
    """
    Decide whether a clause should be copied verbatim.

    Multi-condition obligations are copied verbatim to avoid
    losing meaning.
    """
    indicators = [
        " if ",
        " unless ",
        " provided that ",
        " and ",
        " or ",
        " only if ",
        " except ",
        " subject to ",
        " provided ",
        " however "
    ]

    lower_clause = " " + clause.lower() + " "

    hits = sum(1 for word in indicators if word in lower_clause)

    # If multiple conditions are present, preserve verbatim.
    return hits >= 2


def summarize_clause(clause):
    """
    Produce a safe summary.

    If meaning may be lost, return the original clause and flag it.
    """
    if requires_verbatim(clause):
        return clause, True

    # Conservative summarization:
    # keep the first sentence only if there are multiple sentences.
    sentences = re.split(r'(?<=[.!?])\s+', clause)

    if len(sentences) > 1:
        summary = sentences[0].strip()

        # Avoid accidental empty summaries
        if summary:
            return summary, False

    # If uncertain, preserve verbatim.
    return clause, True


def generate_summary(policy_text):
    """Generate a policy summary preserving all numbered clauses."""

    clauses = split_clauses(policy_text)

    # If no numbered clauses found, preserve entire document.
    if not clauses:
        return (
            "[FLAG: NEEDS_REVIEW] No numbered clauses detected.\n\n"
            + policy_text
        )

    output_lines = []

    for number, clause in clauses:
        summary, flagged = summarize_clause(clause)

        if flagged:
            output_lines.append(
                f"{number} [FLAG: VERBATIM_REQUIRED] {summary}"
            )
        else:
            output_lines.append(f"{number} {summary}")

    return "\n\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )

    args = parser.parse_args()

    policy_text = read_policy_file(args.input)

    if policy_text is None:
        sys.exit(1)

    summary = generate_summary(policy_text)

    write_summary_file(args.output, summary)


if __name__ == "__main__":
    main()

