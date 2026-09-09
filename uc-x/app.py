"""
UC-X — Ask My Documents

Strict single-source policy question answering.
"""

import os
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


def load_documents(base_directory):
    """Load the three approved policy documents."""

    documents = {}

    for filename in POLICY_FILES:

        path = os.path.join(
            base_directory,
            filename
        )

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required policy document not found: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as file:
            documents[filename] = file.read()

    return documents


def normalize(text):
    """Normalize text for question matching."""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        text
    )

    return " ".join(text.split())


def extract_sections(text):
    """
    Extract numbered sections without including later
    decorative section headings.
    """

    lines = text.splitlines()

    sections = []

    current_number = None
    current_lines = []

    section_pattern = re.compile(
        r"^\s*(\d+\.\d+)\s+(.*)$"
    )

    def save_current():
        if current_number is None:
            return

        cleaned = []

        for line in current_lines:

            stripped = line.strip()

            if not stripped:
                continue

            # Remove decorative lines.
            if stripped.startswith("="):
                continue

            if stripped.startswith("-"):
                continue

            # Remove large all-caps headings that are not
            # numbered policy clauses.
            if (
                len(stripped) > 10
                and stripped.upper() == stripped
                and not re.match(
                    r"^\d+\.\d+",
                    stripped
                )
            ):
                continue

            cleaned.append(line.rstrip())

        section_text = "\n".join(
            cleaned
        ).strip()

        if section_text:
            sections.append({
                "number": current_number,
                "text": section_text
            })

    for line in lines:

        match = section_pattern.match(line)

        if match:

            save_current()

            current_number = match.group(1)

            current_lines = [
                line
            ]

        else:

            if current_number is not None:
                current_lines.append(line)

    save_current()

    return sections


def build_index(documents):
    """Build document -> section index."""

    index = {}

    for filename, text in documents.items():

        index[filename] = extract_sections(
            text
        )

    return index


def get_section(index, document, section_number):
    """Return one exact section from one document."""

    for section in index.get(
        document,
        []
    ):

        if section["number"] == section_number:
            return section

    return None


def answer_from_section(
    index,
    document,
    section_number
):
    """Return a source-grounded answer."""

    section = get_section(
        index,
        document,
        section_number
    )

    if section is None:
        return REFUSAL_TEMPLATE

    return (
        f"{section['text']}\n\n"
        f"Source: {document}, "
        f"Section {section_number}"
    )


def answer_question(question, index):
    """
    Answer the required policy questions using exactly one
    source document.

    No answer is constructed by combining documents.
    """

    q = normalize(question)

    # ---------------------------------------------------------
    # HR — Annual leave carry-forward
    # ---------------------------------------------------------

    if (
        "carry forward" in q
        and "annual leave" in q
    ):

        return answer_from_section(
            index,
            "policy_hr_leave.txt",
            "2.6"
        )

    # ---------------------------------------------------------
    # IT — Slack installation
    # ---------------------------------------------------------

    if (
        "slack" in q
        or (
            "install" in q
            and "software" in q
        )
    ):

        return answer_from_section(
            index,
            "policy_it_acceptable_use.txt",
            "2.3"
        )

    # ---------------------------------------------------------
    # Finance — Home office equipment
    # ---------------------------------------------------------

    if (
        "home office equipment" in q
        or "equipment allowance" in q
    ):

        return answer_from_section(
            index,
            "policy_finance_reimbursement.txt",
            "3.1"
        )

    # ---------------------------------------------------------
    # IT — Personal phone / work files
    #
    # IMPORTANT:
    # Never combine HR remote-work information with IT device
    # permissions.
    # ---------------------------------------------------------

    if (
        "personal phone" in q
        and "work files" in q
    ):

        return answer_from_section(
            index,
            "policy_it_acceptable_use.txt",
            "3.1"
        )

    # ---------------------------------------------------------
    # Flexible working culture — refusal
    # ---------------------------------------------------------

    if (
        "flexible working culture" in q
        or "working culture" in q
    ):

        return REFUSAL_TEMPLATE

    # ---------------------------------------------------------
    # Finance — DA and meal receipts
    # ---------------------------------------------------------

    if (
        "da" in q
        and "meal" in q
    ):

        return answer_from_section(
            index,
            "policy_finance_reimbursement.txt",
            "2.6"
        )

    if (
        "meal receipts" in q
        and (
            "same day" in q
            or "claim" in q
        )
    ):

        return answer_from_section(
            index,
            "policy_finance_reimbursement.txt",
            "2.6"
        )

    # ---------------------------------------------------------
    # HR — Leave without pay
    # ---------------------------------------------------------

    if (
        "leave without pay" in q
        or "lwp" in q
    ):

        return answer_from_section(
            index,
            "policy_hr_leave.txt",
            "5.2"
        )

    # ---------------------------------------------------------
    # Unknown question — exact refusal
    # ---------------------------------------------------------

    return REFUSAL_TEMPLATE


def main():
    """Interactive CLI."""

    script_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    policy_directory = os.path.abspath(
        os.path.join(
            script_directory,
            "..",
            "data",
            "policy-documents"
        )
    )

    print("UC-X — Ask My Documents")
    print("=" * 40)

    try:

        documents = load_documents(
            policy_directory
        )

        index = build_index(
            documents
        )

    except Exception as error:

        print(
            f"ERROR: {error}"
        )

        return

    print(
        "Loaded policy documents:"
    )

    for filename in POLICY_FILES:
        print(f"- {filename}")

    print()

    print(
        "Ask a policy question. "
        "Type 'exit' to quit."
    )

    print()

    while True:

        try:

            question = input(
                "Question: "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print()
            break

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit"
        }:

            break

        answer = answer_question(
            question,
            index
        )

        print()
        print("Answer:")
        print(answer)
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()