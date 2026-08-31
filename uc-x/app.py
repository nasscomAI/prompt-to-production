#!/usr/bin/env python3
"""
UC-X — Ask My Documents
Interactive CLI for policy document Q&A with strict single-source enforcement.
"""

import os
import re
import sys
from typing import Dict, List, Tuple


POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
]


def parse_sections(content: str) -> Dict[str, str]:
    """Parse document into sections keyed by section number."""
    sections = {}
    current_section = None
    current_content = []

    lines = content.split("\n")
    for line in lines:
        match = re.match(r"^(\d+\.\d+)\s+(.+)$", line.strip())
        if match:
            if current_section is not None:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = match.group(1)
            current_content = [match.group(2)]
        elif current_section is not None:
            current_content.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    """Load all three policy files and index by document name and section number."""
    index = {}
    for filename in POLICY_FILES:
        path = os.path.join(POLICY_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        index[filename] = parse_sections(content)
    return index


def search_sections(index: Dict[str, Dict[str, str]], question: str) -> List[Tuple[str, str, str]]:
    """Search all sections for relevance to question. Returns (doc, section, text)."""
    question_lower = question.lower()
    question_words = set(re.findall(r"\b\w+\b", question_lower))
    question_words = {w for w in question_words if len(w) > 3}

    results = []
    for doc_name, sections in index.items():
        for section_num, section_text in sections.items():
            text_lower = section_text.lower()
            text_words = set(re.findall(r"\b\w+\b", text_lower))
            overlap = question_words & text_words
            if overlap:
                score = len(overlap)
                results.append((score, doc_name, section_num, section_text))

    results.sort(reverse=True, key=lambda x: x[0])
    return [(doc, sec, text) for _, doc, sec, text in results]


def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> str:
    """Return single-source answer with citation OR refusal template."""
    matches = search_sections(index, question)

    if not matches:
        return REFUSAL_TEMPLATE

    relevant_docs = set(doc for doc, _, _ in matches)
    if len(relevant_docs) > 1:
        return REFUSAL_TEMPLATE

    doc_name = matches[0][0]
    section_num = matches[0][1]
    section_text = matches[0][2]

    answer = f"{section_text} (source: {doc_name} section {section_num})"

    for phrase in HEDGING_PHRASES:
        if phrase in answer.lower():
            return REFUSAL_TEMPLATE

    return answer


def main():
    print("UC-X Policy Q&A — Type 'exit' to quit")
    print("=" * 50)

    index = retrieve_documents()

    while True:
        try:
            question = input("\nQuestion: ").strip()
            if not question:
                continue
            if question.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            answer = answer_question(question, index)
            print(f"\nAnswer: {answer}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()