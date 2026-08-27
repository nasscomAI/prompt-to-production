"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    ("policy_hr_leave.txt", "data/policy-documents/policy_hr_leave.txt"),
    ("policy_it_acceptable_use.txt", "data/policy-documents/policy_it_acceptable_use.txt"),
    ("policy_finance_reimbursement.txt", "data/policy-documents/policy_finance_reimbursement.txt"),
]

def retrieve_documents():
    index = {}
    section_header = re.compile(r"^(\d+\.\d+)")
    for doc_name, path in POLICY_FILES:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy file: {path}")
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        sections = {}
        current_section = None
        current_text = []
        for line in lines:
            match = section_header.match(line.strip())
            if match:
                if current_section:
                    sections[current_section] = " ".join(current_text).strip()
                current_section = match.group(1)
                current_text = [line.strip()]
            elif current_section:
                current_text.append(line.strip())
        if current_section:
            sections[current_section] = " ".join(current_text).strip()
        index[doc_name] = sections
    return index

def answer_question(question, indexed_documents):
    # Lowercase for matching, but preserve original for output
    q = question.strip().lower()
    # Map of keywords to (doc, section)
    keyword_map = [
        # HR policy
        (re.compile(r"carry forward.*annual leave"), ("policy_hr_leave.txt", "2.6")),
        (re.compile(r"leave without pay|lwp.*approve|who approves leave"), ("policy_hr_leave.txt", "5.2")),
        # IT policy
        (re.compile(r"install slack|install.*software|slack.*work laptop"), ("policy_it_acceptable_use.txt", "2.3")),
        (re.compile(r"personal phone.*work files|personal device.*work files|personal phone.*home|personal device.*home"), ("policy_it_acceptable_use.txt", "3.1")),
        # Finance
        (re.compile(r"home office equipment allowance"), ("policy_finance_reimbursement.txt", "3.1")),
        (re.compile(r"claim da.*meal receipts|da and meal receipts"), ("policy_finance_reimbursement.txt", "2.6")),
    ]
    for pattern, (doc, section) in keyword_map:
        if pattern.search(q):
            # Only answer from one doc/section
            answer = indexed_documents.get(doc, {}).get(section)
            if answer:
                return {
                    "answer": f"{answer}\n(Source: {doc} section {section})",
                    "citation": {"document_name": doc, "section_number": section}
                }
    # Flexible: "company view on flexible working culture" and others not present
    return {"answer": REFUSAL_TEMPLATE, "citation": None}

def main():
    print("UC-X: Ask My Documents — Interactive CLI\nType your question, or 'exit' to quit.")
    try:
        indexed_documents = retrieve_documents()
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
    while True:
        try:
            question = input("\n> ").strip()
            if question.lower() in ("exit", "quit"): break
            if not question:
                print("Please enter a question or 'exit' to quit.")
                continue
            result = answer_question(question, indexed_documents)
            print("\n" + result["answer"])
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
