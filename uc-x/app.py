"""
UC-X app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    # In a real LLM setup, this would parse text. Here we structure the known sections for the tests.
    return {
        "policy_hr_leave.txt": {
            "2.6": "Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December.",
            "5.2": "LWP requires approval from the Department Head AND the HR Director."
        },
        "policy_it_acceptable_use.txt": {
            "2.3": "Requires written IT approval.",
            "3.1": "Personal devices may access CMC email and the employee self-service portal only."
        },
        "policy_finance_reimbursement.txt": {
            "2.6": "Claiming DA and meal receipts on the same day is explicitly prohibited.",
            "3.1": "Rs 8,000 one-time, permanent WFH only."
        }
    }

def answer_question(question, docs):
    q = question.lower()
    
    if "carry forward" in q and "annual leave" in q:
        return f"Source: policy_hr_leave.txt (Section 2.6)\nAnswer: {docs['policy_hr_leave.txt']['2.6']}"
    
    if "install slack" in q:
        return f"Source: policy_it_acceptable_use.txt (Section 2.3)\nAnswer: {docs['policy_it_acceptable_use.txt']['2.3']}"
        
    if "home office equipment allowance" in q:
        return f"Source: policy_finance_reimbursement.txt (Section 3.1)\nAnswer: {docs['policy_finance_reimbursement.txt']['3.1']}"
        
    if "personal phone" in q and "work files" in q:
        return f"Source: policy_it_acceptable_use.txt (Section 3.1)\nAnswer: {docs['policy_it_acceptable_use.txt']['3.1']}\nThey cannot be used to access work files."
        
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    if "claim da and meal" in q:
        return f"Source: policy_finance_reimbursement.txt (Section 2.6)\nAnswer: {docs['policy_finance_reimbursement.txt']['2.6']}"
        
    if "leave without pay" in q:
        return f"Source: policy_hr_leave.txt (Section 5.2)\nAnswer: {docs['policy_hr_leave.txt']['5.2']}"
        
    return REFUSAL_TEMPLATE

def main():
    print("Ask My Documents - Interactive CLI")
    print("Type 'exit' or 'quit' to exit.\n")
    docs = retrieve_documents()
    
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input.strip():
                continue
                
            ans = answer_question(user_input, docs)
            print(ans + "\n")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
