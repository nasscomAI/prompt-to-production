"""UC-0B leave-policy summary generator.

This app reads the source policy file, extracts the clauses required by
README.md, and writes a compliant summary without softening conditions.
"""

from __future__ import annotations

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


def extract_clause_blocks(policy_text: str) -> dict[str, str]:
    """Extract numbered policy clauses from the HR leave policy text."""
    lines = policy_text.splitlines()
    clauses: dict[str, str] = {}
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        match = re.match(r"^(\d+\.\d+)\b", stripped)

        if not match:
            i += 1
            continue

        clause_id = match.group(1)
        block = [stripped]
        i += 1

        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                i += 1
                continue

            if re.match(r"^\d+\.\d+\b", next_line):
                break

            if re.match(r"^\d+\.\b", next_line):
                break

            if next_line.startswith("════════"):
                break

            block.append(next_line)
            i += 1

        clauses[clause_id] = " ".join(block)

    return clauses


def build_summary(policy_text: str) -> str:
    """Build a summary that preserves each required clause and condition."""
    clauses = extract_clause_blocks(policy_text)
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")

    summary_lines = []
    for clause in REQUIRED_CLAUSES:
        clause_text = clauses[clause]
        summary_lines.append(f"{clause} {clause_text.split(f'{clause} ', 1)[1] if f'{clause} ' in clause_text else clause_text}")

    return "\n\n".join(summary_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a compliant HR leave policy summary.")
    parser.add_argument("--input", required=True, help="Path to the source policy .txt file")
    parser.add_argument("--output", required=True, help="Path for the generated summary output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input policy file not found: {input_path}")

    policy_text = input_path.read_text(encoding="utf-8")
    summary = build_summary(policy_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()
