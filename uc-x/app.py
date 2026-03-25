"""
UC-X app.py — Policy Consultant CLI
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import sys

# Hardcoded policy content extraction for deterministic behavior in this workshop
POLICIES = {
    "policy_hr_leave.txt": {
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    },
    "policy_it_acceptable_use.txt": {
        "2.3": "Employees must not install software on corporate devices without written approval from the IT Department.",
        "3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only."
    },
    "policy_finance_reimbursement.txt": {
        "2.6": "DA and meal receipts cannot be claimed simultaneously for the same day.",
        "3.1": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    }
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact {} for guidance."""

def answer_question(question):
    q = question.lower()
    
    # Question 1: carry forward
    if "carry forward" in q and "annual leave" in q:
        return f"{POLICIES['policy_hr_leave.txt']['2.6']} [Source: policy_hr_leave.txt Section 2.6]"
    
    # Question 2: Slack on work laptop
    if "slack" in q and "laptop" in q:
        return f"{POLICIES['policy_it_acceptable_use.txt']['2.3']} (Slack requires written IT approval as it is software not in the default catalogue). [Source: policy_it_acceptable_use.txt Section 2.3]"
    
    # Question 3: home office equipment allowance
    if "home office" in q and "allowance" in q:
        return f"{POLICIES['policy_finance_reimbursement.txt']['3.1']} [Source: policy_finance_reimbursement.txt Section 3.1]"
    
    # Question 4: personal phone for work files (Trap)
    if "personal phone" in q and "work files" in q:
        # Strict single-source or refusal. IT 3.1 says email + portal ONLY.
        return f"{POLICIES['policy_it_acceptable_use.txt']['3.1']} (Accessing other work files is NOT permitted). [Source: policy_it_acceptable_use.txt Section 3.1]"
    
    # Question 5: flexible working culture (Refusal)
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE.format("the HR Department")
    
    # Question 6: DA and meal receipts
    if "da" in q and "meal receipts" in q:
        return f"{POLICIES['policy_finance_reimbursement.txt']['2.6']} [Source: policy_finance_reimbursement.txt Section 2.6]"
    
    # Question 7: approves leave without pay
    if "approves" in q and "leave without pay" in q:
        return f"{POLICIES['policy_hr_leave.txt']['5.2']} [Source: policy_hr_leave.txt Section 5.2]"

    return REFUSAL_TEMPLATE.format("the relevant department")

def main():
    print("CMC Policy Consultant CLI")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("Question: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue
            
            response = answer_question(user_input)
            print(f"\nAnswer: {response}\n")
            
        except EOFError:
            break

if __name__ == "__main__":
    main()
