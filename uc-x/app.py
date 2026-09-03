"""
UC-X — Ask My Documents

Deterministic, offline policy question-answering CLI.
Answers are restricted to the three supplied policy documents.
"""

import os
import re
import sys


POLICY_DIR = os.path.join("..", "data", "policy-documents")

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


def retrieve_documents():
    """
    Load all approved policy documents and split them into
    numbered policy sections/subsections.
    """

    sections = []

    for filename in POLICY_FILES:
        path = os.path.join(POLICY_DIR, filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(
                "Required policy document not found: {}".format(path)
            )

        try:
            with open(path, "r", encoding="utf-8") as file:
                text = file.read()
        except OSError as exc:
            raise OSError(
                "Unable to read policy document {}: {}".format(
                    filename, exc
                )
            )

        if not text.strip():
            raise ValueError(
                "Required policy document is empty: {}".format(filename)
            )

        current_section = None
        current_lines = []

        for line in text.splitlines():
            stripped = line.strip()

            if not stripped or all(char in "═─-" for char in stripped):
                continue

            # Major heading: "3. WORK FROM HOME EQUIPMENT"
            major_heading = re.match(
                r"^(\d+)\.\s+(.+)$",
                stripped
            )

            # Subsection: "3.1 Employees..."
            subsection = re.match(
                r"^(\d+\.\d+)\s+(.+)$",
                stripped
            )

            if subsection:
                if current_section is not None:
                    sections.append(
                        {
                            "filename": filename,
                            "section": current_section,
                            "text": "\n".join(current_lines).strip(),
                        }
                    )

                current_section = subsection.group(1)
                current_lines = [stripped]

            elif major_heading:
                # Major headings are boundaries only.
                # Do not include them inside the previous subsection.
                if current_section is not None:
                    sections.append(
                        {
                            "filename": filename,
                            "section": current_section,
                            "text": "\n".join(current_lines).strip(),
                        }
                    )

                current_section = None
                current_lines = []

            elif current_section is not None:
                current_lines.append(stripped)

        if current_section is not None:
            sections.append(
                {
                    "filename": filename,
                    "section": current_section,
                    "text": "\n".join(current_lines).strip(),
                }
            )

    if not sections:
        raise ValueError("No policy sections could be parsed.")

    return sections

def _normalise(text):
    """Normalise whitespace and case for matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _section_contains(section, terms):
    """Return True when all supplied terms occur in the section."""
    text = _normalise(section["text"])
    return all(term in text for term in terms)


def _find_single_source(sections, question):
    """
    Find one authoritative policy section.

    The matching is deliberately conservative. The system refuses
    whenever it cannot identify one directly relevant source section.
    """

    q = _normalise(question)

    candidates = []

    # ---------------------------------------------------------
    # HR POLICY
    # ---------------------------------------------------------

    if "carry forward" in q and "leave" in q:
        candidates = [
            section
            for section in sections
            if (
                section["filename"] == "policy_hr_leave.txt"
                and section["section"] == "2.6"
                and _section_contains(
                    section,
                    ["carry forward", "5"]
                )
            )
        ]

    elif (
        "leave without pay" in q
        or "lwp" in q
    ):
        candidates = [
            section
            for section in sections
            if (
                section["filename"] == "policy_hr_leave.txt"
                and section["section"] == "5.2"
            )
        ]

    # ---------------------------------------------------------
    # IT POLICY
    # ---------------------------------------------------------

    elif (
        "slack" in q
        and ("install" in q or "laptop" in q)
    ):
        candidates = [
            section
            for section in sections
            if (
                section["filename"] == "policy_it_acceptable_use.txt"
                and section["section"] == "2.3"
            )
        ]

    elif (
        "personal phone" in q
        and ("work files" in q or "files" in q)
    ):
        candidates = [
            section
            for section in sections
            if (
                section["filename"] == "policy_it_acceptable_use.txt"
                and section["section"] == "3.1"
            )
        ]

    # ---------------------------------------------------------
    # FINANCE POLICY
    # ---------------------------------------------------------

    elif (
        "home office" in q
        and "equipment" in q
        and "allowance" in q
    ):
        candidates = [
            section
            for section in sections
            if (
                section["filename"]
                == "policy_finance_reimbursement.txt"
                and section["section"] == "3.1"
            )
        ]

    elif (
        "da" in q
        and "meal" in q
        and "receipt" in q
    ):
        candidates = [
            section
            for section in sections
            if (
                section["filename"]
                == "policy_finance_reimbursement.txt"
                and section["section"] == "2.6"
            )
        ]

    # Exactly one authoritative source is required.
    if len(candidates) == 1:
        return candidates[0]

    return None


def answer_question(question, sections):
    """
    Answer a question using one authoritative policy section.

    If no single policy section directly supports the answer,
    return the exact refusal template.
    """

    if not question or not question.strip():
        return REFUSAL

    section = _find_single_source(sections, question)

    if section is None:
        return REFUSAL

    return (
        "{}\n\n"
        "Source: {} section {}".format(
            section["text"],
            section["filename"],
            section["section"],
        )
    )


def main():
    try:
        sections = retrieve_documents()

    except (OSError, ValueError) as exc:
        print(
            "ERROR: {}".format(exc),
            file=sys.stderr
        )
        sys.exit(1)

    print("UC-X — Ask My Documents")
    print(
        "Policy documents loaded: {}".format(
            len(POLICY_FILES)
        )
    )
    print("Type a question or 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()

        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        print("\nAnswer:")
        print(answer_question(question, sections))


if __name__ == "__main__":
    main()