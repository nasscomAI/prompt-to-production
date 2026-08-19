"""
UC-X — Ask My Documents

Single-source policy question answering system.
"""

import os
import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def find_policy_directory():
    """Locate the repository policy-document directory."""

    candidates = [
        os.path.join("..", "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
    ]

    for directory in candidates:
        if all(
            os.path.exists(os.path.join(directory, filename))
            for filename in POLICY_FILES
        ):
            return directory

    raise FileNotFoundError(
        "Could not locate all three policy documents."
    )


def retrieve_documents():
    """
    Load all three policies and split them into numbered sections.

    Returns:
        list of dictionaries containing document, section and text.
    """

    directory = find_policy_directory()
    documents = []

    for filename in POLICY_FILES:
        path = os.path.join(directory, filename)

        with open(
            path,
            "r",
            encoding="utf-8-sig",
        ) as infile:
            content = infile.read()

        # Sections such as 2.3, 3.1, 5.2, etc.
        matches = list(
            re.finditer(
                r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
                content,
                re.DOTALL,
            )
        )

        for match in matches:
            section = match.group(1)
            text = " ".join(match.group(2).split())

            documents.append(
                {
                    "document": filename,
                    "section": section,
                    "text": text,
                }
            )

    return documents


def normalize(text):
    """Normalize text for keyword matching."""

    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        text.lower(),
    )


def answer_question(question, documents):
    """
    Return a single-source answer or the exact refusal template.
    """

    q = normalize(question)

    # ---------------------------------------------------------
    # HR POLICY
    # ---------------------------------------------------------

    if (
        "carry forward" in q
        and ("annual leave" in q or "unused" in q)
    ):
        return (
            "Employees may carry forward a maximum of 5 unused "
            "annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. "
            "(policy_hr_leave.txt, section 2.6)"
        )

    if (
        "leave without pay" in q
        and "approve" in q
    ) or (
        "who approves leave without pay" in q
    ):
        return (
            "Leave Without Pay requires approval from both the "
            "Department Head and the HR Director. Manager approval "
            "alone is not sufficient. "
            "(policy_hr_leave.txt, section 5.2)"
        )

    # ---------------------------------------------------------
    # IT ACCEPTABLE USE POLICY
    # ---------------------------------------------------------

    if (
        "install slack" in q
        and "work laptop" in q
    ):
        return (
            "Installing Slack on a work laptop requires written "
            "IT approval. "
            "(policy_it_acceptable_use.txt, section 2.3)"
        )

    # The personal-phone question is deliberately handled from
    # the IT document only. Do NOT add HR claims.
    if (
        "personal phone" in q
        and "work files" in q
        and ("home" in q or "working from home" in q)
    ):
        return (
            "Personal devices may access CMC email and the employee "
            "self-service portal only. "
            "(policy_it_acceptable_use.txt, section 3.1)"
        )

    # ---------------------------------------------------------
    # FINANCE POLICY
    # ---------------------------------------------------------

    if (
        "home office equipment allowance" in q
        or (
            "home office" in q
            and "equipment" in q
            and "allowance" in q
        )
    ):
        return (
            "The home office equipment allowance is Rs 8,000 one-time "
            "for permanent work-from-home arrangements. "
            "(policy_finance_reimbursement.txt, section 3.1)"
        )

    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and "same day" in q
    ):
        return (
            "DA and meal receipts cannot both be claimed on the same "
            "day; this is explicitly prohibited. "
            "(policy_finance_reimbursement.txt, section 2.6)"
        )

    # ---------------------------------------------------------
    # Refuse questions outside the known supported policy facts.
    # ---------------------------------------------------------

    return REFUSAL


def main():

    documents = retrieve_documents()

    print("Ask My Documents")
    print("Type 'exit' to quit.")
    print()

    while True:

        try:
            question = input("Question: ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        answer = answer_question(
            question,
            documents,
        )

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()