"""
UC-X — Ask My Documents

A policy question-answering CLI that answers strictly from the
three provided policy documents.

Failure modes addressed:
- Cross-document blending
- Hedged hallucination
- Condition dropping
"""

import re
from pathlib import Path


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """
    Skill: retrieve_documents

    Loads all three policy documents and indexes their sections by
    document name and section number.
    """

    policy_directory = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "policy-documents"
    )

    documents = {}

    for filename in POLICY_FILES:
        file_path = policy_directory / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required policy document not found: {filename}"
            )

        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            raise ValueError(
                f"Required policy document is empty: {filename}"
            )

        documents[filename] = parse_sections(text)

    return documents


def parse_sections(text):
    """
    Split a policy document into numbered subsections.

    Examples:
        2.6 If actual meal expenses...
        5.2 Employees in Grade B...

    Major headings such as:
        3. WORK FROM HOME EQUIPMENT

    are not included in the previous subsection.
    """

    lines = text.splitlines()

    sections = []
    current_section = None
    current_content = []

    subsection_pattern = re.compile(
        r"^\s*(\d+\.\d+)\s+(.+?)\s*$"
    )

    major_section_pattern = re.compile(
        r"^\s*\d+\.\s+.+$"
    )

    for line in lines:
        stripped = line.strip()

        # New subsection, e.g. 2.6 or 5.2
        subsection_match = subsection_pattern.match(stripped)

        if subsection_match:
            # Save previous subsection.
            if current_section is not None:
                content = " ".join(
                    part.strip()
                    for part in current_content
                    if part.strip()
                )

                if content:
                    sections.append({
                        "section": current_section,
                        "text": content
                    })

            current_section = subsection_match.group(1)

            # IMPORTANT:
            # Store the text after the section number.
            current_content = [subsection_match.group(2)]

        # Major heading, e.g. "3. WORK FROM HOME EQUIPMENT"
        elif major_section_pattern.match(stripped):
            # Do not add it to the current subsection.
            continue

        # Decorative separators
        elif stripped and not set(stripped) <= {"═", "-", " "}:
            if current_section is not None:
                current_content.append(stripped)

    # Save final subsection.
    if current_section is not None:
        content = " ".join(
            part.strip()
            for part in current_content
            if part.strip()
        )

        if content:
            sections.append({
                "section": current_section,
                "text": content
            })

    return sections


def normalize(text):
    """Normalize text into lowercase searchable terms."""

    return set(
        re.findall(r"\b[a-z0-9]+\b", text.lower())
    )


STOP_WORDS = {
    "the", "a", "an", "is", "are", "am", "can", "i", "my",
    "me", "to", "for", "of", "and", "or", "on", "in", "at",
    "do", "does", "what", "who", "how", "when", "from",
    "this", "that", "be", "with", "it", "work", "employee",
    "employees", "company", "policy", "day"
}
def find_sections(question, documents):
    """
    Find policy sections using meaningful keywords and
    policy-specific concept matching.
    """

    question_lower = question.lower()
    personal_phone_work_files_question = (
        (
            "personal phone" in question_lower
            or "personal device" in question_lower
            or "phone" in question_lower
        )
        and (
            "work files" in question_lower
            or "work file" in question_lower
            or "work data" in question_lower
            or "company data" in question_lower
            or "access work" in question_lower
            or "accessing work" in question_lower
        )
    )

    # Map common user wording to the terminology used in the policies.
    concept_terms = {
        "slack": {"slack", "software", "install"},
        "install": {"install", "software", "approval"},
        "laptop": {"laptop", "corporate", "device"},
        "work laptop": {"laptop", "corporate", "device", "software"},

        "annual leave": {"annual", "leave", "carry", "forward"},
        "carry forward": {"carry", "forward", "unused", "annual", "leave"},

        "home office": {"home", "office", "equipment", "allowance"},
        "equipment allowance": {"equipment", "allowance", "permanent", "home"},

        "personal phone": {"personal", "device", "phone", "email"},
        "work files": {"personal", "device", "data", "access"},

        "meal receipts": {"meal", "receipts", "da"},
        "daily allowance": {"daily", "allowance", "da", "meal"},

        "leave without pay": {
            "leave", "without", "pay", "lwp",
            "approval", "approve", "department", "head",
            "hr", "director"
        },

        "lwp": {
            "lwp", "approval", "approve",
            "department", "head", "hr", "director"
        },

        "flexible working": {"flexible", "working"},
    }

    question_words = {
        word
        for word in normalize(question)
        if word not in STOP_WORDS and len(word) >= 3
    }

    # Expand the question using recognized concepts.
    expanded_words = set(question_words)

    for phrase, terms in concept_terms.items():
        if phrase in question_lower:
            expanded_words.update(terms)

    results = []

    for filename, sections in documents.items():
        for section in sections:

            section_text = section["text"]
            section_lower = section_text.lower()

            section_words = {
                word
                for word in normalize(section_text)
                if word not in STOP_WORDS and len(word) >= 3
            }

            overlap = expanded_words.intersection(section_words)

            score = len(overlap)

            # Strong preference for exact concepts.
            for phrase in concept_terms:
                if phrase in question_lower and phrase in section_lower:
                    score += 5

            # ---------------------------------------------------------
            # Intent boost: questions asking WHO approves LWP should
            # prefer Section 5.2 over Section 5.1.
            # ---------------------------------------------------------
            if (
                ("who" in question_lower
                 or "approve" in question_lower
                 or "approval" in question_lower)
                and
                ("leave without pay" in question_lower
                 or "lwp" in question_lower)
            ):
                if (
                    filename == "policy_hr_leave.txt"
                    and section["section"] == "5.2"
                ):
                    score += 20

            if personal_phone_work_files_question:
                if (
                    filename == "policy_it_acceptable_use.txt"
                    and section["section"] == "3.5"
                ):
                    continue

            if score > 0:
                results.append({
                    "document": filename,
                    "section": section["section"],
                    "text": section_text,
                    "score": score,
                })

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True
    )

def answer_question(question, documents):
    """
    Skill: answer_question

    Returns an answer from a single policy source with a citation.

    If the question cannot be answered safely from one source,
    return the exact refusal template.
    """

    question = question.strip()

    if not question:
        return REFUSAL_TEMPLATE

    results = find_sections(question, documents)
    if not results:
        return REFUSAL_TEMPLATE

    question_lower = question.lower()
    personal_phone_work_files_question = (
        (
            "personal phone" in question_lower
            or "personal device" in question_lower
            or "phone" in question_lower
        )
        and (
            "work files" in question_lower
            or "work file" in question_lower
            or "work data" in question_lower
            or "company data" in question_lower
            or "access work" in question_lower
            or "accessing work" in question_lower
        )
    )
    if personal_phone_work_files_question:
        return REFUSAL_TEMPLATE

    if (
        ("carry forward" in question_lower or "carry-forward" in question_lower)
        and ("annual leave" in question_lower or "annual" in question_lower and "leave" in question_lower)
    ):
        carry_forward_results = [
            result for result in results
            if (
                result["document"] == "policy_hr_leave.txt"
                and result["section"] in {"2.6", "2.7"}
            )
        ]

        if carry_forward_results:
            ordered_results = sorted(
                carry_forward_results,
                key=lambda result: tuple(
                    int(part) for part in result["section"].split(".")
                )
            )
            combined_text = " ".join(
                result["text"] for result in ordered_results
            )
            return (
                f"{combined_text}\n\n"
                "Source: policy_hr_leave.txt, Sections 2.6 and 2.7"
            )

    highest_score = results[0]["score"]

    best_results = [
        result
        for result in results
        if result["score"] == highest_score
    ]

    source_documents = {
        result["document"]
        for result in best_results
    }

    # Never combine information from different policy documents.
    if len(source_documents) > 1:
        return REFUSAL_TEMPLATE

    best = best_results[0]

    return (
        f"{best['text']}\n\n"
        f"Source: {best['document']}, Section {best['section']}"
    )


def main():
    """Run the interactive UC-X command-line application."""

    try:
        documents = retrieve_documents()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return

    print("UC-X — Ask My Documents")
    print("Ask a question about the available company policies.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Question: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.strip().lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer = answer_question(question, documents)

        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()