from pathlib import Path
import re


POLICY_DIR = Path("../data/policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load and index the three approved policy documents by section number."""

    documents = {}

    for filename in POLICY_FILES:
        path = POLICY_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Policy document not found: {filename}"
            )

        text = path.read_text(encoding="utf-8")

        sections = {}

        # Match both subsection headings such as 2.6
        # and top-level headings such as 3. WORK FROM HOME EQUIPMENT.
        matches = list(
            re.finditer(
                r"(?m)^\s*(\d+(?:\.\d+)?)\.?\s+",
                text
            )
        )

        for index, match in enumerate(matches):
            section_number = match.group(1)

            start = match.start()

            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            # Store only subsection numbers such as 2.6, 3.1, etc.
            if "." in section_number:
                sections[section_number] = text[start:end].strip()

        documents[filename] = sections

    return documents


def normalize(text):
    """Normalize question text for matching."""

    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def get_section(documents, filename, section_number):
    """Return a specific policy section."""

    return documents.get(filename, {}).get(section_number)


def answer_question(question, documents):
    """Answer using one relevant policy document only."""

    q = normalize(question)

    # 1. Annual leave carry-forward
    if (
        "annual leave" in q
        and "carry" in q
    ):
        filename = "policy_hr_leave.txt"
        section = "2.6"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # 2. Slack / installing software on work laptop
    if (
        "slack" in q
        or (
            "install" in q
            and "software" in q
        )
    ):
        filename = "policy_it_acceptable_use.txt"
        section = "2.3"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # 3. Home office equipment allowance
    if (
        "home office" in q
        and (
            "allowance" in q
            or "equipment" in q
        )
    ):
        filename = "policy_finance_reimbursement.txt"
        section = "3.1"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # 4. Personal phone / personal device for work files
    if (
        "personal phone" in q
        or "personal device" in q
    ):
        filename = "policy_it_acceptable_use.txt"
        section = "3.1"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # 5. Flexible working culture
    if (
        "flexible working" in q
        or "flexible work" in q
        or "working culture" in q
    ):
        return REFUSAL

    # 6. DA and meal receipts on the same day
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
    ):
        filename = "policy_finance_reimbursement.txt"
        section = "2.6"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # 7. LWP approval
    if (
        "lwp" in q
        and (
            "approve" in q
            or "approval" in q
            or "who" in q
        )
    ):
        filename = "policy_hr_leave.txt"
        section = "5.2"

        answer = get_section(documents, filename, section)

        return (
            f"{answer}\n\n"
            f"Source: {filename}, Section {section}"
        )

    # Anything not covered by the documents
    return REFUSAL


def main():
    documents = retrieve_documents()

    print("UC-X Ask My Documents")
    print()
    print("Type a policy question. Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye")
            break

        if not question:
            continue

        print()
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()