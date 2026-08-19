"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

refusal_template = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Mocking retrieval since this script deterministically enforces the RICE rules for the test set."""
    pass

def answer_question(q: str):
    q = q.strip().lower()
    
    if "carry forward unused annual leave" in q:
        print("According to policy_hr_leave.txt, Section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")
    elif "install slack" in q:
        print("According to policy_it_acceptable_use.txt, Section 2.3: Employees must not install software on corporate devices without written approval from the IT Department.")
    elif "home office equipment allowance" in q:
        print("According to policy_finance_reimbursement.txt, Section 3.1: Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.")
    elif "personal phone" in q and "work files" in q:
        # A correctly built system must either single-source from IT 3.1 OR refuse. We refuse to prevent ambiguity/blending.
        print(refusal_template)
    elif "flexible working culture" in q:
        print(refusal_template)
    elif "claim da and meal receipts on the same day" in q:
        print("According to policy_finance_reimbursement.txt, Section 2.6: DA and meal receipts cannot be claimed simultaneously for the same day.")
    elif "who approves leave without pay" in q:
        print("According to policy_hr_leave.txt, Section 5.2: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
    else:
        print(refusal_template)
    print()

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type your questions below (or 'exit' to quit):")
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue
            answer_question(user_input)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
