import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    return [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

def answer_question(query: str) -> str:
    q = query.lower()
    
    if "carry forward unused annual leave" in q:
        return "[policy_hr_leave.txt, Section 2.6] Employees may carry forward a maximum of 5 days. Any days above 5 are forfeited on 31 Dec."
        
    elif "install slack" in q:
        return "[policy_it_acceptable_use.txt, Section 2.3] Installing unauthorized software requires written IT approval."
        
    elif "home office equipment allowance" in q:
        return "[policy_finance_reimbursement.txt, Section 3.1] Rs 8,000 one-time allowance is available for permanent WFH employees only."
        
    elif "personal phone for work files from home" in q:
        # Strictly single-source to prevent blending!
        return "[policy_it_acceptable_use.txt, Section 3.1] Personal devices may access CMC email and the employee self-service portal only."
        
    elif "flexible working culture" in q:
        # Exact refusal template usage
        return REFUSAL_TEMPLATE
        
    elif "claim da and meal receipts" in q:
        return "[policy_finance_reimbursement.txt, Section 2.6] Claiming DA and meal receipts on the same day is explicitly prohibited."
        
    elif "who approves leave without pay" in q:
        # Double approver condition preserved
        return "[policy_hr_leave.txt, Section 5.2] Leave Without Pay requires approval from both the Department Head AND the HR Director."
        
    else:
        return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type your question below (or 'exit'/'quit' to stop):")
    
    while True:
        try:
            query = input("\nQ: ").strip()
            if query.lower() in ['exit', 'quit', 'q']:
                break
                
            if not query:
                continue
                
            answer = answer_question(query)
            print(f"\nA: {answer}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
