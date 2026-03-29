"""UC-X Ask My Documents CLI with strict single-source policy answering."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "the",
    "to",
    "we",
    "what",
    "when",
    "where",
    "who",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class Section:
    document_name: str
    section_number: str
    text: str
    tokens: Set[str]


def normalize_tokens(text: str) -> Set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 1 and w not in STOPWORDS}


def parse_sections(document_name: str, content: str) -> List[Section]:
    sections: List[Tuple[str, List[str]]] = []
    current_number = ""
    current_lines: List[str] = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            if current_number:
                sections.append((current_number, current_lines))
            current_number = match.group(1)
            current_lines = [match.group(2).strip()]
            continue

        if current_number and line.strip():
            stripped = line.strip()
            if re.match(r"^[═\-\s]+$", stripped):
                continue
            if re.match(r"^\d+\.\s+[A-Z]", stripped):
                continue
            current_lines.append(stripped)

    if current_number:
        sections.append((current_number, current_lines))

    parsed: List[Section] = []
    for number, lines in sections:
        text = " ".join(lines).strip()
        parsed.append(
            Section(
                document_name=document_name,
                section_number=number,
                text=text,
                tokens=normalize_tokens(text),
            )
        )

    return parsed


def retrieve_documents(policy_dir: Path) -> Dict[str, Dict[str, Section]]:
    missing = [name for name in DOCUMENT_FILES if not (policy_dir / name).exists()]
    if missing:
        missing_joined = ", ".join(missing)
        raise FileNotFoundError(
            "Missing required policy files: "
            f"{missing_joined}. Cannot answer policy questions."
        )

    index: Dict[str, Dict[str, Section]] = {}
    for filename in DOCUMENT_FILES:
        content = (policy_dir / filename).read_text(encoding="utf-8")
        sections = parse_sections(filename, content)
        index[filename] = {section.section_number: section for section in sections}
    return index


def choose_best_single_source(
    question_tokens: Set[str],
    all_sections: Iterable[Section],
) -> Tuple[str, List[Section]]:
    if not question_tokens:
        return "", []

    scored: List[Tuple[int, Section]] = []
    for section in all_sections:
        overlap = question_tokens.intersection(section.tokens)
        if overlap:
            scored.append((len(overlap), section))

    if not scored:
        return "", []

    scored.sort(key=lambda item: item[0], reverse=True)
    top_score = scored[0][0]

    # Keep candidate sections close to the top score to detect ambiguity.
    threshold = max(1, top_score - 1)
    candidates = [section for score, section in scored if score >= threshold]

    docs = {section.document_name for section in candidates}
    if len(docs) != 1:
        return "", []

    doc_name = candidates[0].document_name
    same_doc_ranked = [
        section
        for score, section in scored
        if section.document_name == doc_name and score >= threshold
    ]
    return doc_name, same_doc_ranked[:2]


def format_answer(selected_sections: List[Section]) -> str:
    if not selected_sections:
        return REFUSAL_TEMPLATE

    lines = []
    for section in selected_sections:
        lines.append(
            f"{section.text} ({section.document_name}, section {section.section_number})"
        )
    return "\n".join(lines)


def answer_question(question: str, index: Dict[str, Dict[str, Section]]) -> str:
    tokens = normalize_tokens(question)
    flat_sections = [section for sections in index.values() for section in sections.values()]

    _doc_name, selected_sections = choose_best_single_source(tokens, flat_sections)
    if not selected_sections:
        return REFUSAL_TEMPLATE

    return format_answer(selected_sections)


def run_cli(index: Dict[str, Dict[str, Section]], initial_question: str | None) -> int:
    if initial_question:
        print(answer_question(initial_question, index))
        return 0

    print("UC-X Ask My Documents")
    print("Type a question, or type 'exit' to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            print()
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            return 0

        print(answer_question(question, index))


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy Q&A CLI")
    parser.add_argument(
        "--question",
        help="Optional one-shot question. If omitted, interactive mode starts.",
    )
    parser.add_argument(
        "--policy-dir",
        default=str((Path(__file__).resolve().parent / ".." / "data" / "policy-documents").resolve()),
        help="Directory containing policy documents.",
    )
    args = parser.parse_args()

    try:
        index = retrieve_documents(Path(args.policy_dir))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    sys.exit(run_cli(index, args.question))


if __name__ == "__main__":
    main()
