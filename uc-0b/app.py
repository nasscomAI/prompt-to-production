"""Create a meaning-preserving, clause-by-clause HR leave policy summary."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CLAUSE_START = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
SECTION_HEADING = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
DECORATIVE_LINE = re.compile(r"^\s*[═=\-]{3,}\s*$")

REQUIRED_CLAUSES = frozenset(
    {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
)


class PolicyError(ValueError):
    """Raised when a policy cannot be processed without guessing."""


@dataclass(frozen=True)
class PolicyClause:
    number: str
    text: str
    section_number: str | None
    section_title: str | None


@dataclass(frozen=True)
class PolicyDocument:
    preamble: tuple[str, ...]
    clauses: tuple[PolicyClause, ...]


def _normalize_whitespace(parts: Sequence[str]) -> str:
    """Join wrapped source lines without changing their wording."""
    return " ".join(" ".join(parts).split())


def retrieve_policy(input_path: Path) -> PolicyDocument:
    """Load a UTF-8 policy and return its ordered, numbered clauses."""
    if input_path.suffix.lower() != ".txt":
        raise PolicyError(f"input must be a .txt file: {input_path}")

    try:
        raw_text = input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PolicyError(f"input file does not exist: {input_path}") from exc
    except UnicodeDecodeError as exc:
        raise PolicyError(f"input is not valid UTF-8 text: {input_path}") from exc
    except OSError as exc:
        raise PolicyError(f"cannot read input file {input_path}: {exc}") from exc

    if not raw_text.strip():
        raise PolicyError(f"input file is empty: {input_path}")

    preamble: list[str] = []
    clauses: list[PolicyClause] = []
    seen_numbers: set[str] = set()
    current_number: str | None = None
    current_text: list[str] = []
    current_section_number: str | None = None
    current_section_title: str | None = None

    def finish_clause() -> None:
        nonlocal current_number, current_text
        if current_number is None:
            return
        text = _normalize_whitespace(current_text)
        if not text:
            raise PolicyError(f"clause {current_number} has no content")
        clauses.append(
            PolicyClause(
                number=current_number,
                text=text,
                section_number=current_section_number,
                section_title=current_section_title,
            )
        )
        current_number = None
        current_text = []

    for line_number, line in enumerate(raw_text.splitlines(), start=1):
        clause_match = CLAUSE_START.match(line)
        if clause_match:
            finish_clause()
            number, first_line = clause_match.groups()
            if number in seen_numbers:
                raise PolicyError(
                    f"duplicate clause number {number} at line {line_number}"
                )
            seen_numbers.add(number)
            current_number = number
            current_text = [first_line]
            continue

        section_match = SECTION_HEADING.match(line)
        if section_match:
            finish_clause()
            current_section_number, current_section_title = section_match.groups()
            current_section_title = _normalize_whitespace([current_section_title])
            continue

        if DECORATIVE_LINE.match(line) or not line.strip():
            continue

        if current_number is not None:
            current_text.append(line.strip())
        elif current_section_number is None:
            preamble.append(line.strip())
        else:
            raise PolicyError(
                f"unstructured text after section {current_section_number} "
                f"at line {line_number}: {line.strip()!r}"
            )

    finish_clause()

    if not clauses:
        raise PolicyError("no numbered clauses were found in the input")

    return PolicyDocument(
        preamble=tuple(line for line in preamble if line),
        clauses=tuple(clauses),
    )


def _validate_required_clauses(document: PolicyDocument) -> None:
    present = {clause.number for clause in document.clauses}
    missing = sorted(REQUIRED_CLAUSES - present, key=lambda item: tuple(map(int, item.split("."))))
    if missing:
        raise PolicyError(
            "required HR leave clauses are missing: " + ", ".join(missing)
        )


def summarize_policy(document: PolicyDocument) -> str:
    """Render a traceable extractive summary with complete clause coverage."""
    _validate_required_clauses(document)

    output: list[str] = ["EMPLOYEE LEAVE POLICY — CLAUSE SUMMARY", ""]
    active_section: tuple[str | None, str | None] | None = None

    for clause in document.clauses:
        section = (clause.section_number, clause.section_title)
        if section != active_section:
            if active_section is not None:
                output.append("")
            if clause.section_number and clause.section_title:
                output.append(f"{clause.section_number}. {clause.section_title}")
            active_section = section

        # Extractive output is deliberate: changing or removing words from policy
        # obligations can soften scope or silently discard a condition.
        output.append(f"{clause.number} {clause.text}")

    summarized_numbers = {
        line.split(maxsplit=1)[0]
        for line in output
        if CLAUSE_START.match(line)
    }
    source_numbers = {clause.number for clause in document.clauses}
    if summarized_numbers != source_numbers:
        missing = sorted(source_numbers - summarized_numbers)
        extra = sorted(summarized_numbers - source_numbers)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise PolicyError("summary clause coverage failed: " + "; ".join(details))

    return "\n".join(output).rstrip() + "\n"


def _write_atomically(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_name = temporary.name
        os.replace(temporary_name, output_path)
    except OSError as exc:
        if temporary_name:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise PolicyError(f"cannot write output file {output_path}: {exc}") from exc


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a meaning-preserving HR leave policy summary."
    )
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 policy .txt file")
    parser.add_argument("--output", required=True, type=Path, help="summary output path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        document = retrieve_policy(args.input)
        summary = summarize_policy(document)
        _write_atomically(args.output, summary)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
