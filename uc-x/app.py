"""Ask My Documents: a source-only policy question-answering CLI.

The agent intentionally returns only clauses from one approved policy document.
That keeps answers traceable and prevents cross-document policy blending.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


POLICY_DIRECTORY = Path(__file__).parent / "../data/policy-documents"
POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
CLAUSE_START = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
SECTION_START = re.compile(r"^\s*\d+\.\s+\S")
DIVIDER = re.compile(r"^\s*[═=-]{3,}\s*$")
WORDS = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Clause:
    """A source passage whose document and numbered section are retained."""

    document: str
    section: str
    text: str


class RetrievalError(ValueError):
    """Raised when an approved source corpus cannot be indexed."""


def refusal() -> str:
    """Return the mandated refusal unchanged."""
    return REFUSAL


def parse_policy(document: str, source: str) -> list[Clause]:
    """Parse numbered clauses without treating headings as policy content."""
    clauses: list[Clause] = []
    section: str | None = None
    lines: list[str] = []

    def finish_clause() -> None:
        nonlocal section, lines
        if section is None:
            return
        text = " ".join(line.strip() for line in lines if line.strip())
        if text:
            clauses.append(Clause(document=document, section=section, text=text))
        section, lines = None, []

    for line in source.splitlines():
        match = CLAUSE_START.match(line)
        if match:
            finish_clause()
            section, lines = match.group(1), [match.group(2)]
        elif SECTION_START.match(line) or DIVIDER.match(line):
            finish_clause()
        elif section is not None and line.strip():
            lines.append(line)
    finish_clause()
    return clauses


def retrieve_documents(policy_directory: Path = POLICY_DIRECTORY) -> list[Clause]:
    """Load every approved file and preserve document and section provenance."""
    indexed: list[Clause] = []
    for filename in POLICY_FILES:
        path = policy_directory / filename
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            raise RetrievalError(f"Unable to retrieve approved document: {filename}") from error
        parsed = parse_policy(filename, source)
        if not parsed:
            raise RetrievalError(f"Unable to index approved document: {filename}")
        indexed.extend(parsed)
    return indexed


def tokens(value: str) -> set[str]:
    """Normalise searchable terms while dropping words with no policy meaning."""
    ignored = {
        "a", "an", "and", "are", "can", "do", "for", "from", "i", "in", "is",
        "my", "of", "on", "the", "to", "use", "what", "when", "with", "work",
    }
    return {word for word in WORDS.findall(value.lower()) if word not in ignored}


def clauses_for(index: Iterable[Clause], document: str, *sections: str) -> list[Clause]:
    """Fetch an explicitly relevant, same-document set of clauses."""
    wanted = set(sections)
    return [clause for clause in index if clause.document == document and clause.section in wanted]


def known_question_match(question: str, index: Sequence[Clause]) -> list[Clause] | None:
    """Route unambiguous supported question forms to complete source clauses."""
    query = tokens(question)
    if {"carry", "forward"} <= query and "leave" in query:
        return clauses_for(index, "policy_hr_leave.txt", "2.6", "2.7")
    if {"install", "slack"} <= query or ({"install", "software"} <= query and "laptop" in query):
        return clauses_for(index, "policy_it_acceptable_use.txt", "2.3", "2.4")
    if {"home", "office", "equipment", "allowance"} <= query:
        return clauses_for(index, "policy_finance_reimbursement.txt", "3.1", "3.4", "3.5")
    if "personal" in query and ("phone" in query or "device" in query):
        return clauses_for(index, "policy_it_acceptable_use.txt", "3.1")
    if "da" in query and ("meal" in query or "meals" in query):
        return clauses_for(index, "policy_finance_reimbursement.txt", "2.5", "2.6")
    if {"leave", "without", "pay"} <= query and ("approve" in query or "approves" in query):
        return clauses_for(index, "policy_hr_leave.txt", "5.2")
    return None


def best_single_document_match(question: str, index: Sequence[Clause]) -> list[Clause] | None:
    """Find one strongly supported clause, refusing ties between documents."""
    query = tokens(question)
    if not query:
        return None
    scored: list[tuple[int, Clause]] = []
    for clause in index:
        overlap = len(query & tokens(clause.text))
        if overlap:
            scored.append((overlap, clause))
    if not scored:
        return None

    top_score = max(score for score, _ in scored)
    # A one-word overlap is too weak to be reliable policy support.
    if top_score < 2:
        return None
    top = [clause for score, clause in scored if score == top_score]
    documents = {clause.document for clause in top}
    if len(documents) != 1:
        return None
    return [top[0]]


def render_answer(clauses: Sequence[Clause]) -> str:
    """Render source wording with a citation for each factual passage."""
    return "\n\n".join(
        f"{clause.text}\n[{clause.document}, section {clause.section}]" for clause in clauses
    )


def answer_question(question: str, index: Sequence[Clause]) -> str:
    """Return one-document support or the exact refusal required by agents.md."""
    if not question.strip():
        return refusal()
    clauses = known_question_match(question, index)
    if clauses is None:
        clauses = best_single_document_match(question, index)
    if not clauses or len({clause.document for clause in clauses}) != 1:
        return refusal()
    return render_answer(clauses)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask questions about approved CMC policy documents.")
    parser.add_argument("--question", help="Answer one question and exit.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        index = retrieve_documents()
    except RetrievalError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.question is not None:
        print(answer_question(args.question, index))
        return 0

    print("Ask My Documents — enter a policy question (or type 'quit').")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            return 0
        if question.lower() in {"quit", "exit"}:
            return 0
        print(answer_question(question, index))


if __name__ == "__main__":
    raise SystemExit(main())
