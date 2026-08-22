"""
UC-0B — HR Leave Policy Summarizer

Reads the HR leave policy, extracts the required clauses,
and produces a faithful summary without adding or removing
policy conditions.
"""

import argparse
import re
from pathlib import Path


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
    Load the policy and extract only the required numbered clauses.
    """

    text = Path(input_path).read_text(encoding="utf-8")

    sections = {}
    lines = text.splitlines()

    current_clause = None
    current_content = []

    def save_clause():
        """Save the current clause if it is one of the required clauses."""
        if current_clause in REQUIRED_CLAUSES:
            content = " ".join(current_content)

            # Remove decorative separator characters.
            content = re.sub(r"[═=]+", " ", content)

            # Normalize whitespace.
            content = re.sub(r"\s+", " ", content).strip()

            sections[current_clause] = content

    for line in lines:
        stripped = line.strip()

        # Match numbered policy clauses such as:
        # 2.3 ...
        # 5.2 ...
        clause_match = re.match(
            r"^(\d+\.\d+)\s+(.*)$",
            stripped
        )

        if clause_match:
            # Save the previous clause before starting a new one.
            save_clause()

            current_clause = clause_match.group(1)
            current_content = [clause_match.group(2)]

            continue

        # Section headings such as:
        # 3. SICK LEAVE
        # 4. MATERNITY AND PATERNITY LEAVE
        section_match = re.match(
            r"^\d+\.\s+[A-Z]",
            stripped
        )

        if section_match:
            save_clause()

            current_clause = None
            current_content = []

            continue

        # Ignore decorative-only lines.
        if stripped and re.fullmatch(r"[═=*\-_ ]+", stripped):
            continue

        # Continue collecting the current clause.
        if current_clause is not None and stripped:
            current_content.append(stripped)

    # Save the final clause.
    save_clause()

    return sections


def validate_sections(sections):
    """
    Ensure that every required clause is present.
    Refuse to generate a summary if any clause is missing.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in sections
    ]

    if missing:
        raise ValueError(
            "Cannot generate a reliable summary. "
            "Missing required clauses: "
            + ", ".join(missing)
        )


def summarize_policy(sections):
    """
    Generate a faithful summary containing every required clause.
    """

    validate_sections(sections)

    lines = []

    for clause in REQUIRED_CLAUSES:
        lines.append(
            f"{clause} — {sections[clause]}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a faithful HR leave policy summary."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary file.",
    )

    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    summary = summarize_policy(sections)

    Path(args.output).write_text(
        summary + "\n",
        encoding="utf-8",
    )

    print(
        f"Summary written to: {args.output}"
    )


if __name__ == "__main__":
    main()