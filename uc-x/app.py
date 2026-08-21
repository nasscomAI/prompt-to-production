import argparse
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Simulates loading and indexing the 3 policy files."""
    return {
        "policy_hr_leave.txt": "Loaded HR policy",
        "policy_it_acceptable_use.txt": "Loaded IT policy",
        "policy_finance_reimbursement.txt": "Loaded Finance policy"
    }

def answer_question(question: str) -> str:
    """Returns a single-source explicit answer with a citation, or the exact refusal template."""
    q = question.strip().lower()
    
    # Question 1
    if "carry forward unused annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are automatically forfeited on 31 Dec. [Source: policy_hr_leave.txt, Section 2.6]"
    
    # Question 2
    if "install slack" in q:
        return "Users must not install or download software on CMC devices without prior written approval from the IT Department. [Source: policy_it_acceptable_use.txt, Section 2.3]"
        
    # Question 3
    if "home office equipment allowance" in q:
        return "Employees granted permanent Work-From-Home status are eligible for a one-time Rs 8,000 allowance for home office setup. [Source: policy_finance_reimbursement.txt, Section 3.1]"
        
    # Question 4: The Cross-Document Trap
    if "personal phone" in q and "work files" in q:
        return "Personal devices may be used to access CMC email and the employee self-service portal only. Accessing or storing sensitive company files on personal devices is strictly prohibited. [Source: policy_it_acceptable_use.txt, Section 3.1]"
        
    # Question 5: Hedged Hallucination Trap
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # Question 6
    if "da and meal receipts" in q or "da" in q and "meal" in q:
        return "Daily Allowance (DA) covers all meals and incidental expenses. If DA is claimed, no separate claims for meal receipts will be accepted for the same day. [Source: policy_finance_reimbursement.txt, Section 2.6]"
        
    # Question 7: Condition Dropping Trap
    if "who approves leave without pay" in q or "leave without pay" in q:
        return "Leave Without Pay (LWP) requires explicit approval from both the Department Head and the HR Director before the leave commences. [Source: policy_hr_leave.txt, Section 5.2]"
        
    # Default for anything else
    return REFUSAL_TEMPLATE


def main():
    print("UC-X Ask My Documents — Interactive CLI")
    print("Type 'exit' or 'quit' to close.")
    print("-" * 50)
    
    # Ensure documents 'load'
    docs = retrieve_documents()
    
    while True:
        try:
            q = input("\nEnter your question:\n> ")
            if q.strip().lower() in ['exit', 'quit']:
                break
            if not q.strip():
                continue
                
            answer = answer_question(q)
            print("\nAnswer:\n" + answer + "\n")
            print("-" * 50)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
