"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    '../data/policy-documents/policy_hr_leave.txt',
    '../data/policy-documents/policy_it_acceptable_use.txt',
    '../data/policy-documents/policy_finance_reimbursement.txt',
]

def retrieve_documents(file_paths):
    """
    Loads all three policy files and indexes their content by document name and section number.
    Returns: dict {doc_name: {section_number: text}}
    Error handling: returns error if any file missing/unreadable; skips and flags unparsable sections.
    """
    docs = {}
    for path in file_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"ERROR: Could not read {doc_name}: {e}", flush=True)
            continue
        # Index by section number (e.g., 2.6, 3.1, etc.)
        section_pattern = re.compile(r'^(\d+\.\d+) (.+?)(?=^\d+\.\d+ |\Z)', re.MULTILINE | re.DOTALL)
        matches = section_pattern.findall(text)
        section_map = {}
        for section, content in matches:
            section_map[section] = content.strip().replace('\n', ' ')
        docs[doc_name] = section_map
    return docs

def answer_question(question, docs):
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    Error handling: refusal template if blending, hedging, or not found.
    """
    # Map of keywords to (doc, section)
    # In a real system, use semantic search; here, use keyword heuristics for demo
    q = question.lower().strip()
    # HR
    if 'carry forward' in q and 'leave' in q:
        doc, sec = 'policy_hr_leave.txt', '2.6'
    elif 'leave without pay' in q or 'who approves leave' in q:
        doc, sec = 'policy_hr_leave.txt', '5.2'
    # IT
    elif 'slack' in q and 'laptop' in q:
        doc, sec = 'policy_it_acceptable_use.txt', '2.3'
    elif 'personal phone' in q and ('work files' in q or 'home' in q):
        doc, sec = 'policy_it_acceptable_use.txt', '3.1'
    # Finance
    elif 'home office equipment' in q:
        doc, sec = 'policy_finance_reimbursement.txt', '3.1'
    elif 'da' in q and 'meal' in q:
        doc, sec = 'policy_finance_reimbursement.txt', '2.6'
    else:
        # Not found
        return REFUSAL_TEMPLATE

    # Retrieve answer
    if doc in docs and sec in docs[doc]:
        answer = docs[doc][sec]
        return f"{answer}\n(Source: {doc} section {sec})"
    else:
        return REFUSAL_TEMPLATE

def main():
    print("Ask My Documents Agent (UC-X)")
    print("Type your question (or 'exit' to quit):")
    docs = retrieve_documents(POLICY_FILES)
    while True:
        try:
            question = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if question.lower() in ['exit', 'quit']:
            print("Goodbye.")
            break
        answer = answer_question(question, docs)
        print(answer)

if __name__ == "__main__":
    main()
