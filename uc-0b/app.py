"""Generate a source-grounded summary of required leave-policy clauses.

With no configured language-model runtime, selected clauses are rendered
losslessly. This is the deterministic way to avoid weakening an obligation or
dropping a condition while producing a focused summary rather than the full
policy document.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


REQUIRED_CLAUSES = (
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2",
)
SECTION_PATTERN = re.compile(r"^(?P<number>\d+)\.\s+(?P<title>.+?)\s*$")
CLAUSE_PATTERN = re.compile(r"^(?P<number>\d+\.\d+)\s+(?P<text>.+?)\s*$")


@dataclass(frozen=True)
class PolicyClause:
    """One numbered policy clause, including its enclosing section."""

    number: str
    section: str
    text: str


def retrieve_policy(input_path: str) -> dict[str, PolicyClause]:
    """Read a policy file and return its numbered clauses keyed by number."""
    path = Path(input_path)
    try:
        policy_text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise OSError(f"Unable to read policy file '{path}': {error}") from error

    if not policy_text.strip():
        raise ValueError(f"Policy file '{path}' is empty.")

    clauses: dict[str, PolicyClause] = {}
    current_section: str | None = None
    current_number: str | None = None
    current_lines: list[str] = []

    def store_current_clause() -> None:
        if current_number is None:
            return
        text = " ".join(part.strip() for part in current_lines if part.strip())
        if not text:
            raise ValueError(f"Clause {current_number} has no policy text.")
        if current_number in clauses:
            raise ValueError(f"Duplicate clause number {current_number} in '{path}'.")
        if current_section is None:
            raise ValueError(f"Clause {current_number} appears before a numbered section.")
        clauses[current_number] = PolicyClause(current_number, current_section, text)

    for raw_line in policy_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        clause_match = CLAUSE_PATTERN.match(line)
        section_match = SECTION_PATTERN.match(line)

        if clause_match:
            store_current_clause()
            current_number = clause_match.group("number")
            current_lines = [clause_match.group("text")]
        elif section_match:
            store_current_clause()
            current_number = None
            current_lines = []
            current_section = f"{section_match.group('number')}. {section_match.group('title')}"
        elif current_number is not None and not all(character in "═─-= " for character in line):
            current_lines.append(line)

    store_current_clause()
    if not clauses:
        raise ValueError(f"Policy file '{path}' is malformed: no numbered clauses were found.")
    return clauses


def summarize_policy(policy_clauses: Mapping[str, PolicyClause]) -> str:
    """Produce a focused, meaning-preserving summary of required clauses."""
    missing = [number for number in REQUIRED_CLAUSES if number not in policy_clauses]
    if missing:
        raise ValueError("Policy is missing required clause(s): " + ", ".join(missing))

    lines = ["Employee Leave Policy: Required-Clause Summary", ""]
    for number in REQUIRED_CLAUSES:
        clause = policy_clauses[number]
        lines.append(f"{clause.number} — {clause.text}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy text file.")
    parser.add_argument("--output", required=True, help="Path for the summary file.")
    args = parser.parse_args()

    policy_clauses = retrieve_policy(args.input)
    summary = summarize_policy(policy_clauses)
    Path(args.output).write_text(summary + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
