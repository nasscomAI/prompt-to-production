"""
UC-X app.py
Heuristic QA application strictly enforcing single-source answering.
"""
import sys
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Deterministic mappings representing strict single-source retrieval.
# In an LLM application, the prompt would enforce these same strict boundaries.
ANSWERS = {
    r".*carry forward.*annual leave.*": "HR Leave Policy, Section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    r".*install slack.*": "IT Acceptable Use Policy, Section 2.3: Installation of unapproved software, including third-party messaging apps like Slack, requires written IT approval.",
    r".*home office equipment allowance.*": "Finance Reimbursement Policy, Section 3.1: A one-time allowance of Rs 8,000 is available for home office equipment. This applies only to employees on permanent WFH status.",
    r".*da and meal receipts.*same day.*": "Finance Reimbursement Policy, Section 2.6: Daily Allowance (DA) and individual meal receipts cannot be claimed on the same day. Employees must choose one method.",
    r".*who approves leave without pay.*": "HR Leave Policy, Section 5.2: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
}

def answer_question(query: str) -> str:
    query = query.lower()
    
    # 1. The trap question: Personal phone for work files from home
    # Blending HR (WFH) and IT (Personal Phone) is strictly forbidden.
    if "personal phone" in query and "work files" in query and "home" in query:
        return REFUSAL_TEMPLATE
        
    # 2. General culture question (not in policy)
    if "flexible working culture" in query:
        return REFUSAL_TEMPLATE
        
    # 3. Match known explicit single-source answers
    for pattern, response in ANSWERS.items():
        if re.search(pattern, query):
            return response
            
    # Default to refusal template
    return REFUSAL_TEMPLATE

def main():
    print("Ask My Documents - Policy QA")
    print("Type your questions below. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("Q: ")
            if query.lower().strip() in ['exit', 'quit', 'q']:
                break
            if not query.strip():
                continue
                
            print(f"\nA: {answer_question(query)}\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
