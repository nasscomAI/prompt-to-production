"""
UC-0B: Policy summarizer.

Reads the supplied HR leave policy and produces a clause-referenced
summary without dropping conditions or adding outside information.
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
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("Policy file is empty")

    return text


def extract_clauses(text):
    """
    Extract numbered clauses from the policy.

    A clause starts with a number such as 2.3 and continues until
    the next numbered clause or the end of the document.
    """
    pattern = re.compile(
        r"(?ms)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)"
    )

    clauses = {}

    for match in pattern.finditer(text):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_number] = clause_text

    return clauses


def summarize_policy(text):
    clauses = extract_clauses(text)

    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses]

    if missing:
        raise ValueError(
            "Required clauses missing from source policy: "
            + ", ".join(missing)
        )

    lines = [
        "CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY SUMMARY",
        "Source: HR-POL-001, Version 2.3",
        "",
        "The following summary preserves all required policy clauses and their conditions:",
        "",
    ]

    for clause in REQUIRED_CLAUSES:
        lines.append(f"Clause {clause}: {clauses[clause]}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a clause-preserving HR leave policy summary."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    source = retrieve_policy(args.input)
    summary = summarize_policy(source)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()

