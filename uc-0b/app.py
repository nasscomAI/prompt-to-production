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
    """Load the policy and extract numbered clauses."""

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="cp1252")

    if not text.strip():
        raise ValueError("Policy file is empty.")

    clauses = {}

    # Extract each numbered clause.
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = match.group(2)

        # Remove decorative separator characters and section headings.
        clause_text = re.sub(r"[═╔╗╚╝╠╣╦╩╬║]+", " ", clause_text)

        # Remove accidental section headings after a clause.
        clause_text = re.sub(
            r"\s+\d+\.\s+[A-Z][A-Z\s&]+\s*$",
            "",
            clause_text,
        )

        # Convert multiple spaces/newlines into one space.
        clause_text = " ".join(clause_text.split())

        clauses[clause_number] = clause_text.strip()

    if not clauses:
        raise ValueError("No numbered policy clauses were found.")

    return clauses


def summarize_policy(clauses):
    """Create a clause-preserving summary."""

    missing = [
        clause for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Required clauses missing: " + ", ".join(missing)
        )

    lines = [
        "HR LEAVE POLICY — CLAUSE-PRESERVING SUMMARY",
        "",
        "The following summary contains the required policy clauses "
        "using only information from the source document.",
        "",
    ]

    for clause in REQUIRED_CLAUSES:
        lines.append(f"{clause}: {clauses[clause]}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a clause-preserving HR leave summary."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output summary file",
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        output_path = Path(args.output)
        output_path.write_text(summary, encoding="utf-8")

        print(
            f"Summary written successfully to: {output_path}"
        )

    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()