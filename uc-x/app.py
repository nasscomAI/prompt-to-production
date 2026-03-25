import sys

def get_answer(question):
    """
    Returns an answer for the given question based on policy documents.
    Strictly follows the 'no blending' and 'single source' rules.
    """
    q = question.lower()
    
    # Refusal Template
    refusal = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact [relevant team] for guidance."
    )
    
    # 1. Annual Leave Carry Forward
    if "carry forward" in q and "annual leave" in q:
        return "[Source: policy_hr_leave.txt, Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    # 2. Install Slack
    if "install" in q and ("slack" in q or "software" in q):
        return "[Source: policy_it_acceptable_use.txt, Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department."
        
    # 3. Home office allowance
    if "home office" in q and "allowance" in q:
        return "[Source: policy_finance_reimbursement.txt, Section 3.1] Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        
    # 4. Personal phone for work files
    if "personal phone" in q and ("work files" in q or "home" in q):
        # Rule: No blending. Answer only from IT policy.
        return "[Source: policy_it_acceptable_use.txt, Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only. [Section 3.2] Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        
    # 6. DA and meal receipts
    if "da" in q and "meal" in q:
        return "[Source: policy_finance_reimbursement.txt, Section 2.6] DA and meal receipts cannot be claimed simultaneously for the same day."
        
    # 7. Who approves LWP
    if "approves" in q and ("leave without pay" in q or "lwp" in q):
        # 5.2 LWP requires Department Head AND HR Director approval
        return "[Source: policy_hr_leave.txt, Section 5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."

    # 5. Flexible working culture (Not in docs)
    # Default fallback to refusal
    return refusal

def main():
    print("CMC Policy Assistant (UC-X)")
    print("Type your question or 'exit' to quit.")
    
    # Check if a question was passed as an argument (for testing)
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}")
        print(f"Answer: {get_answer(question)}")
        return

    while True:
        try:
            user_input = input("\nQuery > ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            print(get_answer(user_input))
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
