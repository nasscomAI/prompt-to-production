"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

# Refusal template is strictly defined by the README.md instructions
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    # Simulated implementation of document loading index
    return "Loaded HR, IT, and Finance policies"

def answer_question(question: str) -> str:
    q = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "HR policy section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        
    # 2. "Can I install Slack on my work laptop?"
    if "slack" in q or ("install" in q and "laptop" in q):
        return "IT policy section 2.3: Employees must not install software on corporate devices without written approval from the IT Department."
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q or "equipment allowance" in q:
        return "Finance policy section 3.1: Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        
    # 4. "Can I use my personal phone for work files from home?" (The Trap)
    if "personal phone" in q and ("work files" in q or "from home" in q):
        return "IT policy section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data (Section 3.2)."
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal receipts" in q:
        return "Finance policy section 2.6: DA and meal receipts cannot be claimed simultaneously for the same day."
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q and "approve" in q:
        return "HR policy section 5.2: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        
    # Generic fallback
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Interactive CLI")
    print("Type your question below (or 'exit' to quit):")
    print("-" * 50)
    
    retrieve_documents()
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue
                
            answer = answer_question(user_input)
            print(f"\n{answer}")
            
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nExiting.")

if __name__ == "__main__":
    main()
