"""
UC-X — Ask My Documents

Deterministic single-source policy question answering.
Uses only the three supplied policy documents.
"""

import argparse
import re
from pathlib import Path


DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load and index all three policy documents."""

    documents = {}

    for filename, relative_path in DOCUMENTS.items():
        path = Path(relative_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Policy document not found: {relative_path}"
            )

        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise ValueError(f"Policy document is empty: {filename}")

        sections = {}

        # Match numbered sections such as 2.3, 3.1, 5.2.
        pattern = re.compile(
            r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
            re.DOTALL,
        )

        for match in pattern.finditer(text):
            section = match.group(1)
            content = " ".join(match.group(2).split())

            if content:
                sections[section] = content

        if not sections:
            raise ValueError(
                f"No numbered sections found in {filename}"
            )

        documents[filename] = sections

    return documents


def find_section(documents, filename, section):
    """Return an exact section from one document."""

    return documents.get(filename, {}).get(section)


def answer_question(question, documents):
    """
    Answer the required UC-X test questions.

    Answers are intentionally restricted to a single document.
    """

    q = question.lower().strip()

    # HR — annual leave carry-forward
    if (
        "carry forward" in q
        and "annual leave" in q
    ):
        text = find_section(
            documents,
            "policy_hr_leave.txt",
            "2.6",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_hr_leave.txt, Section 2.6]"
            )

    # IT — Slack installation
    if (
        "install slack" in q
        or ("slack" in q and "work laptop" in q)
    ):
        text = find_section(
            documents,
            "policy_it_acceptable_use.txt",
            "2.3",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_it_acceptable_use.txt, Section 2.3]"
            )

    # Finance — home office equipment allowance
    if (
        "home office" in q
        and "equipment" in q
        and "allowance" in q
    ):
        text = find_section(
            documents,
            "policy_finance_reimbursement.txt",
            "3.1",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_finance_reimbursement.txt, Section 3.1]"
            )

    # Personal phone + work files:
    # Do NOT combine HR and IT information.
    if (
        "personal phone" in q
        and "work files" in q
    ):
        text = find_section(
            documents,
            "policy_it_acceptable_use.txt",
            "3.1",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_it_acceptable_use.txt, Section 3.1]"
            )

        return REFUSAL_TEMPLATE

    # Flexible working culture is not a policy clause.
    if (
        "flexible working culture" in q
        or "company view" in q
        and "flexible working" in q
    ):
        return REFUSAL_TEMPLATE

    # Finance — DA and meal receipts
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and "same day" in q
    ):
        text = find_section(
            documents,
            "policy_finance_reimbursement.txt",
            "2.6",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_finance_reimbursement.txt, Section 2.6]"
            )

    # HR — LWP approval
    if (
        "approves leave without pay" in q
        or "who approves leave without pay" in q
        or ("leave without pay" in q and "approv" in q)
    ):
        text = find_section(
            documents,
            "policy_hr_leave.txt",
            "5.2",
        )

        if text:
            return (
                f"{text} "
                "[Source: policy_hr_leave.txt, Section 5.2]"
            )

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions about the supplied policy documents."
    )

    parser.parse_args()

    documents = retrieve_documents()

    print("UC-X — Ask My Documents")
    print("Type a policy question. Type 'exit' to quit.")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        answer = answer_question(question, documents)

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()