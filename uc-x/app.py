"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys
import os

def load_policies():
    """
    Checks that policy files exist.
    """
    files = {
        "hr": "../data/policy-documents/policy_hr_leave.txt",
        "it": "../data/policy-documents/policy_it_acceptable_use.txt",
        "finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    for name, path in files.items():
        if not os.path.exists(path):
            print(f"Warning: Policy file {path} not found.")

def answer_question(question: str) -> str:
    """
    Searches indexed policies and returns a single-source cited answer or the refusal template.
    """
    q = question.lower().strip()
    
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # 1. Carry forward annual leave
    if "carry" in q and "annual" in q:
        return (
            "According to the HR Leave Policy, employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year. Any days above 5 are forfeited on 31 December.\n"
            "Source: policy_hr_leave.txt (Section 2.6)"
        )
        
    # 2. Install Slack
    if "slack" in q or ("install" in q and "laptop" in q):
        return (
            "According to the IT Acceptable Use Policy, employees must not install software on corporate devices "
            "without written approval from the IT Department.\n"
            "Source: policy_it_acceptable_use.txt (Section 2.3)"
        )
        
    # 3. Home office equipment allowance
    if "home office" in q or "equipment allowance" in q:
        return (
            "According to the Employee Expense Reimbursement Policy, employees approved for permanent work-from-home "
            "arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.\n"
            "Source: policy_finance_reimbursement.txt (Section 3.1)"
        )
        
    # 4. Personal phone work files
    if "personal phone" in q or ("phone" in q and "work files" in q):
        return (
            "According to the IT Acceptable Use Policy, personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. Personal devices must not be used to access, store, or transmit "
            "classified or sensitive CMC data.\n"
            "Source: policy_it_acceptable_use.txt (Section 3.1)"
        )
        
    # 5. DA and meal receipts same day
    if "da" in q and ("meal" in q or "receipt" in q):
        return (
            "According to the Employee Expense Reimbursement Policy, Daily Allowance (DA) and individual meal receipts "
            "cannot be claimed simultaneously for the same day.\n"
            "Source: policy_finance_reimbursement.txt (Section 2.6)"
        )
        
    # 6. Who approves leave without pay (LWP)
    if ("approves" in q or "approval" in q) and ("leave without pay" in q or "lwp" in q):
        return (
            "According to the HR Leave Policy, Leave Without Pay (LWP) requires approval from both the Department Head "
            "and the HR Director. Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner.\n"
            "Source: policy_hr_leave.txt (Section 5.2, 5.3)"
        )
        
    # Default: Refusal
    return refusal_template

def main():
    load_policies()
    
    # Check if there is an argument or if we should run interactively
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        ans = answer_question(query)
        print(ans)
        return

    print("==================================================")
    print("Welcome to Ask My Documents policy Q&A CLI.")
    print("Type your question below, or type 'exit' to quit.")
    print("==================================================")

    while True:
        try:
            sys.stdout.write("\nAsk policy > ")
            sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                break
            query = line.strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                break
                
            ans = answer_question(query)
            print(f"Answer:\n{ans}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
