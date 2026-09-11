"""
UC-X Policy Document Assistant

Answers questions using the available policy documents
without combining information from different documents.
"""

import argparse
import os
import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def load_document(path):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    sections = {}

    pattern = (
        r"(?ms)^\s*(\d+(?:\.\d+)?)\s+(.*?)"
        r"(?=^\s*\d+(?:\.\d+)?\s+|\Z)"
    )

    for match in re.finditer(pattern, text):
        section = match.group(1)
        content = " ".join(match.group(2).split())
        sections[section] = content

    return sections


def retrieve_documents(data_dir):
    documents = {}

    for filename in POLICY_FILES:
        path = os.path.join(data_dir, filename)

        if os.path.exists(path):
            documents[filename] = load_document(path)

    return documents


def get_section(documents, filename, section):
    document = documents.get(filename, {})
    return document.get(section)


def answer_question(question, documents):
    q = question.lower().strip()

    # HR: carry-forward annual leave
    if any(
        word in q
        for word in ["carry forward", "carry-forward", "unused annual leave"]
    ):
        text = get_section(
            documents,
            "policy_hr_leave.txt",
            "2.6",
        )
        if text:
            return f"[policy_hr_leave.txt, Section 2.6] {text}"

    # IT: Slack installation
    if "slack" in q or ("install" in q and "software" in q):
        text = get_section(
            documents,
            "policy_it_acceptable_use.txt",
            "2.3",
        )
        if text:
            return f"[policy_it_acceptable_use.txt, Section 2.3] {text}"

    # Finance: home office equipment
    if (
        "home office" in q
        or "equipment allowance" in q
        or "work from home equipment" in q
    ):
        text = get_section(
            documents,
            "policy_finance_reimbursement.txt",
            "3.1",
        )
        if text:
            return f"[policy_finance_reimbursement.txt, Section 3.1] {text}"

    # IT: personal phone / work files
    # IMPORTANT: use IT section 3.1 only.
    if "personal phone" in q and (
        "work files" in q
        or "access" in q
        or "working from home" in q
    ):
        text = get_section(
            documents,
            "policy_it_acceptable_use.txt",
            "3.1",
        )
        if text:
            return f"[policy_it_acceptable_use.txt, Section 3.1] {text}"

    # Finance: DA and meal expenses
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and (
            "receipt" in q
            or "expense" in q
            or "expenses" in q
            or "claim" in q
        )
    ):
        text = get_section(
            documents,
            "policy_finance_reimbursement.txt",
            "2.6",
        )
        if text:
            return f"[policy_finance_reimbursement.txt, Section 2.6] {text}"

    # HR: LWP approval
    if (
        "lwp" in q
        or "leave without pay" in q
    ) and "approv" in q:
        text = get_section(
            documents,
            "policy_hr_leave.txt",
            "5.2",
        )
        if text:
            return f"[policy_hr_leave.txt, Section 5.2] {text}"

    # Flexible working culture is intentionally out of scope.
    if "flexible working culture" in q:
        return REFUSAL

    return REFUSAL


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions about the available policy documents."
    )

    parser.add_argument(
        "--data-dir",
        default="../data/policy-documents",
        help="Directory containing the three policy documents.",
    )

    args = parser.parse_args()

    documents = retrieve_documents(args.data_dir)

    missing = [
        filename
        for filename in POLICY_FILES
        if filename not in documents
    ]

    if missing:
        print("Error: Missing policy document(s):")
        for filename in missing:
            print(f"- {filename}")
        return

    print("Policy assistant ready. Type 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        print("\nAnswer:")
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()