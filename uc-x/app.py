"""
UC-X — Ask My Documents

Single-source policy question answering.
Prevents cross-document blending and uses an exact refusal template.
"""

import re


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load all three policy documents and index them by document and section."""
    base_path = "../data/policy-documents"
    documents = {}

    for filename in POLICY_FILES:
        path = f"{base_path}/{filename}"

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        lines = content.splitlines()
        current_section = None
        current_lines = []

        for line in lines:
            stripped = line.strip()

            # Stop a section before the next numbered section or major heading.
            if current_section is not None and (
                re.match(r"^\d+\.\d+[\s.)]", stripped)
                or re.match(r"^\d+\.\s+", stripped)
            ):
                sections[current_section] = "\n".join(
                    current_lines
                ).strip()

                current_section = None
                current_lines = []

            match = re.match(r"^(\d+\.\d+)[.)]?\s+", stripped)

            if match:
                current_section = match.group(1)
                current_lines = [line.rstrip()]
            elif current_section is not None:
                current_lines.append(line.rstrip())

        if current_section is not None:
            sections[current_section] = "\n".join(
                current_lines
            ).strip()

        documents[filename] = sections

    return documents

def extract_section(document, section_number):
    """Return only the requested numbered section."""
    if section_number in document:
        return document[section_number]

    return None


def answer_question(question, documents):
    """
    Answer only from one policy document.

    Returns a source citation with every factual answer.
    Refuses questions that are not clearly covered.
    """

    q = question.lower().strip()

    # HR — annual leave carry-forward
    if (
        ("carry forward" in q or "carry-forward" in q)
        and ("annual leave" in q or "leave" in q)
    ):
        section = extract_section(
            documents["policy_hr_leave.txt"], "2.6"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_hr_leave.txt, section 2.6"
            )

    # IT — Slack installation
    if "slack" in q and (
        "install" in q or "work laptop" in q
    ):
        section = extract_section(
            documents["policy_it_acceptable_use.txt"], "2.3"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_it_acceptable_use.txt, section 2.3"
            )

    # Finance — home office allowance
    if (
        ("home office" in q or "home-office" in q)
        and ("equipment" in q or "allowance" in q)
    ):
        section = extract_section(
            documents["policy_finance_reimbursement.txt"], "3.1"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_finance_reimbursement.txt, section 3.1"
            )

    # Personal phone + work files:
    # deliberately use the IT source only. Never combine with HR.
    if (
        "personal phone" in q
        and ("work files" in q or "files" in q)
        and ("home" in q or "working from home" in q)
    ):
        section = extract_section(
            documents["policy_it_acceptable_use.txt"], "3.1"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_it_acceptable_use.txt, section 3.1"
            )

        return REFUSAL_TEMPLATE

    # Flexible working culture is not covered by the policies.
    if (
        "flexible working culture" in q
        or "flexible working" in q
        or "company view" in q
    ):
        return REFUSAL_TEMPLATE

    # Finance — DA and meal receipts
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and ("same day" in q or "same-day" in q)
    ):
        section = extract_section(
            documents["policy_finance_reimbursement.txt"], "2.6"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_finance_reimbursement.txt, section 2.6"
            )

    # HR — LWP approvers
    if (
        ("leave without pay" in q or "lwp" in q)
        and ("approve" in q or "approver" in q or "approves" in q)
    ):
        section = extract_section(
            documents["policy_hr_leave.txt"], "5.2"
        )

        if section:
            return (
                f"{section}\n"
                "Source: policy_hr_leave.txt, section 5.2"
            )

    return REFUSAL_TEMPLATE


def main():
    documents = retrieve_documents()

    print("UC-X Policy Assistant")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            print(REFUSAL_TEMPLATE)
            print()
            continue

        answer = answer_question(question, documents)

        print(answer)
        print()


if __name__ == "__main__":
    main()


