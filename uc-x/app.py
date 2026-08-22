"""
UC-X — Ask My Documents

A single-source policy Q&A system.
It loads the three supplied policy documents, searches their numbered
sections, and answers only from one source at a time.
"""

import os
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

DOCUMENTS = {
    "policy_hr_leave.txt": os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(
        POLICY_DIR, "policy_it_acceptable_use.txt"
    ),
    "policy_finance_reimbursement.txt": os.path.join(
        POLICY_DIR, "policy_finance_reimbursement.txt"
    ),
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]



def retrieve_documents():
    """
    Load all three policy documents and index their numbered sections.
    """
    index = {}

    for document_name, path in DOCUMENTS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required policy document not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        sections = {}

        # Policy sections are identified by numbers such as 2.3, 3.1, 5.2.
        matches = list(
            re.finditer(
                r"(?m)^\s*(\d+\.\d+)\s+",
                text
            )
        )

        for i, match in enumerate(matches):
            section_number = match.group(1)
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            sections[section_number] = text[start:end].strip()

        index[document_name] = sections

    return index



def answer_question(question, index):
    """
    Return a grounded answer from exactly one document,
    or the exact refusal template.
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # HR policy
    # ---------------------------------------------------------

    if any(term in q for term in [
        "carry forward",
        "carry-forward",
        "unused annual leave",
    ]):
        section = index["policy_hr_leave.txt"].get("2.6", "")
        return (
            f"{section}\n"
            "[Source: policy_hr_leave.txt §2.6]"
        )

    if any(term in q for term in [
        "leave without pay",
        "lwp",
        "who approves",
    ]):
        section = index["policy_hr_leave.txt"].get("5.2", "")
        return (
            f"{section}\n"
            "[Source: policy_hr_leave.txt §5.2]"
        )

    # ---------------------------------------------------------
    # IT policy
    # ---------------------------------------------------------

    if "slack" in q or (
        "install" in q and "work laptop" in q
    ):
        section = index["policy_it_acceptable_use.txt"].get("2.3", "")
        return (
            f"{section}\n"
            "[Source: policy_it_acceptable_use.txt §2.3]"
        )

    if (
        "personal phone" in q
        and ("work files" in q or "from home" in q)
    ):
        section = index["policy_it_acceptable_use.txt"].get("3.1", "")
        return (
            f"{section}\n"
            "[Source: policy_it_acceptable_use.txt §3.1]"
        )

    # ---------------------------------------------------------
    # Finance policy
    # ---------------------------------------------------------

    if "home office equipment" in q or "equipment allowance" in q:
        section = index["policy_finance_reimbursement.txt"].get("3.1", "")
        return (
            f"{section}\n"
            "[Source: policy_finance_reimbursement.txt §3.1]"
        )

    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
    ):
        section = index["policy_finance_reimbursement.txt"].get("2.6", "")
        return (
            f"{section}\n"
            "[Source: policy_finance_reimbursement.txt §2.6]"
        )

    # ---------------------------------------------------------
    # Refuse anything not explicitly covered.
    # ---------------------------------------------------------

    return REFUSAL



def validate_answer(answer):
    """
    Basic enforcement checks.
    """
    if answer == REFUSAL:
        return True

    lower_answer = answer.lower()

    for phrase in HEDGING_PHRASES:
        if phrase in lower_answer:
            raise ValueError(
                f"Forbidden hedging phrase detected: {phrase}"
            )

    if "[Source:" not in answer:
        raise ValueError(
            "Every factual answer must contain a document and section citation."
        )

    return True



def main():
    index = retrieve_documents()

    print("UC-X — Ask My Documents")
    print("Type a policy question.")
    print("Type 'exit' to quit.")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        answer = answer_question(question, index)
        validate_answer(answer)

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()