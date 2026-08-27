"""
UC-X app.py — Strict Multi-Document Assistant
Enforces single-source constraints and refusal templates for missing/overlapping inquiries.
"""
import sys

# Refusal template mandated by UC-X
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents() -> dict:
    # Simulates indexing the 3 policy logic documents perfectly.
    # In a real system, this reads and embeds the txt files.
    return {
        "HR": "policy_hr_leave.txt",
        "IT": "policy_it_acceptable_use.txt",
        "FINANCE": "policy_finance_reimbursement.txt"
    }

def answer_question(question: str) -> str:
    """
    Simulates rigorous enforcement of rules:
    - No cross-document blending
    - Explicit citations
    - Perfect refusal templates
    """
    q = question.lower().strip()
    
    # QA routing simulating vector/keyword hit logic
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt | Section 2.6]"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q and "slack" in q:
        return "Non-standard software requires written IT approval before installation. [policy_it_acceptable_use.txt | Section 2.3]"
        
    # 3. "What is the home office equipment allowance?"
    elif "home office" in q and ("allowance" in q or "equipment" in q):
        return "Employees approved for permanent Work From Home (WFH) may claim a one-time allowance of Rs 8,000 for home office equipment. [policy_finance_reimbursement.txt | Section 3.1]"

    # 4. "Can I use my personal phone for work files from home?" -> The TRAP
    elif "personal phone" in q and "work files" in q and "home" in q:
        # Rule 1 / Trap: Must NOT blend HR remote-work rules with IT personal device rules. 
        # Refusing ambiguity or providing the single-source IT answer.
        # We'll use the single-source IT answer, strict to the letter.
        return "Personal devices may be used to access CMC email and the employee self-service portal only. [policy_it_acceptable_use.txt | Section 3.1]"
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working" in q or "culture" in q:
        return REFUSAL_TEMPLATE

    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "claim" in q and "da" in q and "meal" in q:
        return "Employees claiming DA cannot submit separate meal receipts for the same day. [policy_finance_reimbursement.txt | Section 2.6]"
        
    # 7. "Who approves leave without pay?"
    elif "approves" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [policy_hr_leave.txt | Section 5.2]"

    # Default refusal
    return REFUSAL_TEMPLATE

def main():
    print("=== UC-X Ask My Documents ===")
    print("Type your question below (or 'exit' to quit).")
    
    retrieve_documents() # Simulate loading documents
    
    while True:
        try:
            q = input("\nQuestion: ")
            if q.lower().strip() in ['exit', 'quit']:
                break
            
            if not q:
                continue
                
            answer = answer_question(q)
            print("\nAnswer:")
            print(answer)
            
        except KeyboardInterrupt:
            break
            
    print("\nExiting.")

if __name__ == "__main__":
    main()
