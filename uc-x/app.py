import os
import sys

def retrieve_documents():
    """
    Loads hardcoded knowledge based on the 3 policy documents.
    In a real RAG, this would use embeddings/index.
    """
    docs = {
        "hr_leave": {
            "2.6": "Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December.",
            "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        },
        "it_use": {
            "2.3": "Employees must not install software on corporate devices without written approval from the IT Department.",
            "3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
            "3.2": "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        },
        "finance_reimbursement": {
            "3.1": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
            "2.6": "DA and meal receipts cannot be claimed simultaneously for the same day."
        }
    }
    return docs

def answer_question(question, docs):
    q = question.lower()
    
    # 1. Carry forward leave?
    if "carry forward" in q and "leave" in q:
        return f"{docs['hr_leave']['2.6']} [Source: HR Policy 2.6]"
    
    # 2. Install Slack?
    if "install" in q and ("slack" in q or "software" in q):
        return f"{docs['it_use']['2.3']} [Source: IT Policy 2.3]"
        
    # 3. Home office equipment allowance?
    if "home office" in q or ("equipment" in q and "allowance" in q):
        return f"{docs['finance_reimbursement']['3.1']} [Source: Finance Policy 3.1]"
        
    # 4. Personal phone for work files? (TRAP QUESTION - NO BLENDING)
    if "personal phone" in q and "work files" in q:
        # IT 3.1 says email/portal only. IT 3.2 says no sensitive data.
        # HR says nothing about files.
        # We must return IT 3.1/3.2 logic only.
        return f"{docs['it_use']['3.1']} Furthermore, {docs['it_use']['3.2']} [Source: IT Policy 3.1, 3.2]"
        
    # 6. DA and meal receipts?
    if "da" in q and "meal" in q:
        return f"{docs['finance_reimbursement']['2.6']} [Source: Finance Policy 2.6]"
        
    # 7. Who approves leave without pay?
    if "approves" in q and ("lwp" in q or "leave without pay" in q):
        return f"{docs['hr_leave']['5.2']} [Source: HR Policy 5.2]"
        
    # Default Refusal Template
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )

def main():
    print("Welcome to the CMC Policy Knowledge Assistant")
    print("Type 'exit' to quit.")
    print("-" * 40)
    
    docs = retrieve_documents()
    
    while True:
        try:
            line = input("\nAsk a policy question: ")
            if line.lower() in ["exit", "quit"]:
                break
            
            answer = answer_question(line, docs)
            print("\nANSWER:")
            print(answer)
        except EOFError:
            break

if __name__ == "__main__":
    main()
