"""
UC-0B — Summary That Changes Meaning

Deterministic policy summarizer.
Uses only the supplied policy document and standard-library Python.
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
    """Read the policy and extract numbered clauses."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("Policy file is empty.")

    clauses = {}

    # Extract clauses such as 2.3, 5.2, and 7.2.
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        number = match.group(1)
        content = " ".join(match.group(2).split())

        # Remove section divider/header text.
        divider = content.find("═")
        if divider != -1:
            content = content[:divider].strip()

        # Restore missing spaces caused by source formatting.
        content = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", content)
        content = re.sub(r"(\d)([A-Za-z])", r"\1 \2", content)
        content = re.sub(r"([a-z])([A-Z])", r"\1 \2", content)

        clauses[number] = content

    if not clauses:
        raise ValueError("No numbered policy clauses were found.")

    return clauses


def summarize_policy(clauses):
    """Create a deterministic summary of the ten required clauses."""

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Required policy clauses are missing: "
            + ", ".join(missing)
        )

    summary = [
        "HR Leave Policy — Required Clause Summary",
        "",
        f"2.3 — {clauses['2.3']}",
        f"2.4 — {clauses['2.4']}",
        f"2.5 — {clauses['2.5']}",
        f"2.6 — {clauses['2.6']}",
        f"2.7 — {clauses['2.7']}",
        f"3.2 — {clauses['3.2']}",
        f"3.4 — {clauses['3.4']}",
        f"5.2 — {clauses['5.2']}",
        f"5.3 — {clauses['5.3']}",
        f"7.2 — {clauses['7.2']}",
    ]

    output = "\n".join(summary)

    # Verify every required clause is present.
    for clause in REQUIRED_CLAUSES:
        if not re.search(
            rf"(?m)^{re.escape(clause)}\s+—",
            output,
        ):
            raise ValueError(
                f"Validation failed: clause {clause} is missing."
            )

    if not output.strip():
        raise ValueError("Generated summary is empty.")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate a clause-preserving HR policy summary."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    output_path = Path(args.output)

    output_path.write_text(
        summary + "\n",
        encoding="utf-8",
    )

    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()