"""
UC-X app.py

Interactive policy QA CLI constrained to three policy documents.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


POLICY_FILES = {
    "policy_hr_leave.txt": Path("../data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": Path("../data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": Path("../data/policy-documents/policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance.\n"
    "The relevant team should be determined based on the below templates:\n"
    "Questions about leave, obboarding, resignation, offboarding - HR team\n"
    "Questions about IT assets, access, software installation - IT team\n"
    "Questions about reibursements, payroll, benefits - Finance team"
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "can",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "who",
    "with",
    "work",
    "working",
}


@dataclass(frozen=True)
class Section:
    document_name: str
    section_number: str
    heading: str
    text: str
    line_items: List[str]


def normalize_tokens(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def extract_section_blocks(raw_text: str) -> List[Tuple[str, str]]:
    lines = raw_text.splitlines()
    section_header_pattern = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
    line_item_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    blocks: List[Tuple[str, str]] = []
    current_section = ""
    current_body: List[str] = []

    for line in lines:
        stripped = line.strip()
        sec_match = section_header_pattern.match(stripped)
        if sec_match:
            if current_section and current_body:
                blocks.append((current_section, "\n".join(current_body).strip()))
            current_section = f"{sec_match.group(1)}. {sec_match.group(2)}"
            current_body = []
            continue
        if line_item_pattern.match(stripped):
            current_body.append(stripped)

    if current_section and current_body:
        blocks.append((current_section, "\n".join(current_body).strip()))

    return blocks


def retrieve_documents() -> Dict[str, List[Section]]:
    index: Dict[str, List[Section]] = {}
    missing_files: List[str] = []

    for doc_name, path in POLICY_FILES.items():
        if not path.exists():
            missing_files.append(doc_name)
            continue

        raw_text = path.read_text(encoding="utf-8")
        section_blocks = extract_section_blocks(raw_text)
        if not section_blocks:
            raise ValueError(f"Could not parse sections in {doc_name}")

        sections: List[Section] = []
        for header, block_text in section_blocks:
            sec_match = re.match(r"^(\d+)\.\s+(.+)$", header)
            if not sec_match:
                continue
            major_number, heading = sec_match.groups()

            line_items: List[str] = []
            section_number = major_number
            for line in block_text.splitlines():
                item_match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
                if item_match:
                    section_number = item_match.group(1)
                    line_items.append(f"{item_match.group(1)} {item_match.group(2)}")

            sections.append(
                Section(
                    document_name=doc_name,
                    section_number=section_number,
                    heading=heading,
                    text=block_text,
                    line_items=line_items,
                )
            )
        index[doc_name] = sections

    if missing_files:
        missing = ", ".join(missing_files)
        raise FileNotFoundError(f"Missing required policy files: {missing}")
    return index


def section_score(question_tokens: List[str], section: Section) -> int:
    section_tokens = set(normalize_tokens(f"{section.heading} {section.text}"))
    overlap = sum(1 for token in question_tokens if token in section_tokens)
    phrase_bonus = 0
    q_lower = " ".join(question_tokens)
    if "work from home" in q_lower and "work-from-home" in section.text.lower():
        phrase_bonus += 2
    if "personal phone" in q_lower and "personal devices" in section.text.lower():
        phrase_bonus += 2
    return overlap + phrase_bonus


def best_line_item(question_tokens: List[str], section: Section) -> str:
    if not section.line_items:
        return section.text.splitlines()[0].strip()
    approval_query = any(t.startswith("approv") for t in question_tokens)
    best = ""
    best_score = -1
    for item in section.line_items:
        item_tokens = set(normalize_tokens(item))
        score = sum(1 for token in question_tokens if token in item_tokens)
        if approval_query and any(t.startswith("approv") for t in item_tokens):
            score += 6
        if score > best_score:
            best_score = score
            best = item
    return best if best else section.line_items[0]


def format_answer(line_item: str, document_name: str, section_number: str) -> str:
    cleaned = re.sub(r"^\d+\.\d+\s+", "", line_item).strip()
    return f"{cleaned}\nSource: {document_name} section {section_number}"


def answer_question(question: str, index: Dict[str, List[Section]]) -> str:
    question_tokens = normalize_tokens(question)
    if not question_tokens:
        return REFUSAL_TEMPLATE

    scored_sections: List[Tuple[int, Section]] = []
    for sections in index.values():
        for section in sections:
            score = section_score(question_tokens, section)
            if score > 0:
                scored_sections.append((score, section))

    if not scored_sections:
        return REFUSAL_TEMPLATE

    scored_sections.sort(key=lambda x: x[0], reverse=True)
    top_score, top_section = scored_sections[0]
    competing_docs = {
        s.document_name for score, s in scored_sections if score == top_score
    }
    if len(competing_docs) > 1:
        return REFUSAL_TEMPLATE

    # Refuse when top two sections from different documents are too close.
    if len(scored_sections) > 1:
        second_score, second_section = scored_sections[1]
        if (
            second_section.document_name != top_section.document_name
            and top_score - second_score <= 1
        ):
            return REFUSAL_TEMPLATE

    best_item = best_line_item(question_tokens, top_section)
    citation_number_match = re.match(r"^(\d+\.\d+)\s+", best_item)
    citation_number = (
        citation_number_match.group(1)
        if citation_number_match
        else top_section.section_number
    )
    return format_answer(best_item, top_section.document_name, citation_number)


def run_cli() -> None:
    index = retrieve_documents()
    print("UC-X Ask My Documents CLI")
    print("Type your question and press Enter. Type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, index))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy QA CLI")
    parser.add_argument(
        "--question",
        type=str,
        help="Optional single question mode (prints one answer and exits).",
    )
    args = parser.parse_args()

    index = retrieve_documents()
    if args.question:
        print(answer_question(args.question, index))
        return
    run_cli()


if __name__ == "__main__":
    main()
