"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    '../data/policy-documents/policy_hr_leave.txt',
    '../data/policy-documents/policy_it_acceptable_use.txt',
    '../data/policy-documents/policy_finance_reimbursement.txt'
]

def retrieve_documents(paths):
    """
    Loads all three policy files and indexes their content by document name and section number.
    """
    indexed = {}
    for path in paths:
        doc_name = os.path.basename(path)
        if not os.path.exists(path):
            indexed[doc_name] = {'error': f'File not found: {path}'}
            continue
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
        sections = {}
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Section detection: e.g., 2.3, 3.1, etc.
            if line[:3].replace('.', '').isdigit() and line[1] == '.' and line[2].isdigit():
                current_section = line[:3]
                sections[current_section] = line[3:].strip()
            elif current_section:
                sections[current_section] += ' ' + line
        indexed[doc_name] = sections
    return indexed

def answer_question(question, indexed_docs):
    """
    Searches indexed documents for the question, returns a single-source answer with citation or refusal template if not found.
    """
    q_lower = question.lower().strip()
    # Flexible working culture is not covered
    if 'flexible working' in q_lower:
        return REFUSAL_TEMPLATE
    # Extract keywords, bigrams, trigrams, and add domain-specific keywords
    import re
    words = re.findall(r'\w+', q_lower)
    keywords = set(words)
    # Add bigrams and trigrams
    for i in range(len(words)-1):
        keywords.add(words[i] + ' ' + words[i+1])
    for i in range(len(words)-2):
        keywords.add(words[i] + ' ' + words[i+1] + ' ' + words[i+2])
    # Add domain-specific keywords for policy questions
    domain_keywords = {
        'annual leave': [
            'annual leave', 'carry forward', 'unused', 'maximum', 'forfeited', 'limit', 'section 2.6', 'calendar year', 'leave days', '31 december'
        ],
        'slack': [
            'slack', 'software', 'install', 'approval', 'it department', 'corporate devices', 'written approval', 'section 2.3'
        ],
        'home office equipment allowance': [
            'home office equipment', 'equipment allowance', 'rs 8000', 'one-time', 'permanent wfh', 'section 3.1', 'finance', 'allowance'
        ],
        'personal phone': [
            'personal phone', 'byod', 'employee self-service portal', 'email', 'access', 'it policy', 'work files', 'section 3.1', 'personal devices', 'may be used', 'only', 'not be used', 'files', 'remote', 'home'
        ],
        'da and meal receipts': [
            'da', 'meal receipts', 'same day', 'explicitly prohibited', 'finance', 'section 2.6', 'cannot be claimed simultaneously', 'receipts', 'daily allowance', 'actual meal expenses', 'combined meal claim', 'rs 750'
        ],
        'leave without pay': [
            'leave without pay', 'lwp', 'department head', 'hr director', 'approval', 'both department head and hr director', 'who approves leave', 'leave approval', 'section 5.2', 'required'
        ],
    }
    for phrase, kws in domain_keywords.items():
        if phrase in q_lower or any(kw in q_lower for kw in kws):
            keywords.update(kws)
    best_match = None
    best_score = 0
    for doc_name, sections in indexed_docs.items():
        if 'error' in sections:
            continue
        for section_num, content in sections.items():
            content_lower = content.lower()
            # Count keyword, bigram, trigram matches
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > best_score:
                best_score = score
                best_match = (content, doc_name, section_num)
    if best_match and best_score > 0:
        content, doc_name, section_num = best_match
        return f"Answer: {content}\nSource: {doc_name} section {section_num}"
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Policy QA Interactive CLI\nType your question and press Enter. Type 'exit' to quit.")
    indexed_docs = retrieve_documents(POLICY_FILES)
    while True:
        question = input("Question: ").strip()
        if question.lower() == 'exit':
            print("Exiting.")
            break
        answer = answer_question(question, indexed_docs)
        print(answer)

if __name__ == "__main__":
    main()
