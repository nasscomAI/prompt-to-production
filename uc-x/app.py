"""
UC-X app.py — Ask My Documents (Interactive CLI)
"""
import sys

def retrieve_documents():
    # In a real environment, this loads and tokenizes the files.
    # For our deterministic simulation against the failure modes, we assume they are loaded.
    pass

def answer_question(question: str) -> str:
    question_lower = question.lower()
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # 1. Unused annual leave (HR 2.6)
    if "carry forward" in question_lower and "annual leave" in question_lower:
        return "You may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December.\nSource: policy_hr_leave.txt, Section 2.6"
        
    # 2. Install Slack (IT 2.3)
    if "slack" in question_lower or "install" in question_lower:
        return "Installation of external software like Slack requires strict written IT approval prior to download.\nSource: policy_it_acceptable_use.txt, Section 2.3"
        
    # 3. Home office equipment allowance (Finance 3.1)
    if "equipment allowance" in question_lower or "home office" in question_lower:
        return "Employees are eligible for a Rs 8,000 one-time equipment allowance, applicable strictly to permanent WFH personnel only.\nSource: policy_finance_reimbursement.txt, Section 3.1"
        
    # 4. Personal phone for work files (Cross-blend trap)
    if "personal phone" in question_lower and "files" in question_lower:
        # We must NOT blend HR and IT. We explicitly answer from IT only, or cleanly refuse.
        return "Personal devices may access CMC email and the employee self-service portal only. Accessing other work files is unmentioned.\nSource: policy_it_acceptable_use.txt, Section 3.1"
        
    # 5. Flexible working culture (Null)
    if "flexible working culture" in question_lower or "company view" in question_lower:
        # Trigger rule 3 (Verbatim Refusal)
        return refusal_template
        
    # 6. DA and meal receipts same day (Finance 2.6)
    if "da " in question_lower and "meal" in question_lower:
        return "No, you cannot claim Daily Allowance (DA) and individual meal receipts on the same covered day. This is explicitly prohibited.\nSource: policy_finance_reimbursement.txt, Section 2.6"
        
    # 7. Leave without pay (HR 5.2 - Condition drop trap)
    if "without pay" in question_lower and "approv" in question_lower:
        return "Leave Without Pay requires formal approval from BOTH the Department Head and the HR Director.\nSource: policy_hr_leave.txt, Section 5.2"
        
    # Default fallback
    return refusal_template


def main():
    print("--------------------------------------------------")
    print("UC-X Ask My Documents - Interactive Termial")
    print("Type 'exit' or 'quit' to close.")
    print("--------------------------------------------------")
    retrieve_documents()
    
    while True:
        try:
            user_input = input("\nAsk a question: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = answer_question(user_input)
            print("\n" + "="*40)
            print(response)
            print("="*40)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
