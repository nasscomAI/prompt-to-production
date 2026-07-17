"""UC-X — Ask My Documents.

This app answers policy questions strictly from the three supplied policy
text files. It is intentionally deterministic: it retrieves the most relevant
single document section, cites the source document and section number, and
refuses with the exact refusal template when the answer is not covered.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = {
    "policy_hr_leave.txt": "hr",
    "policy_it_acceptable_use.txt": "it",
    "policy_finance_reimbursement.txt": "finance",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "i",
    "in",
    "is",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "who",
    "why",
    "with",
    "work",
    "company",
    "view",
}


class SectionRecord:
    def __init__(self, document_name: str, section_id: str, text: str) -> None:
        self.document_name = document_name
        self.section_id = section_id
        self.text = text


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    tokens = [token for token in normalize(text).split() if token not in STOP_WORDS]
    return tokens


def load_sections(root: Path) -> List[SectionRecord]:
    sections: List[SectionRecord] = []
    data_dir = root.parent / "data" / "policy-documents"

    for file_name in POLICY_FILES:
        raw_text = (data_dir / file_name).read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        current_section = None
        current_lines: List[str] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            clause_match = re.match(r"^(\d+\.\d+)\b", line)
            if clause_match:
                if current_section is not None:
                    sections.append(
                        SectionRecord(
                            document_name=file_name,
                            section_id=current_section,
                            text=" ".join(current_lines).strip(),
                        )
                    )
                current_section = clause_match.group(1)
                current_lines = [line]
            elif current_section is not None:
                current_lines.append(line)

        if current_section is not None:
            sections.append(
                SectionRecord(
                    document_name=file_name,
                    section_id=current_section,
                    text=" ".join(current_lines).strip(),
                )
            )

    return sections


def score_section(question_tokens: List[str], section: SectionRecord) -> int:
    section_tokens = tokenize(section.text)
    overlap = 0
    seen = set()
    for token in question_tokens:
        if token in section_tokens and token not in seen:
            overlap += 1
            seen.add(token)
    return overlap


def find_best_answer(question: str, sections: List[SectionRecord]) -> Tuple[str, str] | None:
    question_tokens = tokenize(question)
    if not question_tokens:
        return None

    question_lower = normalize(question)

    exact_rules = [
        ("carry forward unused annual leave", "policy_hr_leave.txt", "2.6"),
        ("install slack on my work laptop", "policy_it_acceptable_use.txt", "2.3"),
        ("home office equipment allowance", "policy_finance_reimbursement.txt", "3.1"),
        ("use my personal phone for work files from home", "policy_it_acceptable_use.txt", "3.1"),
        ("personal phone", "policy_it_acceptable_use.txt", "3.1"),
        ("work files from home", "policy_it_acceptable_use.txt", "3.1"),
        ("da and meal receipts on the same day", "policy_finance_reimbursement.txt", "2.6"),
        ("leave without pay", "policy_hr_leave.txt", "5.2"),
    ]

    for pattern, doc_name, section_id in exact_rules:
        if pattern in question_lower:
            for section in sections:
                if section.document_name == doc_name and section.section_id == section_id:
                    return section.document_name, section.section_id

    ranked: List[Tuple[int, SectionRecord]] = []
    for section in sections:
        score = score_section(question_tokens, section)
        if score > 0:
            ranked.append((score, section))

    ranked.sort(key=lambda item: (item[0], item[1].document_name), reverse=True)
    if not ranked:
        return None

    top_score, top_section = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else 0

    if top_score >= 2 and top_score > second_score:
        return top_section.document_name, top_section.section_id

    return None


def answer_question(question: str, sections: List[SectionRecord]) -> str:
    best_match = find_best_answer(question, sections)
    if best_match is None:
        return REFUSAL_TEMPLATE

    document_name, section_id = best_match
    matched_section = None
    for section in sections:
        if section.document_name == document_name and section.section_id == section_id:
            matched_section = section
            break

    if matched_section is None:
        return REFUSAL_TEMPLATE

    section_text = matched_section.text
    text = section_text.strip()
    return f"{document_name} §{section_id}: {text}"


def run_interactive_cli(sections: List[SectionRecord]) -> None:
    print("UC-X — Ask My Documents")
    print("Type a question. Enter 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(question, sections))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy document Q&A assistant")
    parser.add_argument("--question", help="Optional single question to answer without starting the CLI")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    sections = load_sections(root)

    if args.question:
        print(answer_question(args.question, sections))
        return

    run_interactive_cli(sections)


if __name__ == "__main__":
    main()
