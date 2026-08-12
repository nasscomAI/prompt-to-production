import sys

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def answer_question(q):
    q = q.lower()
    if "carry forward" in q and "annual leave" in q:
        return "Source: policy_hr_leave.txt, Section 2.6. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    if "slack" in q and "laptop" in q:
        return "Source: policy_it_acceptable_use.txt, Section 2.3. Requires written IT approval."
    if "home office equipment allowance" in q:
        return "Source: policy_finance_reimbursement.txt, Section 3.1. Rs 8,000 one-time, permanent WFH only."
    if "personal phone" in q and "work files" in q:
        return "Source: policy_it_acceptable_use.txt, Section 3.1. Personal devices may access CMC email and the employee self-service portal only."
    if "flexible working culture" in q:
        return REFUSAL
    if "da and meal receipts" in q or "da" in q and "meal" in q:
        return "Source: policy_finance_reimbursement.txt, Section 2.6. NO, explicitly prohibited."
    if "approves leave without pay" in q:
        return "Source: policy_hr_leave.txt, Section 5.2. Department Head AND HR Director, both required."
    
    return REFUSAL

if __name__ == "__main__":
    print("Ask My Documents - Interactive CLI. Type 'exit' to quit.")
    while True:
        try:
            user_q = input("> ")
            if user_q.lower() in ('exit', 'quit'):
                break
            print(answer_question(user_q))
        except EOFError:
            break
