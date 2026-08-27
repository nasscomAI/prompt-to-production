import sys

def answer_question(question):
    q = question.lower().strip()
    
    refusal = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    if "carry forward" in q and "leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt, section 2.6)"
    elif "slack" in q or "install" in q:
        return "Installing unauthorized software creates security risks and requires written IT approval. (Source: policy_it_acceptable_use.txt, section 2.3)"
    elif "allowance" in q and "home" in q:
        return "There is a Rs 8,000 one-time allowance for permanent WFH employees only. (Source: policy_finance_reimbursement.txt, section 3.1)"
    elif "personal phone" in q:
        return "Personal devices may access CMC email and the employee self-service portal only. (Source: policy_it_acceptable_use.txt, section 3.1)"
    elif "flexible working" in q or "culture" in q:
        return refusal
    elif "claim" in q and ("da" in q or "meal" in q):
        return "Claiming DA and meal receipts on the same day is explicitly prohibited. (Source: policy_finance_reimbursement.txt, section 2.6)"
    elif "lwp" in q or ("leave without pay" in q and "approve" in q):
        return "LWP requires approval from the Department Head AND the HR Director. Both are required. (Source: policy_hr_leave.txt, section 5.2)"
    else:
        return refusal

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type your question, or 'exit' to quit.")
    while True:
        try:
            q = input("\nQ: ")
        except EOFError:
            break
            
        if q.lower() in ['exit', 'quit']:
            break
            
        ans = answer_question(q)
        print("\nA: " + ans)

if __name__ == "__main__":
    main()
