"""
UC-X - Ask My Documents

Deterministic document retrieval and question answering using only
the three supplied CMC policy documents.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS = {
    "policy_hr_leave.txt": REPO_ROOT
    / "data"
    / "policy-documents"
    / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": REPO_ROOT
    / "data"
    / "policy-documents"
    / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": REPO_ROOT
    / "data"
    / "policy-documents"
    / "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def load_document(path):
    """Load one policy document as UTF-8 text."""
    if not path.is_file():
        raise FileNotFoundError(f"Policy document not found: {path}")

    return path.read_text(encoding="utf-8")


def retrieve_documents():
    """Load all three policy documents."""
    documents = {}

    for name, path in DOCUMENTS.items():
        documents[name] = load_document(path)

    return documents


def index_sections(documents):
    """
    Index numbered policy sections by document and section number.

    Each section begins with a heading such as 2.6 or 3.1.
    Major section headings such as 3. SICK LEAVE are also boundaries.
    """
    index = {}

    pattern = re.compile(
        r"(?ms)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*\d+\.\s+|\Z)"
    )

    for document_name, text in documents.items():
        sections = {}

        for match in pattern.finditer(text):
            section_number = match.group(1)
            section_text = " ".join(match.group(2).split())

            # Remove decorative separator characters that may occur
            # immediately before the next major section heading.
            section_text = re.sub(r"^[═=•\-\s]+", "", section_text)
            section_text = re.sub(r"[═=•\-\s]+$", "", section_text)

            sections[section_number] = section_text

        index[document_name] = sections

    return index


def find_sections(index, question):
    """Find sections using explicit question keywords."""
    question_lower = question.lower()

    keyword_map = {
        "policy_hr_leave.txt": {
            "carry forward": ["2.6", "2.7"],
            "unused annual leave": ["2.6", "2.7"],
            "annual leave": ["2.6", "2.7"],
            "leave without pay": ["5.2", "5.3"],
            "without pay": ["5.2", "5.3"],
            "approves leave": ["5.2"],
            "approve leave": ["5.2"],
        },
        "policy_it_acceptable_use.txt": {
            "slack": ["2.3", "2.4"],
            "install": ["2.3", "2.4"],
            "software": ["2.3", "2.4"],
            "personal phone": ["3.1", "3.2"],
            "personal device": ["3.1", "3.2"],
            "work files": ["3.1", "3.2", "5.1"],
            "files from home": ["3.1", "3.2"],
            "work files from home": ["3.1", "3.2"],
        },
        "policy_finance_reimbursement.txt": {
            "equipment allowance": ["3.1", "3.2", "3.3"],
            "home office": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "work from home": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "allowance": ["3.1", "3.2", "3.3"],
            "da": ["2.5", "2.6"],
            "meal receipts": ["2.5", "2.6"],
            "meal": ["2.5", "2.6"],
            "same day": ["2.6"],
        },
    }

    matches = []

    for document_name, mappings in keyword_map.items():
        for keyword, section_numbers in mappings.items():
            if keyword in question_lower:
                for section_number in section_numbers:
                    section = index[document_name].get(section_number)

                    if section:
                        matches.append(
                            (
                                document_name,
                                section_number,
                                section,
                            )
                        )

    # Remove duplicate matches while preserving order.
    unique_matches = []
    seen = set()

    for match in matches:
        key = (match[0], match[1])

        if key not in seen:
            unique_matches.append(match)
            seen.add(key)

    return unique_matches


def answer_question(index, question):
    """
    Answer from one source document or return the exact refusal template.
    """
    matches = find_sections(index, question)

    if not matches:
        return REFUSAL_TEMPLATE

    documents_found = {match[0] for match in matches}

    # Cross-document matches are not blended.
    if len(documents_found) > 1:
        return REFUSAL_TEMPLATE

    document_name = matches[0][0]

    if "carry forward" in question.lower():
        sections = [match for match in matches if match[1] in {"2.6", "2.7"}]

        answer = " ".join(
            f"{section[2]} [{document_name}, section {section[1]}]."
            for section in sections
        )

        return answer

    if "leave without pay" in question.lower() or "without pay" in question.lower():
        sections = [match for match in matches if match[1] in {"5.2", "5.3"}]

        answer = " ".join(
            f"{section[2]} [{document_name}, section {section[1]}]."
            for section in sections
        )

        return answer

    if "personal phone" in question.lower() or "personal device" in question.lower():
        sections = [match for match in matches if match[1] in {"3.1", "3.2"}]

        answer = " ".join(
            f"{section[2]} [{document_name}, section {section[1]}]."
            for section in sections
        )

        return answer

    if "work files" in question.lower() or "files from home" in question.lower():
        sections = [match for match in matches if match[1] in {"3.1", "3.2", "5.1"}]

        answer = " ".join(
            f"{section[2]} [{document_name}, section {section[1]}]."
            for section in sections
        )

        return answer

    answer = " ".join(
        f"{section[2]} [{document_name}, section {section[1]}]." for section in matches
    )

    return answer


def main():
    print("UC-X - Ask My Documents")
    print("Type 'exit' to quit.")
    print()

    documents = retrieve_documents()
    index = index_sections(documents)

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            print(REFUSAL_TEMPLATE)
            print()
            continue

        answer = answer_question(index, question)

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()
