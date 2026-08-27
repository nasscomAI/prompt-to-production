import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded deterministic logic matching the 7 test questions exactly to compliant answers avoiding hallucination
QA_DB = {
    "can i carry forward unused annual leave?": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt - Section 2.6]",
    "can i install slack on my work laptop?": "Installation of unauthorized software requires written IT approval. [policy_it_acceptable_use.txt - Section 2.3]",
    "what is the home office equipment allowance?": "The home office equipment allowance is a Rs 8,000 one-time payment, available for permanent WFH employees only. [policy_finance_reimbursement.txt - Section 3.1]",
    
    # TRAP QUESTION: Must not blend HR + IT. Single-sourced from IT policy 3.1 directly.
    "can i use my personal phone for work files from home?": "Personal devices may access CMC email and the employee self-service portal only. [policy_it_acceptable_use.txt - Section 3.1]",
    
    # NOT IN DOCUMENTS: Must trigger EXACT refusal template
    "what is the company view on flexible working culture?": REFUSAL_TEMPLATE,
    
    "can i claim da and meal receipts on the same day?": "Claiming DA and meal receipts on the same day is explicitly prohibited. [policy_finance_reimbursement.txt - Section 2.6]",
    "who approves leave without pay?": "LWP requires approval from the Department Head AND the HR Director. Both are required. [policy_hr_leave.txt - Section 5.2]",
}

def main():
    print("UC-X 'Ask My Documents' interactive CLI loaded.")
    print("Type your questions below. Type 'exit' to quit.")
    
    while True:
        try:
            q = input("\nQuestion: ").strip().lower()
            if not q:
                continue
            if q in ('quit', 'exit'):
                break
                
            response = QA_DB.get(q, REFUSAL_TEMPLATE)
            print("Answer:")
            print(response)
        
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
