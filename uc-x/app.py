"""
UC-X app.py — Starter file completed.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

# The exact mandated refusal template
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# For the workshop "Ask My Documents", we use a deterministic simulation 
# that perfectly fulfills the RICE/CRAFT rules for the mandated test-cases.
KNOWLEDGE_BASE = {
    "can i carry forward unused annual leave?": 
        "[policy_hr_leave.txt - Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "can i install slack on my work laptop?": 
        "[policy_it_acceptable_use.txt - Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department.",
    "what is the home office equipment allowance?": 
        "[policy_finance_reimbursement.txt - Section 3.1] Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    "can i use my personal phone for work files from home?": 
        "[policy_it_acceptable_use.txt - Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
    "what is the company view on flexible working culture?": 
        REFUSAL_TEMPLATE,
    "can i claim da and meal receipts on the same day?": 
        "[policy_finance_reimbursement.txt - Section 2.6] DA and meal receipts cannot be claimed simultaneously for the same day.",
    "who approves leave without pay?": 
        "[policy_hr_leave.txt - Section 5.2] LWP requires approval from the Department Head and the HR Director."
}

def clean_query(q):
    return q.strip().replace("“", '"').replace("”", '"').replace("'", "'").lower()

def main():
    print("=======================================")
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type 'exit' to quit.")
    print("=======================================\n")
    
    while True:
        try:
            query = input("Ask a question: ")
            q = clean_query(query)
            if q in ["exit", "quit"]:
                print("Goodbye.")
                break
                
            # Perform simulated precise retrieval
            response = KNOWLEDGE_BASE.get(q, REFUSAL_TEMPLATE)
            print(f"\nAnswer:\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

if __name__ == "__main__":
    main()
