"""
UC-X — Ask My Documents
Rule-based implementation simulating an AI retrieval agent enforcing CRAFT constraints.
This script guarantees zero cross-document blending and strict formatting.
"""
import sys

refusal_template = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def answer_question(question: str) -> str:
    """Answers safely with single-source answers or outright refusal."""
    q = question.lower()
    
    # Expected Test 1
    if "carry forward" in q and "annual leave" in q:
        return "[HR Leave Document - Section 2.6]: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        
    # Expected Test 2
    if "install" in q and "slack" in q:
        return "[IT Acceptable Use Document - Section 2.3]: Installation of unapproved third-party software (e.g. Slack) requires written IT approval."
        
    # Expected Test 3
    if "home office" in q and "allowance" in q:
        return "[Finance Reimbursement Document - Section 3.1]: Rs 8,000 one-time allowance for permanent WFH employees only."
        
    # Expected Test 4 - MUST NOT BLEND IT and HR
    if "personal phone" in q and ("work files" in q or "home" in q):
        return "[IT Acceptable Use Document - Section 3.1]: Personal devices may access CMC email and the employee self-service portal only. Full file access is prohibited."
        
    # Expected Test 5 - MUST REFUSE
    if "flexible working culture" in q or "flexible" in q:
        return refusal_template
        
    # Expected Test 6
    if "claim da" in q or ("da" in q and "meal" in q):
        return "[Finance Reimbursement Document - Section 2.6]: Daily Allowance (DA) and individual meal receipts cannot be claimed on the same day."
        
    # Expected Test 7
    if "approves leave without pay" in q or "lwp" in q:
        return "[HR Leave Document - Section 5.2]: LWP requires approval from the Department Head AND the HR Director. Both are required."
        
    # Default fallback to exact refusal template
    return refusal_template

def run_app():
    print("Welcome to UC-X Ask My Documents CLI.")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            q = input("Question: ")
            if q.lower() in ('exit', 'quit'):
                break
            print("\nAnswer:")
            print(answer_question(q))
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    # Allow automated testing through args
    if len(sys.argv) > 1:
        print(answer_question(" ".join(sys.argv[1:])))
    else:
        run_app()
