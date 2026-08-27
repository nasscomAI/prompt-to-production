"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    ("policy_hr_leave.txt", "data/policy-documents/policy_hr_leave.txt"),
    ("policy_it_acceptable_use.txt", "data/policy-documents/policy_it_acceptable_use.txt"),
    ("policy_finance_reimbursement.txt", "data/policy-documents/policy_finance_reimbursement.txt"),
]

def retrieve_document(file_path):
    """
    Loads a policy document and returns its content as a list of sections (dicts).
    """
    with open(file_path, encoding='utf-8') as f:
        text = f.read()
    # Split into sections by lines of all ═ or by numbered clauses
    sections = []
    # Try numbered clauses first
    clause_pattern = re.compile(r'^(\d+\.\d+) (.+?)(?=^\d+\.\d+ |^\Z)', re.MULTILINE | re.DOTALL)
    matches = clause_pattern.findall(text)
    if matches:
        for clause, clause_text in matches:
            sections.append({'clause': clause, 'text': clause_text.strip()})
    else:
        # Fallback: split by section headers
        for part in re.split(r'\n═+\n', text):
            part = part.strip()
            if part:
                sections.append({'section': part[:40], 'text': part})
    return sections

def answer_question(question, documents):
    """
    Answers a question using only the content of a single policy document.
    Cites document and clause if present, or returns the refusal template.
    """
    q_lower = question.lower()
    for doc_name, sections in documents.items():
        for section in sections:
            # Search for relevant answer (simple keyword match)
            if q_lower in section['text'].lower():
                ref = section.get('clause') or section.get('section') or 'section'
                return f"[{doc_name} {ref}] {section['text']}"
            # Try to match by keywords in question
            q_words = [w for w in re.findall(r'\w+', q_lower) if len(w) > 2]
            if any(w in section['text'].lower() for w in q_words):
                ref = section.get('clause') or section.get('section') or 'section'
                return f"[{doc_name} {ref}] {section['text']}"
    # If not found in any document, return refusal template
    return REFUSAL_TEMPLATE

def main():
    # Load all documents
    documents = {}
    for doc_name, file_path in DOC_PATHS:
        try:
            documents[doc_name] = retrieve_document(file_path)
        except Exception as e:
            print(f"Error loading {doc_name}: {e}")
            return
    print("UC-X Document QA System\nType your question (or 'exit' to quit):")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("exit", "quit"): break
        if not question:
            print("Please enter a question.")
            continue
        answer = answer_question(question, documents)
        print(f"\n{answer}")

if __name__ == "__main__":
    main()
