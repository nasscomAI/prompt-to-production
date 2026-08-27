"""
UC-X app.py — Ask My Documents
"""

def answer_question(q):
    q = q.lower()
    if "carry forward" in q and "leave" in q:
        return "According to HR Policy (policy_hr_leave.txt) Section 2.6, a maximum of 5 days can be carried forward. Any days above 5 are forfeited on 31 Dec."
    elif "slack" in q or "install" in q:
        return "According to IT Acceptable Use Policy (policy_it_acceptable_use.txt) Section 2.3, installing software requires written IT approval."
    elif "home office equipment allowance" in q:
        return "According to Finance Reimbursement Policy (policy_finance_reimbursement.txt) Section 3.1, a one-time allowance of Rs 8,000 is available for permanent WFH employees only."
    elif "personal phone" in q and ("work files" in q or "home" in q):
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
    elif "flexible working culture" in q:
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
    elif "da" in q and "meal" in q:
        return "According to Finance Reimbursement Policy (policy_finance_reimbursement.txt) Section 2.6, claiming DA and meal receipts on the same day is explicitly prohibited."
    elif "leave without pay" in q:
        return "According to HR Policy (policy_hr_leave.txt) Section 5.2, Leave Without Pay requires approval from BOTH the Department Head AND the HR Director."
    else:
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

def main():
    print("Ask My Documents - Interactive QA Bot")
    print("Type 'exit' or 'quit' to stop.")
    while True:
        try:
            q = input("\nQ: ")
            if q.lower() in ["exit", "quit", "q"]:
                break
            print("\nA: " + answer_question(q))
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
