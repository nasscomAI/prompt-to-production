"""Clause-preserving summarizer for the UC-0B HR leave policy.

The implementation is deliberately extractive: the source policy is the sole
authority, so it does not add interpretations or outside HR information.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
SECTION_HEADING_RE = re.compile(r"^\d+\.\s+\S")
SEPARATOR_RE = re.compile(r"^[^\w]*$")
CLAUSE_NUMBER_ONLY_RE = re.compile(r"^\s*\d+\.\d+\s*$")
INDENTED_CLAUSE_RE = re.compile(r"^\s+\d+\.\d+")

# Complete inventory of the supplied HR leave policy. A summary that silently
# drops any clause changes the document's meaning, so every reference must be
# present before the policy is considered complete.
EXPECTED_CLAUSE_NUMBERS = [
    "1.1", "1.2",
    "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3", "5.4",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3",
    "8.1", "8.2",
]


def _clause_sort_key(number: str):
    major, minor = number.split(".")
    return (int(major), int(minor))


def _validate_inventory(clauses: List[Tuple[str, str]]) -> None:
    present = {number for number, _ in clauses}
    missing = sorted(set(EXPECTED_CLAUSE_NUMBERS) - present, key=_clause_sort_key)
    if missing:
        raise ValueError("Missing policy clauses: " + ", ".join(missing))


def retrieve_policy(path: str) -> List[Tuple[str, str]]:
    """Load a UTF-8 text policy and return its numbered clauses in order.

    Every non-empty policy line must either begin a numbered clause, continue
    the currently open clause with indentation, or be a section/decorative
    line. Clause-shaped lines that do not match the exact clause pattern are
    rejected rather than silently attached to a neighbouring clause.
    """
    policy_path = Path(path)
    if not policy_path.is_file():
        raise ValueError(f"Input policy file does not exist: {path}")

    try:
        text = policy_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Could not read UTF-8 policy file: {path}") from exc

    if not text.strip():
        raise ValueError("The input policy is empty")

    clauses: List[Tuple[str, str]] = []
    current_number = None
    current_parts: List[str] = []
    seen_clause = False

    def finish_clause() -> None:
        nonlocal current_number, current_parts
        if current_number is not None:
            clause_text = " ".join(current_parts).strip()
            if not clause_text:
                raise ValueError(f"Clause {current_number} has no text")
            clauses.append((current_number, clause_text))
        current_number = None
        current_parts = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        clause_match = CLAUSE_RE.match(raw_line)
        if clause_match:
            finish_clause()
            seen_clause = True
            current_number = clause_match.group(1)
            current_parts = [clause_match.group(2)]
            continue

        # Reject clause-shaped lines that fail the exact clause pattern before
        # they can be mistaken for preamble or continuations.
        if CLAUSE_NUMBER_ONLY_RE.match(raw_line):
            raise ValueError(f"Clause on line {line_number} has no text")
        if INDENTED_CLAUSE_RE.match(raw_line):
            raise ValueError(
                f"Ambiguous indented clause on line {line_number}; review the policy input"
            )

        if SEPARATOR_RE.fullmatch(stripped):
            continue
        if SECTION_HEADING_RE.match(stripped):
            finish_clause()
            continue

        if current_number is None:
            if not seen_clause:
                # Title, reference, version, and other preamble metadata sit before
                # the first numbered clause and are not part of the inventory.
                continue
            raise ValueError(
                f"Unexpected policy text on line {line_number}: {stripped}"
            )

        if not raw_line[:1].isspace():
            raise ValueError(
                f"Ambiguous unindented text on line {line_number}; review the policy input"
            )
        current_parts.append(stripped)

    finish_clause()

    if not clauses:
        raise ValueError("No numbered policy clauses were found in the input")

    numbers = [number for number, _ in clauses]
    duplicates = sorted(
        {number for number in numbers if numbers.count(number) > 1},
        key=_clause_sort_key,
    )
    if duplicates:
        raise ValueError("Duplicate clause numbers found: " + ", ".join(duplicates))

    _validate_inventory(clauses)
    return clauses


def summarize_policy(clauses: List[Tuple[str, str]]) -> str:
    """Create a clause-referenced summary without changing source meaning."""
    if not clauses:
        raise ValueError("Cannot summarize an empty clause list")
    _validate_inventory(clauses)

    for number, text in clauses:
        if not number or not (text or "").strip():
            raise ValueError(f"Clause {number} is missing its number or text")

    lines = [
        "HR EMPLOYEE LEAVE POLICY - CLAUSE-PRESERVING SUMMARY",
        "Source: supplied HR leave policy",
        "",
    ]
    for number, text in clauses:
        # One source-derived entry per clause preserves conditions, thresholds,
        # approvers, deadlines, exceptions, and consequences.
        lines.append(f"Clause {number}: {text}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a clause-preserving summary of an HR leave policy."
    )
    parser.add_argument("--input", required=True, help="Path to the UTF-8 .txt policy")
    parser.add_argument("--output", required=True, help="Path for the summary .txt file")
    args = parser.parse_args(argv)

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(clauses)} clause summaries to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
