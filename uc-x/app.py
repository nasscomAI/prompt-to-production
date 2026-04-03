"""
UC-X — Ask My Documents
Interactive CLI for policy questions.
"""
import os
import re
import csv

POLICY_FILES = {
    'policy_hr_leave.txt': '../data/policy-documents/policy_hr_leave.txt',
    'policy_it_acceptable_use.txt': '../data/policy-documents/policy_it_acceptable_use.txt',
    'policy_finance_reimbursement.txt': '../data/policy-documents/policy_finance_reimbursement.txt'
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: dict) -> dict:
    """Load all policy files, index by document name and section number."""
    documents = {}
    for doc_name, file_path in file_paths.items():
        sections = {}
        full_text = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                full_text.append(content)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
            continue
        
        lines = content.split('\n')
        for line in lines:
            match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
            if match:
                sections[match.group(1)] = match.group(2)
        
        documents[doc_name] = {'sections': sections, 'full_text': '\n'.join(full_text)}
    
    return documents

def answer_question(documents: dict, question: str) -> str:
    """Search indexed documents, return single-source answer or refusal."""
    question_lower = question.lower()
    
    keywords = {
        'policy_hr_leave.txt': ['leave', 'annual', 'sick', 'maternity', 'paternity', 'lwp', 'carry forward', 'encashment', 'holiday', 'approval'],
        'policy_it_acceptable_use.txt': ['device', 'phone', 'laptop', 'software', 'install', 'password', 'email', 'access', 'network', 'personal'],
        'policy_finance_reimbursement.txt': ['claim', 'reimburse', 'travel', 'equipment', 'allowance', 'da', 'meal', 'home office']
    }
    
    scored_docs = []
    for doc_name, kw_list in keywords.items():
        if doc_name in documents:
            score = sum(1 for kw in kw_list if kw in question_lower)
            if score > 0:
                scored_docs.append((doc_name, score))
    
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    if not scored_docs:
        return REFUSAL_TEMPLATE
    
    best_doc = scored_docs[0][0]
    doc_data = documents[best_doc]
    
    hr_keywords = {
        'policy_hr_leave.txt': {
            'carry forward': ['2.6', '2.7'],
            'annual leave': ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7'],
            'sick leave': ['3.1', '3.2', '3.3', '3.4'],
            'leave without pay': ['5.2'],
            'encashment': ['7.1', '7.2', '7.3'],
            'approve': ['2.4', '5.2', '5.3']
        },
        'policy_it_acceptable_use.txt': {
            'install': ['2.3'],
            'device': ['2.1', '2.2', '2.3', '2.4', '3.1', '3.2', '3.3'],
            'personal phone': ['3.1', '3.2', '3.3'],
            'email': ['3.1', '3.4'],
            'password': ['4.1', '4.2', '4.3']
        },
        'policy_finance_reimbursement.txt': {
            'equipment': ['3.1', '3.2', '3.3', '3.4', '3.5'],
            'allowance': ['3.1', '5.1', '5.2'],
            'home office': ['3.1', '3.5', '5.2'],
            'da': ['2.5', '2.6'],
            'meal': ['2.5', '2.6'],
            'claim': ['2.6', '3.4', '6.1', '6.2']
        }
    }
    
    if best_doc in hr_keywords:
        for phrase, sections in hr_keywords[best_doc].items():
            if phrase in question_lower:
                for sec in sections:
                    if sec in doc_data['sections']:
                        content = doc_data['sections'][sec]
                        return f"[{best_doc} Section {sec}]\n{content}"
    
    return REFUSAL_TEMPLATE

def main():
    print("=" * 60)
    print("UC-X — Policy Document Q&A")
    print("Available: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    documents = retrieve_documents(POLICY_FILES)
    
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ('quit', 'exit', 'q'):
            break
        if not question:
            continue
        
        answer = answer_question(documents, question)
        print(f"\n{answer}")

if __name__ == "__main__":
    main()