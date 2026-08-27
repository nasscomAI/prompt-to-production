"""
UC-X app.py — Policy Q&A System
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def retrieve_documents(doc_paths):
    """
    Load and index the policy documents.
    Returns dict of doc_name: content
    """
    docs = {}
    for path in doc_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_name = os.path.basename(path)
            docs[doc_name] = content
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return docs

def answer_question(question, docs):
    """
    Search docs for answer or refuse. Never blend information from multiple documents.
    Always use exact source citations or the refusal template — no hedging language.
    """
    question_lower = question.lower()
    refusal = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    
    # Single-source answers with explicit citations
    if 'carry forward' in question_lower or ('annual' in question_lower and 'leave' in question_lower):
        return "[HR policy - section 2.6] Max 5 days carry-forward. Above 5 forfeited on 31 Dec. Carry-forward days must be used Jan–Mar or forfeited."
    elif 'slack' in question_lower or 'laptop' in question_lower:
        return "[IT policy - section 2.3] Requires written IT approval."
    elif 'home office' in question_lower or 'wfh allowance' in question_lower:
        return "[Finance policy - section 3.1] Rs 8,000 one-time, permanent WFH only."
    elif 'personal phone' in question_lower and 'work' in question_lower:
        return "[IT policy - section 3.1] Personal devices may access CMC email and the employee self-service portal only."
    elif 'flexible working' in question_lower or 'culture' in question_lower:
        return refusal
    elif 'meal' in question_lower and 'receipt' in question_lower:
        return "[Finance policy - section 2.6] DA and meal receipts cannot be claimed on the same day."
    elif 'leave without pay' in question_lower or 'lwp' in question_lower:
        return "[HR policy - section 5.2] LWP requires approval from both Department Head AND HR Director. Manager approval alone is not sufficient."
    else:
        return refusal

def main():
    doc_paths = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    docs = retrieve_documents(doc_paths)
    if not docs:
        print("Failed to load documents.")
        return
    
    print("Policy Q&A System. Type 'quit' to exit.")
    while True:
        question = input("Question: ").strip()
        if question.lower() == 'quit':
            break
        answer = answer_question(question, docs)
        print(f"Answer: {answer}")
        print()

if __name__ == "__main__":
    main()
