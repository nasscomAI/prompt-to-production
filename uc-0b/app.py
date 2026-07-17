"""UC-0B policy clause summarizer.

This CLI app is deliberately strict:
- it loads the HR leave policy text,
- preserves the exact numbered clauses listed in the task,
- and refuses to summarize in a lossy or softened way.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CLAUSE_ORDER = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def fail(message: str) -> None:
    print(f"REFUSE: {message}")
    sys.exit(1)


def parse_policy_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_clause = None
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith("═"):
            continue

        if re.match(r"^\d+\.\s+[A-Z0-9 &–-]+$", stripped):
            continue

        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current_clause is not None:
                sections[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif current_clause is not None:
            current_lines.append(stripped)

    if current_clause is not None:
        sections[current_clause] = " ".join(current_lines).strip()

    return sections


def build_summary(text: str) -> str:
    sections = parse_policy_sections(text)
    missing = [clause for clause in CLAUSE_ORDER if clause not in sections]
    if missing:
        fail(f"Required clauses are missing from the policy file: {', '.join(missing)}")

    lines = [
        "UC-0B Clause-Preserving Summary",
        "===============================",
        "",
    ]

    for clause in CLAUSE_ORDER:
        quote = sections[clause]
        lines.append(f"{clause}: {quote}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a clause-preserving summary of the HR leave policy.")
    parser.add_argument("--input", required=True, help="Path to the policy TXT file")
    parser.add_argument("--output", required=True, help="Path to the output summary file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        fail(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    summary = build_summary(text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Wrote summary to {output_path}")


if __name__ == "__main__":
    main()
