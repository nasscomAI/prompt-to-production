"""
UC-0B — Summary That Changes Meaning

Source-grounded policy summarizer.

The application deliberately preserves the source wording of the required
clauses so that obligations, conditions, thresholds, deadlines, approvers,
and consequences cannot be silently weakened or omitted.
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


def load_policy(input_path):
    """Load the policy document from disk."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    return path.read_text(encoding="utf-8")


def extract_clauses(text):
    """Extract numbered clauses and their source text."""
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.+?)(?=^\s*\d+\.\d+\s+|^\s*═{3,}\s*$|\Z)",
        re.DOTALL,
    )

    clauses = {}

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_number] = clause_text

    return clauses


def validate_required_clauses(clauses):
    """Ensure every required clause exists before producing output."""
    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Required clauses missing from source: "
            + ", ".join(missing)
        )


def build_summary(clauses):
    """Build a source-grounded summary preserving all required clauses."""
    lines = [
        "CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY",
        "Source-grounded summary of required clauses",
        "",
    ]

    for clause_number in REQUIRED_CLAUSES:
        lines.append(
            f"{clause_number}: {clauses[clause_number]}"
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Create a source-grounded HR leave policy summary."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy text file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary.",
    )

    args = parser.parse_args()

    policy_text = load_policy(args.input)
    clauses = extract_clauses(policy_text)

    validate_required_clauses(clauses)

    summary = build_summary(clauses)

    Path(args.output).write_text(
        summary,
        encoding="utf-8",
    )

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
