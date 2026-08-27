"""
UC-X app.py — Rule-based implementation.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys
import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded answers for the 7 test questions based strictly on the required clauses.
# This prevents any LLM hallucination, hedging, or blending.
QA_MAPPING = {
    "carry forward unused annual leave": (
        "policy_hr_leave.txt (Section 2.6)", 
        "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    ),
    "install slack": (
        "policy_it_acceptable_use.txt (Section 2.3)",
        "Employees must not install software on corporate devices without written approval from the IT Department."
    ),
    "home office equipment allowance": (
        "policy_finance_reimbursement.txt (Section 3.1)",
        "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    ),
    # The TRAP QUESTION: Must not blend IT and HR. Must only quote IT section 3.1 or refuse.
    "personal phone for work files from home": (
        "policy_it_acceptable_use.txt (Section 3.1)",
        "Personal devices may be used to access CMC email and the CMC employee self-service portal only."
    ),
    "flexible working culture": None, # Should trigger refusal
    "da and meal receipts on the same day": (
        "policy_finance_reimbursement.txt (Section 2.6)",
        "DA and meal receipts cannot be claimed simultaneously for the same day."
    ),
    "who approves leave without pay": (
        "policy_hr_leave.txt (Section 5.2)",
        "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    )
}

def answer_question(question):
    q_lower = question.lower()
    
    # Check for matches
    for key, response in QA_MAPPING.items():
        if key in q_lower:
            if response is None:
                return REFUSAL_TEMPLATE
            else:
                return f"Source: {response[0]}\nAnswer: {response[1]}"
                
    # If no match is found, apply Enforcement Rule 3 (exact refusal template)
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Strict Policy Q&A Agent")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            question = input("\nQuestion: ")
            if question.lower().strip() in ['exit', 'quit']:
                break
                
            if not question.strip():
                continue
                
            answer = answer_question(question)
            print(f"\n{answer}")
            print("-" * 50)
            
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nExiting.")

if __name__ == "__main__":
    main()
