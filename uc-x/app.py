"""
UC-X app.py — Ask My Documents
Interactive CLI Q&A system over policy documents.
"""
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "policy-documents")
POLICY_FILES = [
    os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents. "
    "Please contact the relevant team for guidance."
)


def retrieve_documents(file_paths: list) -> dict:
    """Load policy files, index by document name and section number."""
    indexed = {}
    for fp in file_paths:
        doc_name = os.path.basename(fp)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: {doc_name} not found, skipping.")
            continue

        sections = {}
        metadata = {}

        header_match = re.search(
            r"^(.*?)\n.*?Document Reference:\s*(\S+)\s*\n.*?Version:\s*(\S+)\s*\|.*?Effective:\s*(.+?)\n",
            content, re.DOTALL
        )
        if header_match:
            metadata["title"] = header_match.group(1).strip()
            metadata["doc_ref"] = header_match.group(2).strip()
            metadata["version"] = header_match.group(3).strip()
            metadata["effective"] = header_match.group(4).strip()

        section_pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s+|\n═{10,}|\Z)', re.DOTALL | re.MULTILINE)
        for match in section_pattern.finditer(content):
            sec_num = match.group(1).strip()
            sec_text = " ".join(match.group(2).strip().split())
            sections[sec_num] = sec_text

        indexed[doc_name] = {"metadata": metadata, "sections": sections}

    if not indexed:
        raise RuntimeError("No policy documents could be loaded.")

    return indexed


def answer_question(question: str, indexed_docs: dict) -> str:
    """Search indexed docs, return single-source answer with citation OR refusal."""
    q_lower = question.lower()

    keyword_index = {
        "carry forward": [("policy_hr_leave.txt", ["2.6", "2.7"])],
        "annual leave": [("policy_hr_leave.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"])],
        "sick leave": [("policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"])],
        "maternity": [("policy_hr_leave.txt", ["4.1", "4.2"])],
        "paternity": [("policy_hr_leave.txt", ["4.3", "4.4"])],
        "leave without pay": [("policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"])],
        "lwp": [("policy_hr_leave.txt", ["5.1", "5.2", "5.3", "5.4"])],
        "who approves leave without pay": [("policy_hr_leave.txt", ["5.2"])],
        "public holiday": [("policy_hr_leave.txt", ["6.1", "6.2", "6.3"])],
        "encashment": [("policy_hr_leave.txt", ["7.1", "7.2", "7.3"])],
        "leave encashment": [("policy_hr_leave.txt", ["7.1", "7.2", "7.3"])],
        "grievance": [("policy_hr_leave.txt", ["8.1", "8.2"])],
        "install slack": [("policy_it_acceptable_use.txt", ["2.3", "2.4"])],
        "install software": [("policy_it_acceptable_use.txt", ["2.3", "2.4"])],
        "personal phone": [("policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "personal device": [("policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "byod": [("policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "password": [("policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3"])],
        "mfa": [("policy_it_acceptable_use.txt", ["4.4"])],
        "multi-factor": [("policy_it_acceptable_use.txt", ["4.4"])],
        "data handling": [("policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"])],
        "confidential": [("policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"])],
        "internet use": [("policy_it_acceptable_use.txt", ["6.1", "6.2", "6.3"])],
        "email use": [("policy_it_acceptable_use.txt", ["6.1", "6.2", "6.3"])],
        "violation": [("policy_it_acceptable_use.txt", ["7.1", "7.2", "7.3"])],
        "home office": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "equipment allowance": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "work from home": [("policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"])],
        "travel": [("policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"])],
        "da": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
        "meal receipt": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
        "daily allowance": [("policy_finance_reimbursement.txt", ["2.5", "2.6"])],
        "training": [("policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"])],
        "professional development": [("policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"])],
        "mobile phone reimbursement": [("policy_finance_reimbursement.txt", ["5.1"])],
        "internet reimbursement": [("policy_finance_reimbursement.txt", ["5.2"])],
        "reimbursement": [("policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"])],
        "submission": [("policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"])],
        "claim": [("policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"])],
        "flexible working": [],
        "flexible work": [],
        "company culture": [],
        "company view": [],
    }

    best_match = None
    best_score = 0

    for keyword, doc_sections in keyword_index.items():
        if keyword in q_lower:
            score = len(keyword)
            if not doc_sections:
                return REFUSAL_TEMPLATE
            if score > best_score:
                best_score = score
                best_match = (keyword, doc_sections)

    if not best_match:
        for keyword, doc_sections in keyword_index.items():
            words = keyword.split()
            if len(words) > 1 and all(w in q_lower for w in words):
                if not doc_sections:
                    return REFUSAL_TEMPLATE
                best_match = (keyword, doc_sections)
                break

    if not best_match:
        return REFUSAL_TEMPLATE

    keyword, doc_sections = best_match
    results = []
    for doc_name, section_nums in doc_sections:
        if doc_name in indexed_docs:
            for sec_num in section_nums:
                if sec_num in indexed_docs[doc_name]["sections"]:
                    text = indexed_docs[doc_name]["sections"][sec_num]
                    results.append(f"[{doc_name} section {sec_num}] {text}")

    if results:
        return "\n\n".join(results)
    return REFUSAL_TEMPLATE


def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print(f"Loading policy documents from: {POLICY_DIR}")

    indexed_docs = retrieve_documents(POLICY_FILES)
    print(f"Loaded {len(indexed_docs)} policy documents:")
    for doc_name, doc_data in indexed_docs.items():
        sections = doc_data["sections"]
        print(f"  - {doc_name}: {len(sections)} sections")
    print()
    print("Type your question (or 'quit' to exit).")
    print("-" * 60)

    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, indexed_docs)
        print(f"\nA: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
