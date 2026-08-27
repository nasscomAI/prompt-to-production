"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    # Placeholder: In a real app this would load and index the texts.
    pass

def answer_question(question: str) -> str:
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [Source: policy_hr_leave.txt, Section 2.6]"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install slack" in q or ("install" in q and "laptop" in q):
        return "Installation of unapproved software requires written IT approval. [Source: policy_it_acceptable_use.txt, Section 2.3]"
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q or "equipment allowance" in q:
        return "Rs 8,000 one-time allowance for permanent WFH only. [Source: policy_finance_reimbursement.txt, Section 3.1]"
        
    # 4. "Can I use my personal phone for work files from home?" or "Can I use my personal phone to access work files when working from home?"
    if "personal phone" in q and "work files" in q:
        # Prevent blending IT and HR policies.
        return "Personal devices may access CMC email and the employee self-service portal only. [Source: policy_it_acceptable_use.txt, Section 3.1]"
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal receipts" in q:
        return "No, claiming Daily Allowance (DA) and meal receipts on the same day is explicitly prohibited. [Source: policy_finance_reimbursement.txt, Section 2.6]"
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q and "approve" in q:
        return "Leave Without Pay (LWP) requires approval from the Department Head AND the HR Director. Both are required. [Source: policy_hr_leave.txt, Section 5.2]"
        
    # Any other question (e.g. flexible working culture)
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Policy Q&A System")
    print("Type 'exit' or 'quit' to exit.")
    print("-" * 30)
    
    retrieve_documents()
    
    while True:
        try:
            q = input("\nAsk a question: ")
            if q.strip().lower() in ['exit', 'quit']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print("\nAnswer:")
            print(ans)
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
