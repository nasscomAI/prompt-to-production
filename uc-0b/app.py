"""Create a traceable, source-only summary of a numbered policy document.

The implementation deliberately preserves each clause verbatim (with whitespace
normalised).  This is the safe fallback required by agents.md: it prevents a
"summary" from dropping a condition, weakening an obligation, or adding policy
interpretation.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CLAUSE_START = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
SECTION_START = re.compile(r"^\s*\d+\.\s+\S")
DIVIDER = re.compile(r"^\s*[═=-]{3,}\s*$")


@dataclass(frozen=True)
class PolicyClause:
    """One numbered clause, retained exactly in source order."""

    reference: str
    text: str


def retrieve_policy(input_path: Path) -> list[PolicyClause]:
    """Load a UTF-8 policy file and return its numbered clauses.

    Continuation lines belong to the preceding clause. Non-clause document
    headings are not treated as policy clauses, so they cannot be mistaken for
    enforceable content.
    """

    try:
        source = input_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"Cannot read policy file '{input_path}': {error}") from error
    except UnicodeDecodeError as error:
        raise ValueError(f"Policy file '{input_path}' must be UTF-8 text.") from error

    clauses: list[PolicyClause] = []
    reference: str | None = None
    lines: list[str] = []

    def finish_clause() -> None:
        if reference is None:
            return
        text = " ".join(part.strip() for part in lines if part.strip())
        if not text:
            raise ValueError(f"Clause {reference} has no text.")
        clauses.append(PolicyClause(reference=reference, text=text))

    for raw_line in source.splitlines():
        match = CLAUSE_START.match(raw_line)
        if match:
            finish_clause()
            reference = match.group(1)
            lines = [match.group(2)]
        elif SECTION_START.match(raw_line) or DIVIDER.match(raw_line):
            # A section label or decorative separator ends the previous clause but
            # is not itself a numbered policy clause.
            finish_clause()
            reference = None
            lines = []
        elif reference is not None and raw_line.strip():
            lines.append(raw_line)

    finish_clause()

    if not clauses:
        raise ValueError("No numbered clauses were found; refusing to invent clause boundaries.")
    return clauses


def summarize_policy(clauses: Sequence[PolicyClause]) -> str:
    """Return a lossless, clause-by-clause policy summary.

    Verbatim clause wording is used because automatic paraphrasing could alter a
    binding verb, condition, party, threshold, date, exception, or consequence.
    """

    if not clauses:
        raise ValueError("Cannot summarise an empty clause collection.")

    return "\n\n".join(
        f"Clause {clause.reference}: {clause.text}\n"
        "[Verbatim source retained to prevent meaning loss.]"
        for clause in clauses
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a traceable, source-only summary of a numbered policy document."
    )
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 .txt policy file")
    parser.add_argument("--output", required=True, type=Path, help="Summary file to create")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input.suffix.lower() != ".txt":
        print("error: input must be a .txt policy file", file=sys.stderr)
        return 2

    try:
        summary = summarize_policy(retrieve_policy(args.input))
        args.output.write_text(summary, encoding="utf-8")
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: cannot write summary to '{args.output}': {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
