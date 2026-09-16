"""UC-X: source-constrained questions over the three policy documents."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DOCUMENT_NAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "for", "from", "how", "i",
    "in", "is", "it", "may", "my", "of", "on", "the", "to", "what",
    "when", "where", "who", "with", "work", "working", "use",
}


@dataclass(frozen=True)
class Section:
    document: str
    number: str
    title: str
    text: str


def retrieve_documents(documents_dir: Path) -> list[Section]:
    """Load all required files and index them by filename and section number."""
    sections: list[Section] = []
    for filename in DOCUMENT_NAMES:
        path = documents_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required policy file not found: {path}")
        raw = path.read_text(encoding="utf-8")
        matches = list(re.finditer(r"(?m)^(\d+\.\d+)\s+(.+)$", raw))
        if not matches:
            raise ValueError(f"Could not parse numbered sections in: {path}")
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
            text = " ".join(raw[match.start():end].split())
            sections.append(Section(filename, match.group(1), match.group(2).strip(), text))
    return sections


def _terms(value: str) -> set[str]:
    return {
        word for word in re.findall(r"[a-z0-9]+", value.lower())
        if word not in STOP_WORDS and len(word) > 2
    }


def answer_question(question: str, index: list[Section]) -> str:
    """Return a single-source answer with citations, or the exact refusal."""
    query_terms = _terms(question)
    if not query_terms:
        return REFUSAL

    scored: list[tuple[int, Section]] = []
    for section in index:
        section_terms = _terms(section.text)
        score = len(query_terms & section_terms)
        if score:
            scored.append((score, section))
    if not scored:
        return REFUSAL

    best_score = max(score for score, _ in scored)
    best = [section for score, section in scored if score == best_score]
    documents = {section.document for section in best}
    if len(documents) != 1:
        return REFUSAL

    # Include only the strongest sections from the one selected document.
    selected = [section for score, section in scored if score == best_score and section.document == next(iter(documents))]
    return "\n".join(
        f"{section.text} [Source: {section.document}, section {section.number}.]"
        for section in selected
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the available policy documents.")
    parser.add_argument(
        "--documents-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "policy-documents",
        help="Directory containing the three policy text files.",
    )
    args = parser.parse_args()

    try:
        index = retrieve_documents(args.documents_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print("Policy documents loaded. Ask a question, or type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, index))


if __name__ == "__main__":
    main()
