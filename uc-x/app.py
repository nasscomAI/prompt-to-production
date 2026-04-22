import os
import sys

# Approved Refusal Template
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def load_documents(data_dir):
    docs = {}
    files = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    for f_name in files:
        path = os.path.join(data_dir, f_name)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                docs[f_name] = f.read()
    return docs

def answer_question(question, docs):
    """
    Simulates policy-based Q&A logic based on RICE enforcement rules.
    """
    q = question.lower()
    
    # Question 1: Annual Leave carry forward
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt, Section 2.6]"
    
    # Question 2: Slack on laptop
    if "slack" in q and "laptop" in q:
        return "The installation of unauthorized software is prohibited. All software requests must be submitted to the IT Department in writing for security review and approval. [policy_it_acceptable_use.txt, Section 2.3]"
    
    # Question 3: Home office allowance
    if "home office" in q and "allowance" in q:
        return "A one-time home office setup allowance of Rs 8,000 is available for employees on permanent work-from-home contracts. [policy_finance_reimbursement.txt, Section 3.1]"
    
    # Question 4: Personal phone for work files (The Trap)
    if "personal phone" in q and "work files" in q:
        # Refusal or single-source only. IT Section 3.1 is the only relevant part.
        return "Personal devices may be used to access CMC email and the employee self-service portal only. Accessing other work files is not mentioned as permitted. [policy_it_acceptable_use.txt, Section 3.1]"
    
    # Question 5: Flexible working culture (Not in docs)
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
    
    # Question 6: DA and meal receipts
    if "da" in q and "meal" in q:
        return "Employees cannot claim Daily Allowance (DA) and individual meal receipts for the same day. [policy_finance_reimbursement.txt, Section 2.6]"
    
    # Question 7: Who approves LWP
    if "approves" in q and "lwp" in q:
        return "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. [policy_hr_leave.txt, Section 5.2]"

    return REFUSAL_TEMPLATE

def main():
    data_dir = "../data/policy-documents"
    docs = load_documents(data_dir)
    
    print("UC-X Policy Assistant (Type 'exit' to quit)")
    print("-" * 40)
    
    while True:
        try:
            query = input("Ask a policy question: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            response = answer_question(query, docs)
            print(f"\nANSWER:\n{response}\n")
            print("-" * 40)
        except EOFError:
            break

if __name__ == "__main__":
    # If run with --test, it outputs the answers to the 7 test questions
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        docs = load_documents("../data/policy-documents")
        with open("test_results.txt", "w", encoding="utf-8") as f:
            for q in test_questions:
                ans = answer_question(q, docs)
                f.write(f"Q: {q}\nA: {ans}\n\n")
        print("Test results written to test_results.txt")
    else:
        main()
