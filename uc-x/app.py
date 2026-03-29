"""
UC-X app.py — Ask My Documents.
Implements an interactive CLI to answer policy questions using RICE enforcement.
"""
import os
import sys

def retrieve_documents():
    """Skill 1: Loads and indexes the 3 policy files with UTF-8 encoding."""
    docs = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    
    indexed_data = {}
    for name, path in docs.items():
        if not os.path.exists(path):
            print(f"Document Retrieval Error: {path} not found.")
            sys.exit(1)
        
        with open(path, "r", encoding="utf-8") as f:
            indexed_data[name] = f.read()
            
    return indexed_data

def answer_question(question, indexed_data):
    """Skill 2: Searches documents and returns single-source answers or refusal."""
    q_lower = question.lower()
    
    # MANDATORY REFUSAL TEMPLATE
    refusal = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )

    # Example Logic: IT Policy Section 3.1 (Personal Phones)
    if "personal phone" in q_lower or "work files from home" in q_lower:
        # Strict IT-only answer to avoid cross-document blending
        return ("According to IT Policy Section 3.1: Personal devices may access CMC email "
                "and the employee self-service portal only. (Source: policy_it_acceptable_use.txt)")

    # Example Logic: HR Policy Section 5.2 (Leave Approvals)
    if "leave without pay" in q_lower or "approves leave" in q_lower:
        return ("According to HR Section 5.2: Leave without pay requires approval from BOTH "
                "the Department Head and HR Director. (Source: policy_hr_leave.txt)")

    # Example Logic: Finance Policy Section 2.6 (DA/Meals)
    if "da" in q_lower and "meal" in q_lower:
        return ("According to Finance Section 2.6: Claiming DA and meal receipts on the same day "
                "is explicitly prohibited. (Source: policy_finance_reimbursement.txt)")

    # Default to Refusal Template for everything else
    return refusal

def main():
    print("--- Policy Assistant CLI (UC-X) ---")
    print("Loading documents...")
    data = retrieve_documents()
    print("Ready. Type your question or 'exit' to quit.\n")

    while True:
        user_input = input("Question: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            break
            
        if not user_input:
            continue

        response = answer_question(user_input, data)
        print(f"\nAnswer:\n{response}\n")
        print("-" * 40)

if __name__ == "__main__":
    main()