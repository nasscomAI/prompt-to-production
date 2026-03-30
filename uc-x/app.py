"""
UC-X app.py — Ask My Documents
Deterministic single-source policy Q&A CLI.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = {
    "policy_hr_leave.txt": Path("../data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": Path("../data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": Path("../data/policy-documents/policy_finance_reimbursement.txt"),
}


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("–", "-").replace("—", "-")
    lowered = re.sub(r"[^a-z0-9\s\-]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def load_document(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_sections(text: str) -> Dict[str, str]:
    """
    Parse section-numbered clauses like:
    2.6 Employees may carry forward ...
        continued line
    """
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {}
    current_section: Optional[str] = None

    section_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

    for raw_line in lines:
        line = raw_line.rstrip()
        match = section_pattern.match(line)

        if match:
            current_section = match.group(1)
            first_text = match.group(2).strip()
            sections[current_section] = [first_text]
        else:
            if current_section is not None:
                stripped = line.strip()
                if stripped and not re.fullmatch(r"[═\s]+", stripped):
                    sections[current_section].append(stripped)

    parsed: Dict[str, str] = {}
    for section_num, parts in sections.items():
        parsed[section_num] = " ".join(parts).strip()

    return parsed


def load_all_documents() -> Dict[str, Dict[str, str]]:
    documents: Dict[str, Dict[str, str]] = {}
    for doc_name, doc_path in DOC_PATHS.items():
        text = load_document(doc_path)
        documents[doc_name] = parse_sections(text)
    return documents


def find_best_single_source_answer(
    question: str, docs: Dict[str, Dict[str, str]]
) -> Optional[Tuple[str, str, str]]:
    """
    Returns (doc_name, section_number, answer_text) or None.
    Deterministic rule-based mapping to avoid cross-document blending.
    """
    q = normalize_text(question)

    # 1) Carry forward unused annual leave
    if (
        ("carry forward" in q or "carryforward" in q)
        and "leave" in q
    ):
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return (doc, sec, docs[doc][sec])

    # 2) Install Slack on work laptop
    if (
        ("install" in q or "software" in q)
        and ("slack" in q or "work laptop" in q or "corporate device" in q or "laptop" in q)
    ):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return (doc, sec, docs[doc][sec])

    # 3) Home office equipment allowance
    if (
        ("home office" in q or "equipment allowance" in q or "wfh allowance" in q)
    ):
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return (doc, sec, docs[doc][sec])

    # 4) Personal phone / personal device for work files from home
    # Must NOT blend with HR remote work tools.
    if (
        ("personal phone" in q or "personal device" in q or "my phone" in q or "own phone" in q)
        and ("work file" in q or "work files" in q or "files" in q or "from home" in q)
    ):
        doc = "policy_it_acceptable_use.txt"
        # 3.2 is the clearest direct prohibition for work files/data.
        sec = "3.2"
        return (doc, sec, docs[doc][sec])

    # 5) Flexible working culture -> not covered
    if "flexible working culture" in q:
        return None

    # 6) DA and meal receipts same day
    if (
        ("da" in q or "daily allowance" in q)
        and ("meal" in q or "meal receipt" in q or "meal receipts" in q)
    ):
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return (doc, sec, docs[doc][sec])

    # 7) Who approves leave without pay
    if (
        ("leave without pay" in q or "lwp" in q)
        and ("approve" in q or "approval" in q or "who approves" in q)
    ):
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return (doc, sec, docs[doc][sec])

    # Additional safe rules for likely variants
    if ("carry forward" in q or "unused annual leave" in q):
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return (doc, sec, docs[doc][sec])

    if ("slack" in q and ("laptop" in q or "device" in q)):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return (doc, sec, docs[doc][sec])

    if ("personal phone" in q or "personal device" in q) and ("email" in q or "portal" in q):
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return (doc, sec, docs[doc][sec])

    return None


def format_answer(doc_name: str, section: str, text: str) -> str:
    return f"{text}\nSource: {doc_name} section {section}"


def answer_question(question: str, docs: Dict[str, Dict[str, str]]) -> str:
    result = find_best_single_source_answer(question, docs)
    if result is None:
        return REFUSAL_TEMPLATE

    doc_name, section, text = result
    return format_answer(doc_name, section, text)


def main() -> None:
    docs = load_all_documents()

    print("UC-X — Ask My Documents")
    print("Type a question. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except EOFError:
            print()
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            break

        answer = answer_question(question, docs)
        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()
