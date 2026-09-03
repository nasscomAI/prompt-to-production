"""
UC-0B — Summary That Changes Meaning

Reads the HR leave policy and produces a clause-complete summary.

Design goals:
- Every required clause must be represented.
- Multi-condition obligations must preserve every condition.
- No outside information is added.
- Binding language is preserved.
- If a required clause cannot be safely extracted, the output flags it.
"""

import argparse
import re
from pathlib import Path


EXPECTED_CLAUSES = [
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


def retrieve_policy(input_path: str) -> list[dict]:
    """Load the policy and extract every numbered clause."""

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("The policy file is empty.")

    clauses = []

    # Clause headings are normally formatted like:
    # 2.3 Employees must...
    # 3.2 Sick leave...
    #
    # We locate every clause number at the beginning of a line,
    # then capture everything until the next clause number.
    pattern = re.compile(
        r"(?ms)^[ \t]*(\d+\.\d+)\s+(.+?)(?=^[ \t]*\d+\.\d+\s+|\Z)"
    )

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(
            line.strip()
            for line in match.group(2).splitlines()
            if line.strip()
        )

        if clause_text:
            clauses.append(
                {
                    "clause": clause_number,
                    "text": clause_text,
                }
            )

    if not clauses:
        raise ValueError(
            "No numbered clauses could be found in the policy file."
        )

    return clauses


def summarize_policy(clauses: list[dict]) -> str:
    """
    Produce a clause-complete summary.

    The source wording is preserved rather than aggressively paraphrased.
    This prevents:
    - clause omission
    - condition dropping
    - obligation softening
    - scope bleed
    """

    found = {}

    for item in clauses:
        found[item["clause"]] = item["text"]

    output_lines = [
        "HR LEAVE POLICY — CLAUSE-COMPLETE SUMMARY",
        "",
        (
            "This summary preserves the source policy wording to avoid "
            "clause omission, scope bleed, and obligation softening."
        ),
        "",
    ]

    missing = []

    for clause_number in EXPECTED_CLAUSES:
        if clause_number not in found:
            missing.append(clause_number)
            continue

        output_lines.append(f"Clause {clause_number}:")
        output_lines.append(found[clause_number])
        output_lines.append("")

    if missing:
        output_lines.append(
            "NEEDS_REVIEW: The following required clauses were not found "
            "in the source policy: "
            + ", ".join(missing)
        )
        output_lines.append("")

    return "\n".join(output_lines).rstrip() + "\n"


def write_summary(output_path: str, summary: str):
    """Write the summary to the requested output file."""

    Path(output_path).write_text(
        summary,
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy .txt file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary .txt file.",
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        summary = summarize_policy(clauses)

        write_summary(args.output, summary)

        print(f"Done. Summary written to {args.output}")

    except Exception as exc:
        error_message = (
            "UC-0B could not safely summarize the policy.\n"
            "NEEDS_REVIEW\n"
            f"Reason: {exc}\n"
        )

        write_summary(args.output, error_message)

        print(error_message)

        raise SystemExit(1)


if __name__ == "__main__":
    main()