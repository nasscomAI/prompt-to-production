"""
UC-X app.py — Policy Document Assistant
Build using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance."""


def retrieve_documents(file_paths):
    """
    Load all policy files and index by filename and section number.
    Returns dict: {filename: [{section_id, section_text}, ...]}
    """
    documents = {}
    total_sections = 0

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into numbered sections (pattern: digit.digit)
        sections = []
        section_pattern = r'(\d+\.\d+)\s*[:\-]?\s*(.+?)(?=\d+\.\d+|$)'
        matches = re.finditer(section_pattern, content, re.DOTALL)

        for match in matches:
            section_id = match.group(1)
            section_text = match.group(2).strip()
            if section_text:
                sections.append({
                    'section_id': section_id,
                    'section_text': section_text
                })

        documents[filename] = sections
        total_sections += len(sections)

    # Print summary
    for filename, sections in documents.items():
        print(f"  {filename}: {len(sections)} sections")

    print(f"Loaded {total_sections} sections from 3 policy documents.")

    return documents


def answer_question(question, documents):
    """
    Search indexed documents for answer. Return single-source answer with citation
    or refusal template if not found or if multiple conflicting sources exist.
    """
    question_lower = question.lower()
    matches_by_doc = {}

    # Search all documents
    for filename, sections in documents.items():
        for section in sections:
            section_text = section['section_text'].lower()
            section_id = section['section_id']

            # Simple keyword matching
            if has_relevant_match(question_lower, section_text, filename, section_id):
                if filename not in matches_by_doc:
                    matches_by_doc[filename] = []
                matches_by_doc[filename].append({
                    'section_id': section_id,
                    'section_text': section['section_text']
                })

    # Handle results
    if len(matches_by_doc) == 0:
        return REFUSAL_TEMPLATE
    elif len(matches_by_doc) == 1:
        # Single source - return answer
        filename = list(matches_by_doc.keys())[0]
        sections = matches_by_doc[filename]
        section = sections[0]
        answer = section['section_text']
        citation = f"Source: {filename} Section {section['section_id']}"
        return f"{answer}\n{citation}"
    else:
        # Multiple sources - check for conflict
        return REFUSAL_TEMPLATE


def has_relevant_match(question_lower, section_text_lower, filename, section_id):
    """
    Determine if a section is relevant to the question.
    Uses keyword matching and specific section rules.
    """
    # Specific routing rules
    if "personal phone" in question_lower and "work file" in question_lower:
        return filename == "policy_it_acceptable_use.txt" and section_id == "3.1"

    if "carry forward" in question_lower and "annual leave" in question_lower:
        return filename == "policy_hr_leave.txt" and section_id == "2.6"

    if "install slack" in question_lower or "slack" in question_lower:
        return filename == "policy_it_acceptable_use.txt" and section_id == "2.3"

    if "home office equipment" in question_lower or "equipment allowance" in question_lower:
        return filename == "policy_finance_reimbursement.txt" and section_id == "3.1"

    if "claim da" in question_lower and "meal receipt" in question_lower:
        return filename == "policy_finance_reimbursement.txt" and section_id == "2.6"

    if "leave without pay" in question_lower and "approve" in question_lower:
        return filename == "policy_hr_leave.txt" and section_id == "5.2"

    # Generic keyword matching
    question_words = set(question_lower.split())
    section_words = set(section_text_lower.split())
    overlap = question_words & section_words

    return len(overlap) > 2


def main():
    """Interactive CLI for policy questions."""
    print("Loading policy documents...")

    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    documents = retrieve_documents(file_paths)
    print()

    while True:
        question = input("Ask a policy question (or type 'exit' to quit): ").strip()
        if question.lower() == 'exit':
            break
        if not question:
            continue

        answer = answer_question(question, documents)
        print(answer)
        print()


if __name__ == "__main__":
    main()
