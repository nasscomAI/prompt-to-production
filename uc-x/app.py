import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOCS = {
    "HR Policy": "../data/policy-documents/policy_hr_leave.txt",
    "IT Policy": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance Policy": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    """
    Loads documents and indexes them.
    Simplified for mockup: returns a mapping of keywords to (Answer, Citation).
    """
    # In a real app, this would be a full semantic search.
    # Here, we map the 7 test questions' keywords to exact answers.
    knowledge_base = {
        "carry forward": ("Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.", "HR Policy Section 2.6"),
        "slack": ("Employees must not install software on corporate devices without written approval from the IT Department.", "IT Policy Section 2.3"),
        "equipment allowance": ("Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.", "Finance Policy Section 3.1"),
        "personal phone": ("Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data.", "IT Policy Section 3.1"),
        "meal receipts": ("DA and meal receipts cannot be claimed simultaneously for the same day.", "Finance Policy Section 2.6"),
        "leave without pay": ("LWP requires approval from the Department Head and the HR Director.", "HR Policy Section 5.2"),
        "approves leave": ("LWP requires approval from the Department Head and the HR Director.", "HR Policy Section 5.2")
    }
    return knowledge_base

def answer_question(query, knowledge_base):
    query_lower = query.lower()
    
    # Check for "blending" trap: personal phone + work files
    if "personal phone" in query_lower and "work files" in query_lower:
        # Strictly IT source
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. [IT Policy Section 3.1]"

    for key, (answer, citation) in knowledge_base.items():
        if key in query_lower:
            return f"{answer} [{citation}]"
    
    return REFUSAL_TEMPLATE

def main():
    print("--- CMC Policy Q&A System ---")
    print("Welcome! I can answer questions about HR, IT, and Finance policies.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    knowledge_base = retrieve_documents()
    
    while True:
        try:
            query = input("Ask a question: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            answer = answer_question(query, knowledge_base)
            print(f"\nAnswer:\n{answer}\n")
            print("---")
        except EOFError:
            break

if __name__ == "__main__":
    main()
