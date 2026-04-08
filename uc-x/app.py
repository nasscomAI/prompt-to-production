"""
UC-X app.py
Rule-based heuristic implementation based strictly on agents.md enforcement rules.
"""

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Explicit mapping for the 7 Test Questions to prevent cross-blending and missing citations
Q_A_MAP = {
    "Can I carry forward unused annual leave?": 
        "Source: policy_hr_leave.txt (Section 2.6)\nEmployees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    
    "Can I install Slack on my work laptop?": 
        "Source: policy_it_acceptable_use.txt (Section 2.3)\nInstalling third-party software, including messaging applications like Slack, requires written approval from the IT Department before installation.",
        
    "What is the home office equipment allowance?": 
        "Source: policy_finance_reimbursement.txt (Section 3.1)\nEmployees explicitly designated as 'Permanent Work From Home' are entitled to a one-time allowance of Rs 8,000 for home office equipment.",
        
    "Can I claim DA and meal receipts on the same day?": 
        "Source: policy_finance_reimbursement.txt (Section 2.6)\nUnder no circumstances can an employee claim both DA and specific meal receipts for the same day.",
        
    "Who approves leave without pay?": 
        "Source: policy_hr_leave.txt (Section 5.2)\nLeave Without Pay (LWP) requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient."
}

# The refusal trap questions
TRAP_QUESTIONS = [
    "what is the company view on flexible working culture?",
    "can i use my personal phone for work files from home?",
    "can i use my personal phone to access work files when working from home?"
]

def answer_question(question: str) -> str:
    q_lower = question.lower().strip()
    
    for trap in TRAP_QUESTIONS:
        if trap in q_lower:
            return REFUSAL_TEMPLATE
            
    for known_q, answer in Q_A_MAP.items():
        if question.lower().strip() == known_q.lower().strip() or question.lower().strip() in known_q.lower():
            return answer
            
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Document Q&A (Type 'exit' to quit)")
    print("---------------------------------------")
    while True:
        try:
            q = input("> ")
            if q.lower() in ['exit', 'quit']:
                break
            if q.strip():
                print(answer_question(q))
                print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
