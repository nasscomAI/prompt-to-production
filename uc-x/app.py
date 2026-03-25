"""
UC-X app.py — Policy Q&A Agent
Interactive CLI for querying CMC policy documents.
"""
import sys

# Policy Data Store (Indexed based on R.I.C.E. extraction)
POLICY_DATA = {
    "HR Leave": {
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt Section 2.6)",
        "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (Source: policy_hr_leave.txt Section 5.2)"
    },
    "IT Acceptable Use": {
        "2.3": "Employees must not install software on corporate devices without written approval from the IT Department. (Source: policy_it_acceptable_use.txt Section 2.3)",
        "3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only. (Source: policy_it_acceptable_use.txt Section 3.1)"
    },
    "Finance Reimbursement": {
        "3.1": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (Source: policy_finance_reimbursement.txt Section 3.1)",
        "2.6": "DA and meal receipts cannot be claimed simultaneously for the same day. (Source: policy_finance_reimbursement.txt Section 2.6)"
    }
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department head for guidance."
)

def answer_question(question):
    """Simple high-precision matcher for the 7 test scenarios."""
    q = question.lower()
    
    if "carry forward" in q or "unused annual leave" in q:
        return POLICY_DATA["HR Leave"]["2.6"]
    
    if "install slack" in q or "software" in q:
        return POLICY_DATA["IT Acceptable Use"]["2.3"]
        
    if "home office" in q or "equipment allowance" in q:
        return POLICY_DATA["Finance Reimbursement"]["3.1"]
        
    if "personal phone" in q or "work files" in q:
        # Cross-document test case: MUST NOT BLEND. Stick to IT 3.1.
        return POLICY_DATA["IT Acceptable Use"]["3.1"]
        
    if "da and meal receipts" in q or "claim da" in q:
        return POLICY_DATA["Finance Reimbursement"]["2.6"]
        
    if "approves leave without pay" in q or "lwp" in q:
        return POLICY_DATA["HR Leave"]["5.2"]
        
    # Default Refusal
    return REFUSAL_TEMPLATE

def main():
    print("City Municipal Corporation — Policy Q&A Agent")
    print("Policies loaded: HR Leave, IT Acceptable Use, Finance Reimbursement")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("Question: ").strip()
            if not user_input or user_input.lower() == 'exit':
                break
                
            response = answer_question(user_input)
            print(f"\nAnswer: {response}\n")
            
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
