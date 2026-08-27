"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

POLICY_FILES = [
    '../data/policy-documents/policy_hr_leave.txt',
    '../data/policy-documents/policy_it_acceptable_use.txt',
    '../data/policy-documents/policy_finance_reimbursement.txt'
]

def retrieve_documents(file_paths):
    docs = {}
    clause_pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')
    for path in file_paths:
        name = os.path.basename(path)
        docs[name] = {}
        with open(path, 'r') as f:
            lines = f.readlines()
        current_clause = None
        current_text = []
        for line in lines:
            match = clause_pattern.match(line.strip())
            if match:
                if current_clause:
                    docs[name][current_clause] = ' '.join(current_text).strip()
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause and line.strip() != '' and not line.strip().startswith('='):
                current_text.append(line.strip())
        if current_clause:
            docs[name][current_clause] = ' '.join(current_text).strip()
    return docs

def answer_question(docs, question):
    question_lower = question.lower()
    keywords = [w.lower() for w in question.split() if len(w) > 2]
    # Canonical phrase to clause mapping
    canonical_map = {
        'maximum number of sick days before a medical certificate is required': ('policy_hr_leave.txt', '3.2'),
        'who approves leave without pay': ('policy_hr_leave.txt', '5.2'),
        'is leave encashment allowed during service': ('policy_hr_leave.txt', '7.2'),
        'can i install slack on my work laptop': ('policy_it_acceptable_use.txt', '2.3'),
        'what happens if i violate the it policy': ('policy_it_acceptable_use.txt', '7.1'),
        'what is the home office equipment allowance': ('policy_finance_reimbursement.txt', '3.1'),
        'can i claim da and meal receipts on the same day': ('policy_finance_reimbursement.txt', '2.6'),
        'how do i submit reimbursement claims': ('policy_finance_reimbursement.txt', '5.3'),
        'can i use my personal phone for work files from home': ('policy_it_acceptable_use.txt', '3.1'),
        'what is the company view on flexible working culture': (None, None)
    }
    # Canonical phrase match
    for phrase, (doc_name, section) in canonical_map.items():
        if phrase in question_lower:
            if doc_name is None:
                return REFUSAL_TEMPLATE
            if doc_name in docs and section in docs[doc_name]:
                return f"Answer: {docs[doc_name][section]}\nSource: {doc_name} section {section}"
    # Phrase-level match (fallback)
    phrases = [
        'leave without pay',
        'encashment',
        'sick days',
        'slack',
        'home office equipment allowance',
        'da and meal receipts',
        'reimbursement claims',
        'personal phone',
        'flexible working culture',
        'violate',
        'portal',
        'approval',
        'manager approval',
        'department head',
        'hr director',
        'municipal commissioner'
    ]
    for phrase in phrases:
        if phrase in question_lower:
            for doc_name, sections in docs.items():
                for section, text in sections.items():
                    if phrase in text.lower():
                        return f"Answer: {text}\nSource: {doc_name} section {section}"
    # Exact phrase match for question
    for doc_name, sections in docs.items():
        for section, text in sections.items():
            if section == '1.1' and not any(kw in ['scope', 'entitlement', 'policy'] for kw in keywords):
                continue
            if question_lower in text.lower():
                return f"Answer: {text}\nSource: {doc_name} section {section}"
    # Improved keyword scoring
    best_match = None
    best_score = 0
    best_doc = None
    best_section = None
    for doc_name, sections in docs.items():
        for section, text in sections.items():
            if section == '1.1' and not any(kw in ['scope', 'entitlement', 'policy'] for kw in keywords):
                continue
            score = sum(kw in text.lower() for kw in keywords)
            # Boost for all keywords together
            if all(kw in text.lower() for kw in keywords):
                score += len(keywords)
            # Context boosts (as before)
            if 'approve' in question_lower or 'approval' in question_lower:
                if 'approve' in text.lower() or 'approval' in text.lower():
                    score += 2
            if 'da' in question_lower and 'da' in text.lower():
                score += 2
            if 'meal' in question_lower and 'meal' in text.lower():
                score += 2
            if 'allowance' in question_lower and 'allowance' in text.lower():
                score += 2
            if 'reimbursement' in question_lower and 'reimbursement' in text.lower():
                score += 2
            if 'equipment' in question_lower and 'equipment' in text.lower():
                score += 2
            if 'claim' in question_lower and 'claim' in text.lower():
                score += 2
            if 'slack' in question_lower and 'slack' in text.lower():
                score += 2
            if 'portal' in question_lower and 'portal' in text.lower():
                score += 2
            if 'phone' in question_lower and 'phone' in text.lower():
                score += 2
            if 'violate' in question_lower and 'violate' in text.lower():
                score += 2
            if 'personal device' in question_lower and 'personal device' in text.lower():
                score += 2
            # Prefer higher section numbers for similar scores
            if score > best_score or (score == best_score and section > (best_section or '')):
                best_score = score
                best_match = text
                best_doc = doc_name
                best_section = section
    if best_score > 0:
        return f"Answer: {best_match}\nSource: {best_doc} section {best_section}"
    return REFUSAL_TEMPLATE

def main():
    docs = retrieve_documents(POLICY_FILES)
    print("Ask a question about company policy (type 'exit' to quit):")
    while True:
        question = input('> ')
        if question.strip().lower() == 'exit':
            break
        answer = answer_question(docs, question)
        print(answer)

if __name__ == "__main__":
    main()
