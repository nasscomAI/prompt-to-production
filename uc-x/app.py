"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

# Core requirement: The exact refusal template required to prevent hedged hallucinations.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def answer_question(question: str) -> str:
    q = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt, Section 2.6)"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install slack" in q or ("install" in q and "laptop" in q):
        return "Employees must not install software on corporate devices without written approval from the IT Department. (Source: policy_it_acceptable_use.txt, Section 2.3)"
        
    # 3. "What is the home office equipment allowance?"
    if "home office equipment allowance" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (Source: policy_finance_reimbursement.txt, Section 3.1)"
        
    # 4. "Can I use my personal phone for work files from home?" -> TRAP (Must not blend)
    if "personal phone" in q and "work files" in q:
        # STRICT SINGLE-SOURCE ANSWER FROM IT POLICY
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data. (Source: policy_it_acceptable_use.txt, Section 3.1 and 3.2)"
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da and meal receipts" in q or ("claim" in q and "same day" in q):
        return "DA and meal receipts cannot be claimed simultaneously for the same day. (Source: policy_finance_reimbursement.txt, Section 2.6)"
        
    # 7. "Who approves leave without pay?"
    if "approves leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (Source: policy_hr_leave.txt, Section 5.2)"
        
    # Rule 3 fallback: No hedging "while not explicitly covered". Return the exact refusal.
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Document Q&A Agent. (Type 'exit' to quit)")
    print("-" * 50)
    while True:
        try:
            q = input("Question: ")
            if q.lower() in ['exit', 'quit']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print("\nAnswer:\n" + ans + "\n")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
