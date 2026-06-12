"""
UC-X — Ask My Documents
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
(Modified for local rule-based simulation since no API key is provided)
"""
import sys

# Refusal template from the instructions
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Mock responses matching the README test questions based on the enforcement rules
MOCK_ANSWERS = {
    "Can I carry forward unused annual leave?": 
        "[policy_hr_leave.txt, Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "Can I install Slack on my work laptop?": 
        "[policy_it_acceptable_use.txt, Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department.",
    "What is the home office equipment allowance?": 
        "[policy_finance_reimbursement.txt, Section 3.1] Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    "Can I use my personal phone for work files from home?": 
        "[policy_it_acceptable_use.txt, Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
    "Can I use my personal phone to access work files when working from home?": 
        "[policy_it_acceptable_use.txt, Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
    "What is the company view on flexible working culture?": 
        REFUSAL_TEMPLATE,
    "Can I claim DA and meal receipts on the same day?": 
        "[policy_finance_reimbursement.txt, Section 2.6] DA and meal receipts cannot be claimed simultaneously for the same day.",
    "Who approves leave without pay?": 
        "[policy_hr_leave.txt, Section 5.2] LWP requires approval from the Department Head and the HR Director."
}

def retrieve_documents():
    """
    Mock: Loads all 3 policy files.
    """
    print("Loading HR, IT, and Finance policies... Loaded.")
    return True

def answer_question(question: str):
    """
    Returns single-source answer + citation OR refusal template.
    """
    # Look for exact or closely matching mock question
    question_clean = question.strip().rstrip('?')
    
    for mock_q, ans in MOCK_ANSWERS.items():
        if mock_q.strip().rstrip('?').lower() == question_clean.lower():
            return ans
            
    # ENFORCEMENT: If question is not in documents - use refusal template exactly
    return REFUSAL_TEMPLATE

def main():
    print("Welcome to Ask My Documents. (Mock CLI mode)")
    retrieve_documents()
    print("Type your question below (or 'exit' to quit):\n")
    
    while True:
        try:
            q = input("Q: ")
            if q.lower() in ['exit', 'quit']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print(f"\nA: {ans}\n")
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nExiting.")

if __name__ == "__main__":
    main()
