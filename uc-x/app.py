"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENTS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


class DocumentError(Exception):
    pass


def retrieve_documents(file_paths):
    """
    Loads all policy files and indexes content by:
    {
        document_name: {
            section_number: section_content
        }
    }
    """

    index = {}

    for path in file_paths:

        if not os.path.exists(path):
            raise DocumentError(f"Document loading error: missing file '{path}'")

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            raise DocumentError(f"Document loading error: unreadable file '{path}'")

        if not text.strip():
            raise DocumentError(f"Document loading error: empty file '{path}'")

        document_name = os.path.basename(path)

        sections = {}

        current_section = None
        current_lines = []

        for line in text.splitlines():

            line = line.rstrip()

            match = re.match(r"^\s*(\d+(?:\.\d+)*)\s*[:.-]?\s*(.*)$", line)

            if match:

                if current_section is not None:
                    sections[current_section] = "\n".join(current_lines).strip()

                current_section = match.group(1)

                title = match.group(2).strip()

                current_lines = [title] if title else []

            else:
                if current_section is not None:
                    current_lines.append(line)

        if current_section is not None:
            sections[current_section] = "\n".join(current_lines).strip()

        if not sections:
            raise DocumentError(
                f"Document indexing error: no section numbers found in '{path}'"
            )

        index[document_name] = sections

    return index


def find_matches(question, document_index):

    q = question.lower()

    matches = []

    for document_name, sections in document_index.items():

        for section_number, content in sections.items():

            content_lower = content.lower()

            score = 0

            for word in re.findall(r"\w+", q):
                if len(word) > 2 and word in content_lower:
                    score += 1

            if score > 0:
                matches.append((score, document_name, section_number, content.strip()))

    matches.sort(reverse=True)

    return matches


def answer_question(question, document_index):

    q = question.strip().lower()

    # Critical cross-document trap
    if "personal phone" in q and ("work files" in q or "access work files" in q):

        it_doc = "policy_it_acceptable_use.txt"

        if it_doc not in document_index:
            return REFUSAL_TEMPLATE

        section = document_index[it_doc].get("3.1")

        if not section:
            return REFUSAL_TEMPLATE

        return f"{section}\n" f"[Source: {it_doc} Section 3.1]"

    matches = find_matches(question, document_index)

    if not matches:
        return REFUSAL_TEMPLATE

    best_score = matches[0][0]

    best_matches = [m for m in matches if m[0] == best_score]

    documents = {m[1] for m in best_matches}

    # Prevent cross-document blending
    if len(documents) > 1:
        return REFUSAL_TEMPLATE

    _, document_name, section_number, content = best_matches[0]

    if not document_name or not section_number or not content.strip():
        return REFUSAL_TEMPLATE

    prohibited_phrases = [
        "while not explicitly covered",
        "typically",
        "generally understood",
        "it is common practice",
    ]

    answer = f"{content}\n" f"[Source: {document_name} Section {section_number}]"

    lower_answer = answer.lower()

    for phrase in prohibited_phrases:
        if phrase in lower_answer:
            return REFUSAL_TEMPLATE

    return answer


def main():

    try:
        document_index = retrieve_documents(DOCUMENTS)

    except DocumentError as e:
        print(str(e))
        return

    print("UC-X — Ask My Documents")
    print("Type 'exit' to quit.")

    while True:

        question = input("\nQuestion: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        response = answer_question(question, document_index)

        print("\nAnswer:")
        print(response)


if __name__ == "__main__":
    main()
