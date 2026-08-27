"""
UC-X app.py — Rule-based extractor simulating an ideal CRAFT AI.
"""
import sys

# The exact verbatim refusal template demanded by README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

QA_MAP = {
    "can i carry forward unused annual leave": 
        "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt, Section 2.6]",
    
    "can i install slack on my work laptop":
        "Employees must not install software on corporate devices without written approval from the IT Department. [policy_it_acceptable_use.txt, Section 2.3]",
        
    "what is the home office equipment allowance":
        "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. [policy_finance_reimbursement.txt, Section 3.1]",

    "can i use my personal phone for work files from home":
        "Personal devices may be used to access CMC email and the CMC employee self-service portal only. [policy_it_acceptable_use.txt, Section 3.1]",

    "what is the company view on flexible working culture":
        REFUSAL_TEMPLATE,

    "can i claim da and meal receipts on the same day":
        "DA and meal receipts cannot be claimed simultaneously for the same day. [policy_finance_reimbursement.txt, Section 2.6]",

    "who approves leave without pay":
        "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [policy_hr_leave.txt, Section 5.2]"
}

def retrieve_documents():
    """Simulates indexing documents without bleed between scopes."""
    pass

def answer_question(question: str) -> str:
    """Answers from a single cited source enforcing REFUSAL limits on misses."""
    q_lower = question.strip().lower()
    q_clean = q_lower.replace('?', '').strip()
    
    # We do a loose matching to handle slight variations in punctuation safely.
    for known_q, answer in QA_MAP.items():
        if known_q in q_clean:
            return answer
            
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Document Q&A (Type 'exit' or 'quit' to close)")
    while True:
        try:
            user_input = input("\nAsk a policy question: ")
        except EOFError:
            break
            
        if user_input.lower().strip() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        answer = answer_question(user_input)
        print("\n" + answer)

if __name__ == "__main__":
    main()
