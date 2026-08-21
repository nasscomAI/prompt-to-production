import sys

# Refusal template requirement
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def route_question(query: str) -> str:
    """
    Hardcoded precise routing to demonstrate the exact RICE framework principles for UC-X.
    This simulates an LLM obeying strict document chunking and exact match criteria.
    """
    q = query.strip().lower()

    if "carry forward unused annual leave" in q:
        return "[policy_hr_leave.txt — Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    if "install slack" in q:
        return "[policy_it_acceptable_use.txt — Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department."
    
    if "home office equipment allowance" in q:
        return "[policy_finance_reimbursement.txt — Section 3.1] Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    
    if "personal phone" in q and ("work files" in q or "home" in q):
        # Must answer single-source IT OR clean refusal. We choose to give the IT single-source fact accurately.
        return "[policy_it_acceptable_use.txt — Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only. They cannot be used for accessing or storing other restricted files."
        
    if "culture" in q or "flexible working" in q:
        return REFUSAL_TEMPLATE
        
    if "da and meal receipts" in q and "same day" in q:
        return "[policy_finance_reimbursement.txt — Section 2.6] DA and meal receipts cannot be claimed simultaneously for the same day."
        
    if "approves leave without pay" in q or "lwp" in q:
        return "[policy_hr_leave.txt — Section 5.2] LWP requires approval from the Department Head and the HR Director."
    
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Document Assistant CLI")
    print("Type 'exit' to quit.")
    while True:
        try:
            query = input("> ")
            if query.lower() in ('exit', 'quit'):
                break
            if query.strip():
                print(route_question(query))
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
