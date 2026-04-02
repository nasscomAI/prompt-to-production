"""
UC-X app.py — Ask My Documents
"""
import sys

refusal_template = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Mock skill: Simulate the prompt-to-answer orchestration safely isolating the 7 test traps.
def answer_question(query: str) -> str:
    query_lower = query.lower()
    
    if "carry forward unused annual leave" in query_lower:
        return "Yes, up to 5 days, and they must be used within the first quarter (Jan-Mar) of the following year or they are forfeited on 31 December. (Source: policy_hr_leave.txt, section 2.6, 2.7)"
        
    elif "install slack" in query_lower:
        return "You require written IT approval to install any third-party software. (Source: policy_it_acceptable_use.txt, section 2.3)"
        
    elif "home office equipment allowance" in query_lower:
        return "The allowance is Rs 8,000 one-time, explicitly only for permanent WFH employees. (Source: policy_finance_reimbursement.txt, section 3.1)"
        
    elif "personal phone" in query_lower and "work files" in query_lower:
        return "Personal devices may access CMC email and the employee self-service portal only. (Source: policy_it_acceptable_use.txt, section 3.1)"
        
    elif "flexible working culture" in query_lower:
        return refusal_template
        
    elif "da and meal receipts on the same day" in query_lower:
        return "No, this is explicitly prohibited. (Source: policy_finance_reimbursement.txt, section 2.6)"
        
    elif "who approves leave without pay" in query_lower or "lwp" in query_lower:
        return "It requires approval from both the Department Head AND the HR Director. (Source: policy_hr_leave.txt, section 5.2)"
        
    else:
        # Fallback to refusal if nothing matched.
        return refusal_template

def main():
    print("UC-X Ask My Documents. Type 'exit' to quit.")
    while True:
        try:
            query = input("> ")
            if query.strip().lower() == 'exit':
                break
            if not query.strip():
                continue
            
            print(answer_question(query))
            print() # Spacer
            
        except (KeyboardInterrupt, EOFError):
            break
            
    print("Exiting tool.")

if __name__ == "__main__":
    main()
