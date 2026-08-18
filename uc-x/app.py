"""
UC-X — Ask My Documents

Source-grounded interactive policy question answering system.
"""

import re
from pathlib import Path


DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load all three policy documents and index numbered subsections."""

    documents = {}

    for document_name, document_path in DOCUMENTS.items():
        path = Path(document_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Required document not found: {document_path}"
            )

        text = path.read_text(encoding="utf-8")

        sections = {}
        current_section = None
        current_lines = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            # Recognize only subsection numbers such as 2.1, 2.6, 3.1.
            # Do NOT recognize major headings such as:
            # 3. WORK FROM HOME EQUIPMENT
            match = re.match(
                r"^(\d+\.\d+)\s+(.*)$",
                line
            )

            if match:
                # Save the previous subsection.
                if current_section is not None:
                    sections[current_section] = " ".join(
                        current_lines
                    ).strip()

                current_section = match.group(1)
                current_lines = [match.group(2)]

            elif current_section is not None:
                # Ignore empty lines.
                if not line:
                    continue

                # Ignore decorative separator lines.
                if set(line).issubset({"═", "-", "_"}):
                    continue

                # Ignore major headings such as:
                # 3. WORK FROM HOME EQUIPMENT
                if re.match(r"^\d+\.\s+", line):
                    continue

                # Keep normal continuation lines.
                current_lines.append(line)

        # Save the final subsection.
        if current_section is not None:
            sections[current_section] = " ".join(
                current_lines
            ).strip()

        documents[document_name] = sections

    return documents


def normalize(text):
    """Normalize text for keyword matching."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def answer_question(question, documents):
    """Return a single-source answer or the exact refusal template."""

    normalized_question = normalize(question)

    # ---------------------------------------------------------
    # Critical cross-document test
    # ---------------------------------------------------------

    personal_phone_terms = [
        "personal phone",
        "work files",
        "working from home",
    ]

    if all(term in normalized_question for term in personal_phone_terms):
        section = documents.get(
            "policy_it_acceptable_use.txt", {}
        ).get("3.1")

        if section:
            return (
                f"{section} "
                "(Source: policy_it_acceptable_use.txt, section 3.1)"
            )

        return REFUSAL

    # ---------------------------------------------------------
    # Keyword mappings
    # ---------------------------------------------------------

    keyword_groups = [
        (
            "policy_hr_leave.txt",
            {
                "carry forward": ["2.6"],
                "annual leave": ["2.6"],
                "leave without pay": ["5.2"],
                "lwp": ["5.2"],
                "sick leave": ["3.2"],
                "leave encashment": ["7.2"],
                "encash": ["7.2"],
            },
        ),
        (
            "policy_it_acceptable_use.txt",
            {
                "slack": ["2.3"],
                "install": ["2.3"],
                "personal phone": ["3.1"],
                "personal device": ["3.1"],
            },
        ),
        (
            "policy_finance_reimbursement.txt",
            {
                "equipment allowance": ["3.1"],
                "home office": ["3.1"],
                "da": ["2.6"],
                "meal receipts": ["2.6"],
            },
        ),
    ]

    matches = []

    for document_name, groups in keyword_groups:
        for keyword, section_numbers in groups.items():

            if normalize(keyword) in normalized_question:

                for section_number in section_numbers:

                    section = documents.get(
                        document_name, {}
                    ).get(section_number)

                    if section:
                        matches.append(
                            (
                                document_name,
                                section_number,
                                section,
                            )
                        )

    # ---------------------------------------------------------
    # No supported evidence
    # ---------------------------------------------------------

    if not matches:
        return REFUSAL

    # Remove duplicate matches.
    unique_matches = list(dict.fromkeys(matches))

    # ---------------------------------------------------------
    # Never blend claims from different documents.
    # ---------------------------------------------------------

    source_documents = {
        match[0]
        for match in unique_matches
    }

    if len(source_documents) > 1:
        return REFUSAL

    # ---------------------------------------------------------
    # Return the single-source answer.
    # ---------------------------------------------------------

    document_name, section_number, section = unique_matches[0]

    return (
        f"{section} "
        f"(Source: {document_name}, section {section_number})"
    )


def main():
    documents = retrieve_documents()

    print("UC-X Policy Assistant")
    print("Documents loaded:")

    for document_name in documents:
        print(f"- {document_name}")

    print("\nType 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(
            question,
            documents
        )

        print(f"\nAnswer: {answer}")


if __name__ == "__main__":
    main()
