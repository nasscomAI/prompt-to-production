"""UC-0B policy summarization tool.

Reads an HR leave policy text file, extracts numbered clauses,
and writes a compliance-preserving summary for required clauses.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List

REQUIRED_CLAUSES: List[str] = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
CLAUSE_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)?\s*$")
DISALLOWED_SCOPE_BLEED = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

REQUIRED_CONDITION_KEYWORDS: Dict[str, List[str]] = {
    "2.4": ["written", "verbal"],
    "2.6": ["5", "forfeit"],
    "2.7": ["jan", "mar", "forfeit"],
    "3.2": ["3", "medical", "48"],
    "3.4": ["before", "after", "holiday", "medical"],
    "5.2": ["department head", "hr director"],
    "5.3": ["30", "municipal commissioner"],
    "7.2": ["not permitted"],
}


class ClarificationNeededError(Exception):
    """Raised when required clauses are missing or ambiguous in source text."""


def retrieve_policy(input_path: Path) -> Dict[str, str]:
    """Load policy text and return clause-numbered content.

    Returns:
        Mapping of clause number (e.g., "2.3") to clause text.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    raw_text = input_path.read_text(encoding="utf-8")
    if not raw_text.strip():
        raise ValueError("Input file is empty")

    clauses: Dict[str, str] = {}
    current_clause: str | None = None
    current_lines: List[str] = []

    for line in raw_text.splitlines():
        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause is not None:
                clauses[current_clause] = " ".join(part.strip() for part in current_lines if part.strip()).strip()
            current_clause = match.group(1)
            first_text = (match.group(2) or "").strip()
            current_lines = [first_text] if first_text else []
            continue

        if current_clause is not None:
            stripped = line.strip()
            if stripped:
                current_lines.append(stripped)

    if current_clause is not None:
        clauses[current_clause] = " ".join(part.strip() for part in current_lines if part.strip()).strip()

    if not clauses:
        raise ValueError("No numbered clauses could be parsed from input text")

    return clauses


def summarize_policy(clauses: Dict[str, str]) -> str:
    """Create a clause-preserving summary for the required clauses."""
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses or not clauses[clause].strip()]
    if missing:
        missing_text = ", ".join(missing)
        raise ClarificationNeededError(
            f"clarification-needed: required clause text missing/ambiguous for {missing_text}"
        )

    ambiguous_conditions: List[str] = []
    for clause, keywords in REQUIRED_CONDITION_KEYWORDS.items():
        source = clauses.get(clause, "").lower()
        if not all(keyword in source for keyword in keywords):
            ambiguous_conditions.append(clause)

    if ambiguous_conditions:
        missing_text = ", ".join(ambiguous_conditions)
        raise ClarificationNeededError(
            f"clarification-needed: required conditions missing/ambiguous for {missing_text}"
        )

    lines: List[str] = []
    lines.append("Summary (required clauses):")

    for clause in REQUIRED_CLAUSES:
        clause_text = clauses[clause].strip()
        if not clause_text or len(clause_text.split()) < 4:
            lines.append(f"- {clause}: [FLAGGED_VERBATIM] \"{clauses[clause]}\"")
            continue

        lines.append(f"- {clause}: {clause_text}")

    summary_text = "\n".join(lines) + "\n"
    lower_summary = summary_text.lower()
    found_scope_bleed = [phrase for phrase in DISALLOWED_SCOPE_BLEED if phrase in lower_summary]
    if found_scope_bleed:
        phrase_text = ", ".join(found_scope_bleed)
        raise ClarificationNeededError(
            f"clarification-needed: unsupported scope-bleed text detected in summary: {phrase_text}"
        )

    return summary_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate compliance-preserving summary for UC-0B")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        clauses = retrieve_policy(input_path)
        summary = summarize_policy(clauses)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")
    except ClarificationNeededError as error:
        print(str(error), file=sys.stderr)
        return 2
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
