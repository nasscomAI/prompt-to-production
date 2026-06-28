"""
UC-X — Ask My Documents
Interactive policy Q&A
"""

import os
import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)


def load_document(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_sections(text):
    sections = {}
    current = None

    for line in text.splitlines():
        line = line.strip()

        # Skip blank lines and decorative separators
        if not line or line.startswith("═"):
            continue

        # Skip major section headings like "3. WORK FROM HOME EQUIPMENT"
        if re.match(r"^\d+\.\s", line):
            continue

        # Match numbered subsections like "2.6 ..."
        m = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if m:
            current = m.group(1)
            sections[current] = m.group(2)
        elif current:
            sections[current] += " " + line

    return sections


def retrieve_documents():
    base = "../data/policy-documents"

    docs = {
        "policy_hr_leave.txt":
            build_sections(load_document(os.path.join(base, "policy_hr_leave.txt"))),

        "policy_it_acceptable_use.txt":
            build_sections(load_document(os.path.join(base, "policy_it_acceptable_use.txt"))),

        "policy_finance_reimbursement.txt":
            build_sections(load_document(os.path.join(base, "policy_finance_reimbursement.txt"))),
    }

    return docs


def answer_question(question, docs):
    q = question.lower()

    # HR
    if "carry forward" in q or "annual leave" in q:
        return (
            docs["policy_hr_leave.txt"]["2.6"],
            "policy_hr_leave.txt Section 2.6",
        )

    if "leave without pay" in q or "approves leave without pay" in q:
        return (
            docs["policy_hr_leave.txt"]["5.2"],
            "policy_hr_leave.txt Section 5.2",
        )

    # IT
    if "slack" in q:
        return (
            docs["policy_it_acceptable_use.txt"]["2.3"],
            "policy_it_acceptable_use.txt Section 2.3",
        )

    if "personal phone" in q or "personal device" in q or "work files" in q:
        return (
            docs["policy_it_acceptable_use.txt"]["3.1"],
            "policy_it_acceptable_use.txt Section 3.1",
        )

    # Finance
    if "home office" in q or "equipment allowance" in q:
        return (
            docs["policy_finance_reimbursement.txt"]["3.1"],
            "policy_finance_reimbursement.txt Section 3.1",
        )

    if "da" in q and "meal" in q:
        return (
            docs["policy_finance_reimbursement.txt"]["2.6"],
            "policy_finance_reimbursement.txt Section 2.6",
        )

    return (REFUSAL, None)


def main():
    docs = retrieve_documents()

    print("CMC Policy Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in ("exit", "quit"):
            break

        answer, citation = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)

        if citation:
            print(f"\nSource: {citation}")

        print()


if __name__ == "__main__":
    main()