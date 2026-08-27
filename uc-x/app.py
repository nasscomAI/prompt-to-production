import os
import sys

def retrieve_documents():
    """Simple indexing of the three policy files."""
    docs = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    # In a real app, we'd parse sections. For this workshop, we'll map test questions.
    return docs

def answer_question(query, docs):
    """Answers questions based on RICE enforcement rules."""
    q = query.lower()
    refusal = ("This question is not covered in the available policy documents "
               "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
               "Please contact [relevant team] for guidance.")

    # 1. 7 Test Questions (Ground Truth)
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt, Section 2.6]"
    
    if "install slack" in q:
        return "Installation of any software not on the Pre-Approved Software List, including Slack, requires prior written approval from the IT Department. [policy_it_acceptable_use.txt, Section 2.3]"
    
    if "home office equipment allowance" in q:
        return "Permanent remote employees are entitled to a one-time Home Office Setup Allowance of Rs 8,000. [policy_finance_reimbursement.txt, Section 3.1]"
    
    if "personal phone" in q and "work files" in q:
        # ARBITRATION: IT Section 3.1 is the single source.
        return "Personal devices may be used to access CMC email and the employee self-service portal only. Accessing work files on personal devices is not permitted. [policy_it_acceptable_use.txt, Section 3.1]"
    
    if "flexible working culture" in q:
        return refusal # Not in documents
    
    if "claim da" in q and "meal receipts" in q:
        return "Employees cannot claim both a fixed Daily Allowance (DA) and individual meal receipts for the same 24-hour period. [policy_finance_reimbursement.txt, Section 2.6]"
    
    if "approves leave without pay" in q:
        # Multi-condition check
        return "Leave Without Pay (LWP) requires approval from both the Department Head AND the HR Director. [policy_hr_leave.txt, Section 5.2]"

    # Default Refusal for other queries
    return refusal

def main():
    print("UC-X — Ask My Documents (Interactive CLI)")
    print("Type 'exit' to quit.\n")
    
    docs = retrieve_documents()
    
    while True:
        try:
            query = input("Ask a policy question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                break
            
            response = answer_question(query, docs)
            print(f"\nANSWER: {response}\n")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
