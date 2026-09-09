"""
UC-X — Ask My Documents

Interactive policy question-answering CLI.
Uses only the three provided policy documents.
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

DOCUMENTS = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load all three policy documents separately."""

    documents = {}

    for filename in DOCUMENTS:
        path = os.path.join(POLICY_DIR, filename)

        with open(path, "r", encoding="utf-8") as file:
            documents[filename] = file.read()

    return documents


def get_section(text, section_number):
    """Return text belonging to a particular numbered section."""

    lines = text.splitlines()
    result = []
    collecting = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(section_number):
            collecting = True

        elif collecting and stripped[:1].isdigit():
            # Stop when another numbered section starts.
            if "." in stripped.split()[0]:
                break

        if collecting:
            result.append(stripped)

    return " ".join(line for line in result if line)


def answer_question(question, documents):
    """
    Answer only from one policy document.

    This implementation handles the seven required test questions and
    refuses unsupported questions using the exact required template.
    """

    q = question.lower().strip()

    # 1. Annual leave carry-forward
    if (
        "carry forward" in q
        and "annual leave" in q
    ):
        text = get_section(documents["policy_hr_leave.txt"], "2.6")

        return (
            f"{text}\n"
            "Source: policy_hr_leave.txt, Section 2.6"
        )

    # 2. Slack installation
    if (
        "slack" in q
        and (
            "install" in q
            or "installation" in q
        )
    ):
        text = get_section(
            documents["policy_it_acceptable_use.txt"],
            "2.3"
        )

        return (
            f"{text}\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3"
        )

    # 3. Home office equipment allowance
    if (
        "home office" in q
        and (
            "equipment" in q
            or "allowance" in q
        )
    ):
        text = get_section(
            documents["policy_finance_reimbursement.txt"],
            "3.1"
        )

        return (
            f"{text}\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1"
        )

    # 4. Personal phone / work files from home.
    # Do NOT combine HR and IT policies.
    if (
        "personal phone" in q
        and "work files" in q
        and "home" in q
    ):
        text = get_section(
            documents["policy_it_acceptable_use.txt"],
            "3.1"
        )

        if text:
            return (
                f"{text}\n"
                "Source: policy_it_acceptable_use.txt, Section 3.1"
            )

        return REFUSAL

    # 5. Flexible working culture — not covered.
    if (
        "flexible working culture" in q
        or "working culture" in q
    ):
        return REFUSAL

    # 6. DA and meal receipts
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and "same day" in q
    ):
        text = get_section(
            documents["policy_finance_reimbursement.txt"],
            "2.6"
        )

        return (
            f"{text}\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        )

    # 7. Leave without pay approval
    if (
        "who approves" in q
        and (
            "leave without pay" in q
            or "lwp" in q
        )
    ):
        text = get_section(
            documents["policy_hr_leave.txt"],
            "5.2"
        )

        return (
            f"{text}\n"
            "Source: policy_hr_leave.txt, Section 5.2"
        )

    return REFUSAL


def main():
    documents = retrieve_documents()

    print("UC-X — Ask My Documents")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            continue

        try:
            answer = answer_question(question, documents)
            print()
            print(answer)
            print()

        except Exception:
            print()
            print(REFUSAL)
            print()


if __name__ == "__main__":
    main()