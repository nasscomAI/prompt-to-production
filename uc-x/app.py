"""
UC-X app.py — Ask My Documents
Policy Q&A agent for CMC employees.
Implements skills: retrieve_documents, answer_question
Enforces rules from agents.md: single-source answers, mandatory citations, verbatim refusal template.
"""

import os
import re

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLICY_FILES = [
    os.path.join(os.path.dirname(__file__), "../data/policy-documents/policy_hr_leave.txt"),
    os.path.join(os.path.dirname(__file__), "../data/policy-documents/policy_it_acceptable_use.txt"),
    os.path.join(os.path.dirname(__file__), "../data/policy-documents/policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# Loads all policy files and indexes by document name → section number → text.
# Halts if any file is missing or unreadable.
# ---------------------------------------------------------------------------

def retrieve_documents(file_paths: list[str]) -> dict:
    """
    Skill: retrieve_documents
    Input:  List of file paths to policy documents.
    Output: Dict — { doc_name: { section_number: section_text } }
    Error:  Raises FileNotFoundError if any file is missing; halts entirely.
    """
    index = {}

    # Section header pattern: digits-and-dots followed by the section title
    # e.g.  "2.6  Leave Carry-Forward" or "3.1 Personal Devices"
    section_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$')

    for path in file_paths:
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(
                f"Policy file not found: {abs_path}\n"
                "Cannot proceed with partial document sets."
            )

        doc_name = os.path.basename(abs_path)
        index[doc_name] = {}

        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_section = None
        current_text = []

        def flush_section():
            if current_section is not None:
                index[doc_name][current_section] = " ".join(current_text).strip()

        for line in lines:
            stripped = line.strip()
            m = section_pattern.match(stripped)
            if m:
                flush_section()
                current_section = m.group(1)
                current_text = [m.group(2)]
            else:
                if current_section is not None and stripped:
                    current_text.append(stripped)

        flush_section()

    return index


# ---------------------------------------------------------------------------
# Skill: answer_question
# Searches the index for a single-source answer + citation.
# Returns refusal template when:
#   - No section matches, OR
#   - More than one document matches (cross-document blending forbidden).
# ---------------------------------------------------------------------------

def answer_question(question: str, doc_index: dict) -> str:
    """
    Skill: answer_question
    Input:  User question (str) + indexed document store from retrieve_documents.
    Output: Single-source answer with (doc_name, section_number) citation,
            OR the verbatim refusal template.
    Error:  If question spans multiple documents → return refusal template.
    """
    question_lower = question.lower()
    question_words = set(re.findall(r'\w+', question_lower))

    hits = []  # list of (doc_name, section_number, section_text, score)

    for doc_name, sections in doc_index.items():
        for section_num, section_text in sections.items():
            section_lower = section_text.lower()
            section_words = set(re.findall(r'\w+', section_lower))

            # Score = number of question words found in section text
            overlap = question_words & section_words
            # Filter out very common stop words from the overlap count
            stop_words = {
                'i', 'can', 'my', 'a', 'the', 'is', 'on', 'in', 'for',
                'to', 'of', 'and', 'or', 'what', 'when', 'who', 'how',
                'me', 'do', 'did', 'same', 'be', 'are', 'at', 'it'
            }
            meaningful_overlap = overlap - stop_words

            if meaningful_overlap:
                hits.append((doc_name, section_num, section_text, len(meaningful_overlap)))

    if not hits:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    hits.sort(key=lambda h: h[3], reverse=True)

    # Check if top matches span more than one document — cross-doc blending prohibited
    top_score = hits[0][3]
    top_docs = {h[0] for h in hits if h[3] == top_score}

    if len(top_docs) > 1:
        return REFUSAL_TEMPLATE

    best_doc, best_section, best_text, _ = hits[0]
    return (
        f"{best_text}\n\n"
        f"[Source: {best_doc}, Section {best_section}]"
    )


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("UC-X — Ask My Documents")
    print("Policy Q&A for CMC employees")
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    try:
        doc_index = retrieve_documents(POLICY_FILES)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    doc_names = list(doc_index.keys())
    total_sections = sum(len(s) for s in doc_index.values())
    print(f"Loaded {len(doc_names)} document(s), {total_sections} section(s) indexed.")
    for name in doc_names:
        print(f"  • {name} ({len(doc_index[name])} sections)")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        answer = answer_question(question, doc_index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
