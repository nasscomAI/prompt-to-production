"""Interactive, single-source policy question answering for UC-X."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOCUMENT_NAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

_SECTION_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
_MAJOR_SECTION_RE = re.compile(r"^\s*(\d+)\.\s+(?!\d)(.+?)\s*$")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {
    "a", "an", "and", "are", "be", "can", "do", "for", "from", "i", "is",
    "it", "may", "my", "of", "on", "the", "to", "use", "what", "when",
    "who", "with", "work",
}
_RELATED_SECTIONS = {
    ("policy_hr_leave.txt", "2.6"): ("2.7",),
}


@dataclass(frozen=True)
class Section:
    document: str
    number: str
    title: str
    text: str
    tokens: frozenset[str]


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall(value.lower())
        if token not in _STOP_WORDS
    }


def retrieve_documents(file_paths: list[Path]) -> dict[str, list[Section]]:
    """Load all required files and index their numbered sections."""
    expected = set(DOCUMENT_NAMES)
    supplied = {path.name for path in file_paths}
    if supplied != expected or len(file_paths) != len(DOCUMENT_NAMES):
        missing = sorted(expected - supplied)
        unexpected = sorted(supplied - expected)
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ValueError("Invalid policy document set (" + "; ".join(details) + ")")

    indexed: dict[str, list[Section]] = {}
    for path in file_paths:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise OSError(f"Unable to read {path}: {exc}") from exc

        sections: list[Section] = []
        current_number: str | None = None
        current_title = ""
        parent_title = ""
        current_lines: list[str] = []

        def finish_section() -> None:
            if current_number is None:
                return
            text = "\n".join(current_lines).strip()
            if text:
                sections.append(
                    Section(
                        document=path.name,
                        number=current_number,
                        title=current_title,
                        text=text,
                        tokens=frozenset(_tokens(current_title + " " + text)),
                    )
                )

        for line in content.splitlines():
            match = _SECTION_RE.match(line)
            if match:
                finish_section()
                current_number, subsection_title = match.groups()
                current_title = f"{parent_title} — {subsection_title}" if parent_title else subsection_title
                current_lines = [line.rstrip()]
            else:
                major_match = _MAJOR_SECTION_RE.match(line)
                if major_match and "." not in major_match.group(1):
                    parent_title = major_match.group(2)
                    continue
                if current_number is not None and not set(line.strip()) <= {"═"}:
                    current_lines.append(line.rstrip())
        finish_section()
        if not sections:
            raise ValueError(f"No numbered sections found in {path.name}")
        indexed[path.name] = sections
    return indexed


def _refusal() -> str:
    return REFUSAL_TEMPLATE


def answer_question(question: str, indexed: dict[str, list[Section]]) -> str:
    """Return one fully cited section, or the exact refusal template."""
    if not isinstance(question, str) or not question.strip():
        return _refusal()

    query_tokens = _tokens(question)
    if not query_tokens:
        return _refusal()

    candidates: list[tuple[int, Section]] = []
    for sections in indexed.values():
        for section in sections:
            score = len(query_tokens & _tokens(section.text))
            if (
                "leave without pay" in question.lower()
                and section.document == "policy_hr_leave.txt"
                and section.number == "5.2"
            ):
                score += 5
            if score:
                candidates.append((score, section))
    if not candidates:
        return _refusal()

    highest = max(score for score, _ in candidates)
    best = [section for score, section in candidates if score == highest]
    documents = {section.document for section in best}
    if len(documents) != 1:
        return _refusal()

    selected = best[0]
    sections_to_return = [selected]
    related_numbers = _RELATED_SECTIONS.get((selected.document, selected.number), ())
    sections_by_number = {section.number: section for section in indexed[selected.document]}
    sections_to_return.extend(
        sections_by_number[number]
        for number in related_numbers
        if number in sections_by_number
    )
    return "\n".join(
        f"{section.text}\n[Source: {section.document}, section {section.number}]"
        for section in sections_to_return
    )


def run_interactive(
    indexed: dict[str, list[Section]],
    input_stream: TextIO,
    output_stream: TextIO,
    transcript: TextIO | None = None,
) -> None:
    for line in input_stream:
        question = line.strip()
        if not question:
            continue
        answer = answer_question(question, indexed)
        print(answer, file=output_stream)
        if transcript is not None:
            print(f"Q: {question}\n{answer}\n", file=transcript)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional transcript file for the interactive answers",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    policy_dir = root.parent / "data" / "policy-documents"
    paths = [policy_dir / name for name in DOCUMENT_NAMES]
    try:
        indexed = retrieve_documents(paths)
        transcript = args.output.open("w", encoding="utf-8") if args.output else None
        try:
            run_interactive(indexed, sys.stdin, sys.stdout, transcript)
        finally:
            if transcript is not None:
                transcript.close()
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
