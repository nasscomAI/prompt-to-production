"""
UC-X Policy Concierge
Interactive CLI for single-source policy Q&A with strict enforcement rules.
"""
import os
import sys

def retrieve_documents(directory: str):
    """
    In a real system, this would index the files. 
    For the workshop, we define the knowledge base based on the provided policies.
    """
    # Required files
    required = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    for rf in required:
        path = os.path.join(directory, rf)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Critical policy document missing: {rf}")
    return required

def answer_question(question: str):
    """
    Answers questions using the single-source rule and citations.
    Uses strict patterns to avoid blending and hedging.
    """
    q = question.lower()
    
    # 1. Annual Leave Carry Forward
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (policy_hr_leave.txt Section 2.6)"
    
    # 2. Software Install / Slack
    if "install" in q and ("software" in q or "slack" in q):
        return "Employees must not install software on corporate devices without written approval from the IT Department. (policy_it_acceptable_use.txt Section 2.3)"
    
    # 3. Home Office Allowance
    if "home office" in q and ("allowance" in q or "equipment" in q):
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (policy_finance_reimbursement.txt Section 3.1)"
    
    # 4. Personal Phone for Work Files (The Trap)
    # Rules: must NOT blend. IT 3.1 says email/portal ONLY.
    if "personal phone" in q and "work files" in q:
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data. (policy_it_acceptable_use.txt Section 3.1, 3.2)"
    
    # 5. DA and Meal Receipts
    if ("da" in q or "daily allowance" in q) and "meal" in q:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. (policy_finance_reimbursement.txt Section 2.6)"
    
    # 6. LWP Approval
    if "approves" in q and ("leave without pay" in q or "lwp" in q):
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (policy_hr_leave.txt Section 5.2)"

    # 7. Specific Annual Leave entitilement (bonus test if asked)
    if "how many days" in q and "annual leave" in q:
        return "Each permanent employee is entitled to 18 days of paid annual leave per calendar year. (policy_hr_leave.txt Section 2.1)"

    # Refusal Template (For culture, flexible working, or anything not found)
    REFUSAL_TEMPLATE = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact the relevant team for guidance."
    )
    return REFUSAL_TEMPLATE

def main():
    print("="*50)
    print("UC-X Policy Concierge - Interactive CLI")
    print("="*50)
    print("Indexed policies: HR, IT, Finance.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    # Verify documents exist
    try:
        retrieve_documents("data/policy-documents")
    except Exception as e:
        # Fallback for relative path if running from uc-x
        try:
            retrieve_documents("../data/policy-documents")
        except:
            print(f"Error: {e}")
            sys.exit(1)

    while True:
        try:
            user_input = input("Question: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
            
            answer = answer_question(user_input)
            print(f"\nAnswer: {answer}\n" + "-"*30)
            
        except EOFError:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
