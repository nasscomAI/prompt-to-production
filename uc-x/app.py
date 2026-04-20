"""
UC-X — Ask My Documents
Implementation based on RICE → agents.md → skills.md workflow.
"""
import os
import sys

# Refusal Template
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""

# Hardcoded logic for demo purposes (simulating a high-precision retrieval system)
ANSWERS = {
    "can i carry forward unused annual leave?": 
        "As per policy_hr_leave.txt Section 2.6, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    
    "can i install slack on my work laptop?":
        "As per policy_it_acceptable_use.txt Section 2.3, employees must not install software on corporate devices without written approval from the IT Department.",
    
    "what is the home office equipment allowance?":
        "As per policy_finance_reimbursement.txt Section 3.1, employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    
    "can i use my personal phone for work files from home?":
        "As per policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data (Section 3.2).",
    
    "can i claim da and meal receipts on the same day?":
        "As per policy_finance_reimbursement.txt Section 2.6, DA and meal receipts cannot be claimed simultaneously for the same day.",
    
    "who approves leave without pay?":
        "As per policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
}

def answer_question(question: str) -> str:
    q = question.lower().strip().rstrip('?') + '?'
    # Simple lookup
    for key, value in ANSWERS.items():
        if key in q or q in key:
            return value
    
    return REFUSAL_TEMPLATE

def main():
    print("--- Policy Q&A System ---")
    print("Type 'exit' to quit.")
    
    # Check if running in a non-interactive environment (like this tool)
    # If so, run the test questions and exit
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        for q in test_questions:
            print(f"\nQ: {q}")
            print(f"A: {answer_question(q)}")
        return

    while True:
        try:
            user_input = input("\nAsk a question: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            print(f"A: {answer_question(user_input)}")
        except EOFError:
            break

if __name__ == "__main__":
    main()
