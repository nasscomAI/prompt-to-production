"""UC-0B policy summarizer.

This script reads a leave-policy text file, extracts the required numbered clauses,
and writes a clause-by-clause summary that preserves all conditions from the source.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List

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
CLAUSE_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\s*\d+\.\s+[A-Z][A-Z0-9 /&()'-]+$")


def is_ignored_line(line: str) -> bool:
    """Return True for decorative separators or section headings that should not be stored as clause text."""
    if not line:
        return True
    if re.fullmatch(r"[═\s]+", line):
        return True

    normalized = re.sub(r"^[═\s]+|[═\s]+$", "", line)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return True
    return bool(SECTION_HEADER_PATTERN.match(normalized))


def parse_policy(text: str) -> Dict[str, str]:
    """Extract numbered clauses from the policy text."""
    clauses: Dict[str, str] = {}
    current_clause: str | None = None
    current_lines: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause is not None:
                clauses[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif current_clause is not None and not is_ignored_line(line):
            current_lines.append(line)

    if current_clause is not None:
        clauses[current_clause] = " ".join(current_lines).strip()

    return clauses


def build_summary(clauses: Dict[str, str]) -> str:
    """Create a faithful summary with the required clauses."""
    lines = ["Leave policy summary", "==================="]
    for clause_id in REQUIRED_CLAUSES:
        text = clauses.get(clause_id, "[Clause not found in source document]")
        lines.append(f"{clause_id}: {text}")
    return "\n".join(lines) + "\n"


def resolve_path(path_str: str, base_dir: Path, is_output: bool = False) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = base_dir / path
    path = path.resolve()
    if is_output:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Summarize the HR leave policy clauses")
    parser.add_argument(
        "--input",
        default=str(base_dir.parent / "data" / "policy-documents" / "policy_hr_leave.txt"),
        help="Path to the source policy text file",
    )
    parser.add_argument(
        "--output",
        default=str(base_dir / "summary_hr_leave.txt"),
        help="Path to write the summary output",
    )
    args = parser.parse_args()

    input_path = resolve_path(args.input, base_dir)
    output_path = resolve_path(args.output, base_dir, is_output=True)

    text = input_path.read_text(encoding="utf-8")
    clauses = parse_policy(text)
    summary = build_summary(clauses)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Wrote summary to {output_path}")


if __name__ == "__main__":
    main()
