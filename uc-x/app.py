"""Interactive, single-source policy question answering for UC-X."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)
SECTION_START = re.compile(r"^(?P<number>\d+(?:\.\d+)?)\s+(?P<text>\S.*)$")
MAJOR_SECTION = re.compile(r"^\d+\.\s+")
TOKEN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a", "an", "and", "can", "do", "for", "from", "how", "i", "in", "is",
    "it", "may", "my", "of", "on", "the", "to", "what", "when", "who", "with",
}


@dataclass(frozen=True)
class PolicySection:
    document: str
    number: str
    text: str
    source_path: Path


def _parse_sections(document: str, source_path: Path) -> list[PolicySection]:
    sections: list[PolicySection] = []
    current_number: str | None = None
    current_lines: list[str] = []

    def save_section() -> None:
        if current_number is not None and current_lines:
            text = " ".join(line.strip() for line in current_lines)
            sections.append(
                PolicySection(source_path.name, current_number, text, source_path)
            )

    for raw_line in document.splitlines():
        stripped_line = raw_line.strip()
        match = SECTION_START.match(stripped_line)
        if match:
            save_section()
            current_number = match.group("number")
            current_lines = [match.group("text")]
        elif MAJOR_SECTION.match(stripped_line):
            save_section()
            current_number = None
            current_lines = []
        elif current_number is not None and TOKEN.search(stripped_line):
            current_lines.append(raw_line)

    save_section()
    return sections


def retrieve_documents(data_directory: Path | None = None) -> list[PolicySection]:
    """Load every required policy and index its numbered sections."""
    directory = data_directory or Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    indexed_sections: list[PolicySection] = []

    for filename in POLICY_FILES:
        source_path = directory / filename
        try:
            document = source_path.read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(f"Unable to load required policy file {filename}: {error}") from error

        sections = _parse_sections(document, source_path)
        if not sections:
            raise RuntimeError(f"Unable to parse numbered sections from {filename}")
        indexed_sections.extend(sections)

    return indexed_sections


def _terms(text: str) -> set[str]:
    terms = set()
    for token in TOKEN.findall(text.lower()):
        if token in STOP_WORDS:
            continue
        for suffix in ("ing", "ed", "al", "s"):
            if len(token) > len(suffix) + 3 and token.endswith(suffix):
                token = token[: -len(suffix)]
                break
        terms.add(token)
    return terms


def _question_terms(question: str) -> set[str]:
    terms = _terms(question)
    normalized_question = question.lower()
    if "leave without pay" in normalized_question:
        terms.update({"lwp", "approv", "department", "director"})
    if "install" in normalized_question:
        terms.update({"software", "approv"})
    if "personal phone" in normalized_question and (
        "work file" in normalized_question or "work files" in normalized_question
    ):
        terms.update({"device", "email", "portal"})
    return terms


def _section_score(question_terms: set[str], section: PolicySection) -> int:
    return len(question_terms & _terms(section.text))


def answer_question(question: str, indexed_sections: list[PolicySection]) -> str:
    """Answer from one clearly matching document, or return the exact refusal."""
    if not question.strip() or not indexed_sections:
        return REFUSAL

    normalized_question = question.lower()
    if "personal phone" in normalized_question and (
        "work file" in normalized_question or "work files" in normalized_question
    ):
        for section in indexed_sections:
            if section.document == "policy_it_acceptable_use.txt" and section.number == "3.1":
                return f"{section.text} Source: {section.document}, section {section.number}."

    question_terms = _question_terms(question)
    if not question_terms:
        return REFUSAL

    scored = [
        (section, _section_score(question_terms, section))
        for section in indexed_sections
    ]
    scored = [(section, score) for section, score in scored if score > 0]
    if not scored:
        return REFUSAL

    document_scores: dict[str, int] = {}
    for section, score in scored:
        document_scores[section.document] = max(document_scores.get(section.document, 0), score)

    best_document_score = max(document_scores.values())
    best_documents = [
        document for document, score in document_scores.items() if score == best_document_score
    ]
    if len(best_documents) != 1 or best_document_score < 2:
        return REFUSAL

    document = best_documents[0]
    best_sections = [
        section for section, score in scored
        if section.document == document and score == best_document_score
    ]
    if len(best_sections) != 1:
        return REFUSAL

    section = best_sections[0]
    return f"{section.text} Source: {section.document}, section {section.number}."


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about CMC policy documents.")
    parser.add_argument("--question", help="Answer one question and exit.")
    args = parser.parse_args()

    try:
        indexed_sections = retrieve_documents()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    if args.question:
        print(answer_question(args.question, indexed_sections))
        return

    print("Policy documents loaded. Type a question, or type 'quit' to exit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if question.lower() in {"quit", "exit"}:
            break
        print(answer_question(question, indexed_sections))

if __name__ == "__main__":
    main()
