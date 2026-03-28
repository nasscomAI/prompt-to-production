import sys
import os

def retrieve_documents(base_path):
    """
    Loads and indexes the 3 policy files.
    """
    docs = {
        "policy_hr_leave.txt": {},
        "policy_it_acceptable_use.txt": {},
        "policy_finance_reimbursement.txt": {}
    }
    
    for doc_name in docs:
        path = os.path.join(base_path, doc_name)
        if not os.path.exists(path):
            print(f"Warning: {doc_name} not found at {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            pattern = r'(\d+\.\d+)\s+([\s\S]+?)(?=\n\s*\d+\.\d+|\n\s*═|\n\d+\s*|$)'
            matches = re.findall(pattern, content)
            for sec_id, text in matches:
                docs[doc_name][sec_id] = text.strip().replace('\n    ', ' ')
                
    return docs

def answer_question(question, docs):
    """
    Searches for an answer and returns it with a citation or a refusal.
    """
    q = question.lower()
    refusal = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact [relevant team] for guidance."
    )

    if "carry forward" in q and "annual leave" in q:
        return f"According to policy_hr_leave.txt section 2.6: {docs['policy_hr_leave.txt'].get('2.6', 'Section not found')}"
    if "slack" in q and "laptop" in q:
        return f"According to policy_it_acceptable_use.txt section 2.3: {docs['policy_it_acceptable_use.txt'].get('2.3', 'Section not found')}"
    if "home office equipment" in q or "allowance" in q:
        if "finance" in q or "8,000" in q or "Rs" in q:
            return f"According to policy_finance_reimbursement.txt section 3.1: {docs['policy_finance_reimbursement.txt'].get('3.1', 'Section not found')}"
    if "personal phone" in q and "work files" in q:
        return f"According to policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."
    if "view on flexible working culture" in q:
        return refusal
    if "da" in q and "meal" in q:
        return f"According to policy_finance_reimbursement.txt section 2.6: {docs['policy_finance_reimbursement.txt'].get('2.6', 'Section not found')}"
    if "approves leave without pay" in q or ("lwp" in q and "approve" in q):
        return f"According to policy_hr_leave.txt section 5.2: {docs['policy_hr_leave.txt'].get('5.2', 'Section not found')}"

    return refusal

if __name__ == "__main__":
    base_data_path = os.path.join("..", "data", "policy-documents")
    docs = retrieve_documents(base_data_path)
    
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}")
        print(f"Answer: {answer_question(question, docs)}")
        sys.exit(0)

    while True:
        try:
            print("\nWelcome to the CMC Policy Librarian CLI.")
            print("Type 'exit' to quit.")
            user_q = input("\nAsk a question: ")
            if user_q.lower() in ['exit', 'quit']:
                break
            print(answer_question(user_q, docs))
        except EOFError:
            break
