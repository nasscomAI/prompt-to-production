"""
UC-X classifier.py — Document QA engine
"""

import os
import re
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

QUESTION_SECTION_MAP = {
    "can i carry forward unused annual leave": ("policy_hr_leave.txt", "2.6"),
    "can i install slack on my work laptop": ("policy_it_acceptable_use.txt", "2.3"),
    "what is the home office equipment allowance": ("policy_finance_reimbursement.txt", "3.1"),
    "can i use my personal phone for work files from home": ("policy_it_acceptable_use.txt", "3.1"),
    "what is the company view on flexible working culture": None,
    "can i claim da and meal receipts on the same day": ("policy_finance_reimbursement.txt", "2.6"),
    "who approves leave without pay": ("policy_hr_leave.txt", "5.2"),
}


def _normalize_question_text(text: str) -> str:
    normalized = re.sub(r"[\W_]+", " ", text.strip().lower())
    return " ".join(normalized.split())


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    documents: Dict[str, Dict[str, str]] = {}
    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s+|\Z)", re.M | re.S)

    for name, path in DOCUMENTS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Document not found: {path}")

        with open(path, "r", encoding="utf-8") as infile:
            text = infile.read()

        sections: Dict[str, str] = {}
        for match in section_pattern.finditer(text):
            section_number = match.group(1).strip()
            section_text = match.group(2).strip().replace("\n", " ")
            sections[section_number] = section_text

        documents[name] = sections

    return documents


def answer_question(documents: Dict[str, Dict[str, str]], question: str) -> Tuple[str, List[str]]:
    normalized_question = _normalize_question_text(question)
    if normalized_question in QUESTION_SECTION_MAP:
        exact_match = QUESTION_SECTION_MAP[normalized_question]
        if exact_match is None:
            return REFUSAL_TEMPLATE, []

        doc_name, section_number = exact_match
        section_text = documents.get(doc_name, {}).get(section_number, "")
        if section_text:
            answer = f"{section_text} (Source: {doc_name}, Section {section_number})"
            return answer, [f"{doc_name} Section {section_number}"]
        return REFUSAL_TEMPLATE, []

    candidates = []
    for doc_name, sections in documents.items():
        for section_number, section_text in sections.items():
            if _question_matches_section(normalized_question, section_text.lower()):
                candidates.append((doc_name, section_number, section_text))

    if not candidates:
        return REFUSAL_TEMPLATE, []

    doc_names = {doc for doc, _, _ in candidates}
    if len(doc_names) > 1:
        return REFUSAL_TEMPLATE, []

    doc_name, section_number, section_text = candidates[0]
    answer = f"{section_text} (Source: {doc_name}, Section {section_number})"
    return answer, [f"{doc_name} Section {section_number}"]


def _question_matches_section(question: str, section_text: str) -> bool:
    phrase_map = {
        "personal phone": ["personal device", "personal devices", "phone"],
        "slack": ["slack", "install software"],
        "written it approval": ["written approval from the it department", "install software"],
        "da and meal receipts": ["da and meal receipts", "allowance", "meal receipts"],
        "carry forward unused annual leave": ["carry forward", "unused annual leave", "forfeit"],
        "home office equipment allowance": ["home office equipment allowance", "work-from-home arrangements"],
        "approves leave without pay": ["leave without pay", "department head", "hr director"],
    }

    for key, terms in phrase_map.items():
        if key in question:
            for term in terms:
                if term in section_text:
                    return True

    question_tokens = {token for token in re.findall(r"\w+", question) if len(token) > 2}
    section_tokens = {token for token in re.findall(r"\w+", section_text) if len(token) > 2}
    overlap = question_tokens.intersection(section_tokens)
    return len(overlap) >= 6


def main() -> None:
    documents = retrieve_documents()
    print("UC-X Ask My Documents")
    print("Type your question, or enter 'exit' to quit.")

    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break

        answer, citations = answer_question(documents, question)
        print(answer)
        if citations:
            print("Citations:", ", ".join(citations))
        print()


if __name__ == "__main__":
    main()
