"""UC-X — deterministic, single-source policy question answering CLI."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


POLICY_FILENAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

STOP_WORDS = {
    "a", "about", "all", "an", "and", "are", "at", "be", "can", "do",
    "does", "for", "from", "how", "i", "if", "in", "is", "it", "me",
    "my", "of", "on", "or", "the", "this", "to", "what", "when",
    "where", "which", "who", "with", "work", "company", "policy",
}

SYNONYMS = {
    "carry": {"carry-forward", "unused", "forfeited"},
    "forward": {"carry-forward", "unused", "forfeited"},
    "slack": {"software", "install"},
    "install": {"software", "approval"},
    "home": {"work-from-home", "wfh"},
    "office": {"equipment", "allowance"},
    "phone": {"personal", "device", "devices"},
    "file": {"data", "access", "store", "transmit"},
    "meal": {"meals", "da", "receipts"},
    "meals": {"meal", "da", "receipts"},
    "approv": {"approval", "requires"},
    "approval": {"approve", "requires"},
    "lwp": {"leave", "without", "pay"},
}

SECTION_RE = re.compile(
    r"(?ms)^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s+|^═{5,}|\Z)"
)


@dataclass(frozen=True)
class Section:
    document_name: str
    number: str
    text: str


def _normalise(text: str) -> str:
    text = text.lower().replace("work from home", "work-from-home")
    return re.sub(r"[^a-z0-9-]+", " ", text)


def _stem(term: str) -> str:
    """Apply tiny, conservative stemming sufficient for policy vocabulary."""
    if term.startswith("approv"):
        return "approv"
    for suffix in ("ing", "ed", "s"):
        if term.endswith(suffix) and len(term) > len(suffix) + 3:
            return term[: -len(suffix)]
    return term


def _terms(text: str, expand: bool = False) -> set[str]:
    normalised = _normalise(text)
    terms = {_stem(term) for term in normalised.split() if term not in STOP_WORDS}
    if "leave without pay" in normalised:
        terms.add("lwp")
    if expand:
        for term in tuple(terms):
            terms.update(_stem(value) for value in SYNONYMS.get(term, set()))
    return terms


def retrieve_documents(policy_dir: Path | None = None) -> list[Section]:
    """Load only the approved files and split them into numbered sections."""
    directory = policy_dir or Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    sections: list[Section] = []

    for filename in POLICY_FILENAMES:
        path = directory / filename
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Required policy document is unavailable: {filename}") from exc

        matches = list(SECTION_RE.finditer(content))
        if not matches:
            raise RuntimeError(f"No numbered sections found in required document: {filename}")
        for match in matches:
            section_text = re.sub(r"\s+", " ", match.group(2)).strip()
            sections.append(Section(filename, match.group(1), section_text))

    return sections


def _score(question_terms: set[str], section: Section) -> float:
    section_terms = _terms(section.text)
    overlap = question_terms & section_terms
    if not overlap:
        return 0.0
    # Coverage prevents a generic section with one common word from winning;
    # the small overlap bonus rewards sections matching several query concepts.
    score = len(overlap) / max(len(question_terms), 1) + 0.08 * len(overlap)
    # Approval is an intent-bearing term: prefer the section that names the
    # approver over a neighboring section that merely names the leave type.
    if "approv" in question_terms and "approv" in section_terms:
        score += 0.35
    return score


def _render(section: Section) -> str:
    answer = section.text[0].upper() + section.text[1:]
    return f"{answer}\n[Source: {section.document_name}, section {section.number}]"


def answer_question(question: str, sections: Iterable[Section]) -> str:
    """Return a supported single-section answer, otherwise refuse exactly."""
    if not question or not question.strip():
        return REFUSAL

    question_terms = _terms(question, expand=True)
    if not question_terms:
        return REFUSAL

    ranked = sorted(
        ((_score(question_terms, section), section) for section in sections),
        key=lambda item: item[0],
        reverse=True,
    )
    best_score, best = ranked[0] if ranked else (0.0, None)
    if best is None or best_score < 0.34:
        return REFUSAL

    # A near-tie across documents is ambiguous and could invite blending.
    for score, candidate in ranked[1:]:
        if candidate.document_name != best.document_name and score >= best_score * 0.92:
            return REFUSAL

    return _render(best)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask questions about CMC policy documents.")
    parser.add_argument("-q", "--question", help="answer one question and exit")
    parser.add_argument(
        "--policy-dir",
        type=Path,
        help="directory containing the three approved policy files",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        sections = retrieve_documents(args.policy_dir)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    if args.question is not None:
        print(answer_question(args.question, sections))
        return

    print("UC-X — Ask My Documents (type 'exit' or 'quit' to stop)")
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, sections))


if __name__ == "__main__":
    main()
