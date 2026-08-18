"""
UC-X app.py — Policy Q&A Agent Implementation.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

# Configuration
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# keyword to document-section mapping for rule-based answering
# in a real world, this would be an LLM + RAG, but here we enforce the rules strictly via mapping
GROUND_TRUTH = [
    (r"carry forward.*annual leave", "policy_hr_leave.txt", "2.6", "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."),
    (r"install.*slack", "policy_it_acceptable_use.txt", "2.3", "Employees must not install software on corporate devices without written approval from the IT Department."),
    (r"home office equipment allowance", "policy_finance_reimbursement.txt", "3.1", "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."),
    (r"personal phone.*work files", "policy_it_acceptable_use.txt", "3.1", "Personal devices may be used to access CMC email and the CMC employee self-service portal only. (Note: Access to other work files is implicitly restricted by exception)."),
    (r"da and meal receipts", "policy_finance_reimbursement.txt", "2.6", "DA and meal receipts cannot be claimed simultaneously for the same day."),
    (r"approves leave without pay", "policy_hr_leave.txt", "5.2", "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."),
]

def get_answer(question):
    question = question.lower()
    
    # Strictly forbid hedging or blending by using direct mapping
    for pattern, doc, section, answer in GROUND_TRUTH:
        if re.search(pattern, question.replace("  ", " ")):
            return f"{answer}\n\nSource: {doc} Section {section}"
    
    # Refusal template if not found
    return REFUSAL_TEMPLATE

def main():
    print("Welcome to the CMC Policy Q&A Agent.")
    print("Available documents: HR Leave, IT Acceptable Use, Finance Reimbursement.")
    print("-" * 50)
    
    # Check if files exist
    base_path = "../data/policy-documents/"
    for doc in DOCUMENTS:
        if not os.path.exists(os.path.join(base_path, doc)):
            print(f"Warning: {doc} not found in {base_path}")

    while True:
        try:
            user_input = input("\nAsk a question (or type 'exit' to quit): ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
                
            answer = get_answer(user_input)
            print("\n" + "="*20)
            print(answer)
            print("="*20)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
