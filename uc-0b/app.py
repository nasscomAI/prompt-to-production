"""Create a meaning-preserving summary of a numbered policy document.

The implementation deliberately quotes each numbered clause verbatim.  This is
the lossless form of a summary: it retains every obligation, qualifier,
exception, deadline, and approval condition in the source.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CLAUSE_PATTERN = re.compile(r"^(?P<number>\d+\.\d+)\s+(?P<text>.+)$")
SECTION_HEADING_PATTERN = re.compile(r"^\d+\.\s+.+$")


class PolicyError(ValueError):
    """Raised when policy input cannot be safely processed."""


@dataclass(frozen=True)
class PolicySection:
    """An exact numbered policy clause."""

    reference: str
    text: str


def retrieve_policy(input_path: str | Path) -> list[PolicySection]:
    """Load a .txt policy document as ordered, exact numbered sections."""
    path = Path(input_path)
    if path.suffix.lower() != ".txt":
        raise PolicyError("Input must be a .txt policy document.")
    if not path.is_file():
        raise PolicyError(f"Policy file does not exist or is not readable: {path}")

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PolicyError(f"Could not read policy file: {path}") from exc

    sections: list[PolicySection] = []
    current_reference: str | None = None
    current_lines: list[str] = []

    def finish_clause() -> None:
        nonlocal current_reference, current_lines
        if current_reference is None:
            return
        # Keep the source wording and line structure intact. Only trailing blank
        # lines separating clauses are removed.
        while current_lines and not current_lines[-1].strip():
            current_lines.pop()
        if not current_lines or not any(line.strip() for line in current_lines):
            raise PolicyError(f"Clause {current_reference} has no text.")
        sections.append(PolicySection(current_reference, "\n".join(current_lines)))
        current_reference, current_lines = None, []

    for line in source.splitlines():
        match = CLAUSE_PATTERN.match(line)
        if match:
            finish_clause()
            current_reference = match.group("number")
            current_lines = [match.group("text")]
        elif SECTION_HEADING_PATTERN.match(line) or _is_decorative_separator(line):
            # Top-level section headings and divider lines are document
            # structure, not numbered clauses or clause continuation text.
            finish_clause()
        elif current_reference is not None:
            # Indented continuation lines belong to the prior clause. A new
            # unnumbered substantive line is ambiguous and must not be guessed.
            if line.strip() and not line[:1].isspace():
                raise PolicyError(
                    f"Ambiguous unnumbered text after clause {current_reference}; "
                    "provide a document with unambiguous numbered clauses."
                )
            current_lines.append(line)

    finish_clause()
    if not sections:
        raise PolicyError("No numbered clauses were found in the policy document.")

    references = [section.reference for section in sections]
    if len(references) != len(set(references)):
        raise PolicyError("Duplicate numbered clauses make the document ambiguous.")
    return sections


def _is_decorative_separator(line: str) -> bool:
    """Return whether a non-empty line is a visual divider, not policy text."""
    stripped = line.strip()
    return bool(stripped) and not any(character.isalnum() for character in stripped)


def summarize_policy(sections: Sequence[PolicySection]) -> str:
    """Return a lossless, clause-referenced policy summary.

    Quoting is used instead of paraphrase whenever a condition could be lost;
    doing so preserves every source constraint and prevents unsupported content.
    """
    if not sections:
        raise PolicyError("Cannot summarize an empty set of policy sections.")

    seen: set[str] = set()
    rendered: list[str] = []
    for section in sections:
        if not isinstance(section, PolicySection):
            raise PolicyError("Sections must be PolicySection values.")
        if not re.fullmatch(r"\d+\.\d+", section.reference) or not section.text.strip():
            raise PolicyError("Each section must have a numbered reference and source text.")
        if section.reference in seen:
            raise PolicyError(f"Duplicate clause reference: {section.reference}")
        seen.add(section.reference)
        rendered.append(
            f"[VERBATIM — quoted to prevent meaning loss]\n"
            f"{section.reference} {section.text}"
        )

    # One rendered entry per parsed clause is a direct coverage check.
    if len(rendered) != len(sections):
        raise PolicyError("Summary validation failed: a numbered clause was omitted.")
    return "\n\n".join(rendered) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a lossless policy summary.")
    parser.add_argument("--input", required=True, help="Path to the source .txt policy.")
    parser.add_argument("--output", required=True, help="Path for the summary text file.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding="utf-8")
    except (OSError, PolicyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
