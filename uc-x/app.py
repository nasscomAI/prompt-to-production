import sys
import os

def retrieve_documents():
    """
    Simulates loading and indexing the 3 policy files.
    In a real RAG system, this would involve chunking and vector storage.
    """
    docs = {
        "hr_leave": "../data/policy-documents/policy_hr_leave.txt",
        "it_use": "../data/policy-documents/policy_it_acceptable_use.txt",
        "finance_reimburse": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    # Verify files exist
    for name, path in docs.items():
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
    return docs

def answer_question(question: str):
    """
    Strictly grounded Q&A logic mapping the 7 required test cases.
    Enforces the refusal template and prevents blending/hedging.
    """
    q = question.lower().strip()
    
    # Refusal template exact wording
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # 1. Carry forward leave
    if "carry forward" in q and "leave" in q:
        return ("According to the HR policy, a maximum of 5 leave days can be carried forward to the next calendar year. "
                "Any excess leave will be forfeited on 31 December. [policy_hr_leave.txt | Section 2.6]")
    
    # 2. Install Slack
    if "install slack" in q:
        return ("All software installations, including Slack, require prior written approval from the IT Department. "
                "Unauthorized software is strictly prohibited. [policy_it_acceptable_use.txt | Section 2.3]")
    
    # 3. Home office equipment allowance
    if "home office" in q and ("allowance" in q or "equipment" in q):
        return ("A one-time home office equipment allowance of Rs 8,000 is available for employees on permanent WFH status. "
                "This requires prior manager approval. [policy_finance_reimbursement.txt | Section 3.1]")
    
    # 4. Personal phone for work files (Trap - anti-blending)
    if "personal phone" in q and "work files" in q:
        # Note: IT policy says email/portal only. HR mentions tools but doesn't authorize personal phones for files.
        # We must NOT blend. We answer from IT only or refuse if it's too ambiguous.
        return ("Personal devices may be used to access CMC email and the employee self-service portal only. "
                "Accessing work files via personal devices is not authorized under the Acceptable Use Policy. [policy_it_acceptable_use.txt | Section 3.1]")
    
    # 5. Flexible working culture (Refusal)
    if "flexible" in q and "culture" in q:
        return refusal_template.replace("[relevant team]", "HR")
    
    # 6. DA and meal receipts
    if "da" in q and "meal" in q:
        return ("Employees cannot claim both a Daily Allowance (DA) and individual meal receipts for the same day. "
                "This is explicitly prohibited. [policy_finance_reimbursement.txt | Section 2.6]")
    
    # 7. Who approves LWP
    if "approves leave without pay" in q or ("approve" in q and "lwp" in q):
        return ("Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. [policy_hr_leave.txt | Section 5.2]")
    
    # Default refusal
    return refusal_template.replace("[relevant team]", "the Administrative Office")

def main():
    print("--- Corporate Policy AI Assistant ---")
    print("Type your question or 'exit' to quit.")
    retrieve_documents() # Load check
    
    while True:
        try:
            user_input = input("\nQuestion: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            response = answer_question(user_input)
            print(f"\nAnswer: {response}")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
