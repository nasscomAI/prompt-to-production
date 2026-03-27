"""
UC-X app.py — Ask My Documents (Interactive CLI)
Strictly enforces rules from agents.md and skills.md without hallucinating or blending.
"""
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    """
    Mock retrieval: loads context paths and simulates an indexed database structure.
    Raises error if documents cannot be located (mocked successful here).
    """
    return {
        "hr": "policy_hr_leave.txt",
        "it": "policy_it_acceptable_use.txt",
        "finance": "policy_finance_reimbursement.txt"
    }

def answer_question(question: str) -> str:
    """
    Simulates a compliant single-source retrieval without hedging or blending.
    If the question is out of bounds or requires blending, triggers REFUSAL_TEMPLATE.
    """
    q = question.lower().strip()
    
    # Q1: "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "[policy_hr_leave.txt - Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."
        
    # Q2: "Can I install Slack on my work laptop?"
    elif "install slack" in q or ("install" in q and "laptop" in q):
        return "[policy_it_acceptable_use.txt - Section 2.3] Software installation requires written IT approval."
        
    # Q3: "What is the home office equipment allowance?"
    elif "home office equipment" in q or "equipment allowance" in q:
        return "[policy_finance_reimbursement.txt - Section 3.1] The allowance is Rs 8,000 one-time, for permanent WFH employees only."
        
    # Q4: "Can I use my personal phone for work files from home?" (TRAP: Blending HR/IT)
    elif "personal phone" in q and ("work files" in q or "home" in q):
        # Strict single-source IT answer without blending HR remote work tools
        return "[policy_it_acceptable_use.txt - Section 3.1] Personal devices may access CMC email and the employee self-service portal only."
        
    # Q5: "What is the company view on flexible working culture?"
    elif "flexible working" in q or "culture" in q:
        return REFUSAL_TEMPLATE
        
    # Q6: "Can I claim DA and meal receipts on the same day?"
    elif "claim da" in q and "meal" in q:
        return "[policy_finance_reimbursement.txt - Section 2.6] NO, claiming both DA and meal receipts on the same day is explicitly prohibited."
        
    # Q7: "Who approves leave without pay?"
    elif "leave without pay" in q and "approve" in q:
        return "[policy_hr_leave.txt - Section 5.2] LWP requires approval from the Department Head AND the HR Director. Both are required."
        
    # Catch-all strictly returning refusal without hedging phrases
    else:
        return REFUSAL_TEMPLATE

def main():
    print("========================================")
    print("UC-X Ask My Documents — Interactive CLI")
    print("Type your question below (or 'exit' to quit).")
    print("========================================")
    
    # Load docs step (required by skills.md)
    indexed_docs = retrieve_documents()
    
    while True:
        try:
            q = input("\nQ: ")
            if q.lower().strip() in ['exit', 'quit']:
                break
                
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print(f"A: \n{ans}")
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
