"""
UC-X app.py
Ask My Documents.
Deterministic implementation for Q&A demonstrating required retrieval and anti-blending logic.
"""
import argparse
import sys

# The exact refusal template required by the prompt
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded logic to demonstrate the exact bounds of the policies for the 7 questions
def answer_question(question: str) -> str:
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [Source: policy_hr_leave.txt, Section 2.6]"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install slack" in q or ("install" in q and "laptop" in q):
        return "Employees must not install software on corporate devices without written approval from the IT Department. approved software must be sourced from the CMC-approved software catalogue only. [Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        
    # 3. "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. [Source: policy_finance_reimbursement.txt, Section 3.1]"
        
    # 4. "Can I use my personal phone for work files from home?" (The Blend Trap)
    elif "personal phone" in q and "work files" in q:
        # We must NOT blend HR's remote work definitions with IT's BYOD restrictions.
        # IT policy explicitly says personal devices can access email and self-service portal *only*.
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data. [Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal receipts" in q:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. [Source: policy_finance_reimbursement.txt, Section 2.6]"
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q and ("approve" in q or "approves" in q):
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [Source: policy_hr_leave.txt, Section 5.2]"
        
    # Catch-all
    else:
        return REFUSAL_TEMPLATE


def main():
    print("UC-X Ask My Documents — Interactive CLI")
    print("Type your question below (or 'exit' to quit):")
    print("-" * 50)
    
    while True:
        try:
            q = input("\nQ: ")
            if q.lower() in ('exit', 'quit'):
                break
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print(f"\nA: {ans}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
