"""
UC-0B — Policy Summary
RICE-enforced policy summarizer.
"""

import argparse
import re


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def clean_line(raw_line: str) -> str:
    """Remove formatting noise while preserving policy text."""

    line = raw_line.strip()

    # Remove decorative box/separator characters from the source.
    line = re.sub(
        r"[═╤╧╪╫╬╩╦╠╣╚╝╔╗╒╓╕╖╘╙╛╜╞╟╡╢╣╤╥╦╧╨╩╪╫╬]+",
        " ",
        line,
    )

    return re.sub(r"\s+", " ", line).strip()


def retrieve_policy(input_path: str):
    """
    Load the policy text file and return numbered clauses
    as structured sections.
    """

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        lines = infile.readlines()

    sections = []
    current_number = None
    current_lines = []

    for raw_line in lines:
        line = clean_line(raw_line)

        if not line:
            continue

        # Ignore standalone section headings such as:
        # "2. ANNUAL LEAVE"
        if re.match(r"^\d+\.\s+", line):
            continue

        match = CLAUSE_PATTERN.match(line)

        if match:
            # Save the previous clause.
            if current_number is not None:
                sections.append(
                    {
                        "clause": current_number,
                        "text": " ".join(current_lines).strip(),
                    }
                )

            current_number = match.group(1)
            current_lines = [match.group(2).strip()]

        elif current_number is not None:
            # Continuation line belonging to the current clause.
            current_lines.append(line)

    # Save the final clause.
    if current_number is not None:
        sections.append(
            {
                "clause": current_number,
                "text": " ".join(current_lines).strip(),
            }
        )

    return sections


def summarize_policy(sections):
    """
    Create a meaning-preserving clause-by-clause summary.

    Every numbered clause is retained so that conditions,
    obligations, thresholds, exceptions, and consequences
    cannot silently disappear.
    """

    output = [
        "EMPLOYEE LEAVE POLICY — CLAUSE-PRESERVING SUMMARY",
        "",
    ]

    for section in sections:
        output.append(
            f"{section['clause']}: {section['text']}"
        )

    return "\n".join(output) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the source policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the summary output file",
    )

    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)

        if not sections:
            raise ValueError(
                "No numbered policy clauses were found."
            )

        summary = summarize_policy(sections)

        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(summary)

        print(f"Done. Summary written to {args.output}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        raise


if __name__ == "__main__":
    main()
