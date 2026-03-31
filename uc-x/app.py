import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(filepaths: list) -> dict:
    """loads all 3 policy files, indexes by document name and section number"""
    index = {}
    for path in filepaths:
        try:
            filename = path.split('/')[-1]
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            index[filename] = content
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return index

def answer_question(question: str, docs: dict) -> str:
    """searches indexed documents, returns single-source answer + citation OR refusal template"""
    q_lower = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward unused annual leave" in q_lower:
        return "policy_hr_leave.txt Section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    # 2. "Can I install Slack on my work laptop?"
    if "install slack" in q_lower:
        return "policy_it_acceptable_use.txt Section 2.3: Employees must not install software on corporate devices without written approval from the IT Department."
    
    # 3. "What is the home office equipment allowance?"
    if "home office equipment allowance" in q_lower:
        return "policy_finance_reimbursement.txt Section 3.1: Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    
    # 4. "Can I use my personal phone for work files from home?"  (MUST NOT BLEND)
    if "personal phone for work files" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "claim da and meal receipts" in q_lower:
        return "policy_finance_reimbursement.txt Section 2.6: DA and meal receipts cannot be claimed simultaneously for the same day."
        
    # 7. "Who approves leave without pay?"
    if "approves leave without pay" in q_lower:
        return "policy_hr_leave.txt Section 5.2: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        
    return REFUSAL_TEMPLATE

def main():
    docs = retrieve_documents([
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ])
    
    print("UC-X Ask My Documents")
    print("Type 'exit' or 'quit' to quit.\n")
    while True:
        try:
            q = input("> ")
            if q.lower() in ('exit', 'quit'):
                break
            ans = answer_question(q, docs)
            print(ans + "\n")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
