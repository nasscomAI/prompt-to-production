"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant team for guidance."
)


# Load documents
def retrieve_documents():
    base_path = "../data/policy-documents"

    files = {
        "hr": "policy_hr_leave.txt",
        "it": "policy_it_acceptable_use.txt",
        "finance": "policy_finance_reimbursement.txt",
    }

    docs = {}

    for key, filename in files.items():
        path = os.path.join(base_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs[key] = f.read().lower()
        except FileNotFoundError:
            docs[key] = ""

    return docs


# Helper: extract section text
def find_section(doc_text, section_number):
    pattern = rf"(section\s*{section_number}.*?)(?=section\s*\d+|$)"
    match = re.search(pattern, doc_text, re.DOTALL)
    return match.group(1).strip() if match else None


# Answer logic (STRICT — no blending)
def answer_question(question, docs):
    q = question.lower()

    # ---------------- HR ----------------
    if "carry forward" in q or "unused leave" in q:
        section = find_section(docs["hr"], "2.6")
        if section:
            return f"HR Policy (Section 2.6): {section}"
        return REFUSAL

    if "leave without pay" in q:
        section = find_section(docs["hr"], "5.2")
        if section:
            return f"HR Policy (Section 5.2): {section}"
        return REFUSAL

    # ---------------- IT ----------------
    if "slack" in q:
        section = find_section(docs["it"], "2.3")
        if section:
            return f"IT Policy (Section 2.3): {section}"
        return REFUSAL

    if "personal phone" in q or "personal device" in q:
        section = find_section(docs["it"], "3.1")
        if section:
            return f"IT Policy (Section 3.1): {section}"
        return REFUSAL

    # ---------------- FINANCE ----------------
    if "home office" in q or "equipment allowance" in q:
        section = find_section(docs["finance"], "3.1")
        if section:
            return f"Finance Policy (Section 3.1): {section}"
        return REFUSAL

    if "da" in q and "meal" in q:
        section = find_section(docs["finance"], "2.6")
        if section:
            return f"Finance Policy (Section 2.6): {section}"
        return REFUSAL

    # ---------------- DEFAULT REFUSAL ----------------
    return REFUSAL


# CLI loop
def main():
    docs = retrieve_documents()

    print("Ask your question (type 'exit' to quit):")

    while True:
        q = input("> ")

        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()