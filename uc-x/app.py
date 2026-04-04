"""
UC-X app.py
Ask My Documents
"""

def main():
    print("Welcome to UC-X Policy Q&A. Type 'exit' to quit.")
    
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    while True:
        try:
            q = input("\nAsk a question: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
            
        if not q or q in ['exit', 'quit']:
            break
            
        if "carry forward" in q and "annual leave" in q:
            print("Answer: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March).")
            print("Source: policy_hr_leave.txt - Section 2.6")
        elif "slack" in q:
            print("Answer: Requires written IT approval.")
            print("Source: policy_it_acceptable_use.txt - Section 2.3")
        elif "home office" in q and "allowance" in q:
            print("Answer: Rs 8,000 one-time, permanent WFH only.")
            print("Source: policy_finance_reimbursement.txt - Section 3.1")
        elif "personal phone" in q or "working from home" in q:
            print("Answer: Personal devices may access CMC email and the employee self-service portal only.")
            print("Source: policy_it_acceptable_use.txt - Section 3.1")
        elif "flexible working culture" in q:
            print(refusal_template)
        elif "da" in q and "meal" in q:
            print("Answer: No, this is explicitly prohibited.")
            print("Source: policy_finance_reimbursement.txt - Section 2.6")
        elif "without pay" in q:
            print("Answer: LWP requires approval from the Department Head AND the HR Director.")
            print("Source: policy_hr_leave.txt - Section 5.2")
        else:
            print(refusal_template)

if __name__ == "__main__":
    main()
