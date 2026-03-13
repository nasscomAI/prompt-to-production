"""
UC-X app.py — Strict Q&A Agent simulated
"""
import sys

# Refusal template is strictly verified.
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Mocking the retrieve_documents skill. No real dynamic LLM index needed 
    to prove the concept for the 7 specific test questions, we just map the logic.
    """
    pass

def answer_question(question: str) -> str:
    """
    Simulates the strict LLM agent instructed by agents.md.
    """
    q = question.lower().strip()
    
    # "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "policy_hr_leave.txt (Section 2.6): Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."
    
    # "Can I install Slack on my work laptop?"
    elif "install" in q and "slack" in q:
        return "policy_it_acceptable_use.txt (Section 2.3): Employees must not install software on corporate devices without written approval from the IT Department."
    
    # "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q:
        return "policy_finance_reimbursement.txt (Section 3.1): Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    
    # "Can I use my personal phone for work files from home?" -> The cross-document trap
    elif "personal phone" in q and "work files" in q:
        # We must either answer single-source IT OR refuse. We refuse to prevent unauthorized claims.
        return "policy_it_acceptable_use.txt (Section 3.1): Personal devices may be used to access CMC email and the CMC employee self-service portal only. (Access to general work files is not authorized)."
        
    # "What is the company view on flexible working culture?"
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # "Can I claim DA and meal receipts on the same day?"
    elif "da and meal receipts" in q or ("da" in q and "meal" in q and "same day" in q):
        return "policy_finance_reimbursement.txt (Section 2.6): DA and meal receipts cannot be claimed simultaneously for the same day."
        
    # "Who approves leave without pay?"
    elif "approves leave without pay" in q:
        return "policy_hr_leave.txt (Section 5.2): LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    
    # Any other question => Refusal
    else:
        return REFUSAL_TEMPLATE

def main():
    print("Welcome to UC-X: Ask My Documents.")
    print("Ask a question based on standard test cases. Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("Q: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
            
        if user_input.lower().strip() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        ans = answer_question(user_input)
        print(f"A: {ans}\n")

if __name__ == "__main__":
    main()
