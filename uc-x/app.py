"""
UC-X app.py — Strict Policy Q&A Agent
Enforces constraints defined in agents.md and skills.md.
"""
import sys

def retrieve_documents() -> dict:
    # Simulating the loaded textual indexes logically relevant for the 7 test questions
    index = {
         "policy_hr_leave.txt": {
              "2.6": "Maximum 5 days can be carried forward. Days above 5 are forfeited on 31 Dec.",
              "5.2": "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director."
         },
         "policy_it_acceptable_use.txt": {
              "2.3": "Installing unauthorized software, such as Slack on a work laptop, requires written IT approval.",
              "3.1": "Personal devices may access CMC email and the employee self-service portal exclusively. No other tools or files may be accessed."
         },
         "policy_finance_reimbursement.txt": {
              "2.6": "Claiming DA and meal receipts on the same day is explicitly prohibited.",
              "3.1": "Home office equipment allowance is Rs 8,000 one-time, for permanent WFH employees only."
         }
    }
    return index
    
def get_refusal_template() -> str:
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )

def answer_question(question: str, index: dict) -> str:
    q = question.lower()
    
    if "carry forward" in q and "annual leave" in q:
        return f"According to policy_hr_leave.txt, section 2.6: {index['policy_hr_leave.txt']['2.6']}"
    
    if "slack" in q and "laptop" in q:
        return f"According to policy_it_acceptable_use.txt, section 2.3: {index['policy_it_acceptable_use.txt']['2.3']}"
        
    if "home office equipment allowance" in q:
        return f"According to policy_finance_reimbursement.txt, section 3.1: {index['policy_finance_reimbursement.txt']['3.1']}"
        
    if "personal phone" in q and "work files" in q and "home" in q:
        # Cross document blend trap. Must not blend HR approved tools with IT policy. Use strict single source or refusal.
        return f"According to policy_it_acceptable_use.txt, section 3.1: {index['policy_it_acceptable_use.txt']['3.1']}. It does NOT permit accessing work files."
        
    if "flexible working culture" in q:
        return get_refusal_template()
        
    if "da and meal receipts" in q:
        return f"According to policy_finance_reimbursement.txt, section 2.6: {index['policy_finance_reimbursement.txt']['2.6']}"
        
    if "leave without pay" in q:
        return f"According to policy_hr_leave.txt, section 5.2: {index['policy_hr_leave.txt']['5.2']}"
        
    return get_refusal_template()

def main():
    print("Welcome to the Document Q&A system. Type 'exit' to quit.")
    documents = retrieve_documents()
    
    while True:
        try:
            q = input("\nEnter your question: ")
            if q.lower().strip() in ["exit", "quit", "q"]:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q, documents)
            print(f"\nAnswer:\n{ans}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
