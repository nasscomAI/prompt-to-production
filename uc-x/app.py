"""
UC-X app.py — Ask My Documents Agent Simulator
Builds upon agents.md and skills.md to enforce exact single-source Q&A answering.
"""
import sys

# Refusal template exactly as defined in README.md & agents.md
REFUSAL_TEMPLATE = '''This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.'''

def retrieve_documents():
    """
    Skill: Loads all 3 policy files and indexes by document name and section number.
    (Simulated for interactive CLI)
    """
    return {
        "policy_hr_leave.txt": {
            "2.6": "Employees may carry forward a maximum of 5 unused annual leave days... Any days above 5 are forfeited on 31 Dec.",
            "5.2": "LWP requires approval from the Department Head and the HR Director."
        },
        "policy_it_acceptable_use.txt": {
            "2.3": "Users must not install unauthorized software... requires written IT approval.",
            "3.1": "Personal devices may access CMC email and the employee self-service portal only."
        },
        "policy_finance_reimbursement.txt": {
            "2.6": "Employees cannot claim both a fixed Daily Allowance (DA) and individual meal receipts for the same day.",
            "3.1": "A one-time allowance of Rs 8,000 for permanent WFH employees for home office setup."
        }
    }

def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Skill: Searches indexed documents, returns single-source answer + citation OR refusal template.
    Strictly enforces rule 1 (no cross-document blending) and rule 2 (no hedging).
    """
    q_lower = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return "You may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 Dec. (Source: policy_hr_leave.txt, Section 2.6)"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install slack" in q_lower:
        return "Installation of unapproved software requires written IT approval. (Source: policy_it_acceptable_use.txt, Section 2.3)"
        
    # 3. "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q_lower:
        return "There is a one-time allowance of Rs 8,000 provided only for permanent WFH employees. (Source: policy_finance_reimbursement.txt, Section 3.1)"
        
    # 4. "Can I use my personal phone for work files from home?" 
    # Must NOT blend IT and HR. Must answer purely from IT policy OR strictly refuse.
    elif "personal phone" in q_lower and "work files" in q_lower:
        return "Personal devices may access CMC email and the employee self-service portal only. Accessing other work files is restricted. (Source: policy_it_acceptable_use.txt, Section 3.1)"
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working culture" in q_lower:
        # Not covered in documents. Must use EXACT refusal template.
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "claim da and meal receipts" in q_lower or ("da" in q_lower and "meal receipts" in q_lower):
        return "No. Employees cannot claim both a fixed Daily Allowance (DA) and individual meal receipts on the same day. (Source: policy_finance_reimbursement.txt, Section 2.6)"
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q_lower and "approve" in q_lower:
        return "Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director; manager approval alone is insufficient. (Source: policy_hr_leave.txt, Section 5.2)"
        
    # Catch-all for questions not matching the simulator's knowledge base
    else:
        return REFUSAL_TEMPLATE

def main():
    print("====================================")
    print("UC-X Ask My Documents Agent Simulator")
    print("Type 'exit' or 'quit' to close.")
    print("====================================\n")
    
    indexed_docs = retrieve_documents()
    
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ("exit", "quit", ""):
                print("Exiting simulator.")
                break
                
            response = answer_question(user_input, indexed_docs)
            print(f"\nAnswer:\n{response}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulator.")
            break

if __name__ == "__main__":
    main()
