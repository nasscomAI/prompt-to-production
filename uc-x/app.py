"""
UC-X Policy Q&A System
Interactive CLI for asking questions about company policy documents.
"""

import argparse
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def retrieve_documents():

    files = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
    }

    docs = {}

    for name, path in files.items():
        sections = {}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        for num, text in matches:
            sections[num] = text.strip()

        docs[name] = sections

    return docs


def answer_question(docs, question):

    q = question.lower()

    # HR Leave checks
    if "carry forward" in q or "unused leave" in q:
        text = docs["policy_hr_leave.txt"].get("2.6")
        if text:
            return f"{text}\n(Source: policy_hr_leave.txt section 2.6)"

    if "leave without pay" in q or "lwp" in q:
        text = docs["policy_hr_leave.txt"].get("5.2")
        if text:
            return f"{text}\n(Source: policy_hr_leave.txt section 5.2)"

    # IT policy checks
    if "install slack" in q or "work laptop" in q:
        text = docs["policy_it_acceptable_use.txt"].get("2.3")
        if text:
            return f"{text}\n(Source: policy_it_acceptable_use.txt section 2.3)"

    if "personal phone" in q:
        text = docs["policy_it_acceptable_use.txt"].get("3.1")
        if text:
            return f"{text}\n(Source: policy_it_acceptable_use.txt section 3.1)"

    # Finance checks
    if "home office equipment" in q or "allowance" in q:
        text = docs["policy_finance_reimbursement.txt"].get("3.1")
        if text:
            return f"{text}\n(Source: policy_finance_reimbursement.txt section 3.1)"

    if "da and meal" in q or "meal receipts" in q:
        text = docs["policy_finance_reimbursement.txt"].get("2.6")
        if text:
            return f"{text}\n(Source: policy_finance_reimbursement.txt section 2.6)"

    return REFUSAL_TEMPLATE


def main():

    docs = retrieve_documents()

    print("\nPolicy Q&A System")
    print("Type a question or type 'exit' to quit.\n")

    while True:
        question = input("Question: ")

        if question.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        answer = answer_question(docs, question)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()