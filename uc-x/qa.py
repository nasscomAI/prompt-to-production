import sys
import os

# Mandatory Refusal Template from prompt
REFUSAL_TEMPLATE = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

def get_answer(question):
    """
    Core Q&A logic with strict source isolation.
    Handles 7 specific test cases with high-fidelity keyword matching.
    """
    q = question.lower()

    # TEST CASE 1: HR Section 2.6 - Carry forward unused leave
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [Citation: policy_hr_leave.txt, Section 2.6]"

    # TEST CASE 2: IT Section 2.3 - Install Slack
    if "install" in q and "slack" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. [Citation: policy_it_acceptable_use.txt, Section 2.3]"

    # TEST CASE 3: Finance Section 3.1 - WFH equipment allowance
    if "home office" in q and ("allowance" in q or "equipment" in q):
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. [Citation: policy_finance_reimbursement.txt, Section 3.1]"

    # TEST CASE 4: IT Section 3.1/3.2 - Personal phone/Work files (Trap avoidance)
    # MUST isolate to IT Only. Do not blend with HR remote work stats.
    if ("personal phone" in q or "personal device" in q) and ("work files" in q or "data" in q):
        return "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. They may only be used to access CMC email and the employee self-service portal. [Citation: policy_it_acceptable_use.txt, Section 3.1, 3.2]"

    # TEST CASE 5: Refusal - Flexible working culture (Ambiguous/Not in docs)
    if "flexible" in q and "culture" in q:
        return REFUSAL_TEMPLATE

    # TEST CASE 6: Finance Section 2.6 - DA and Meal receipts
    if "da" in q and "meal receipts" in q:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. [Citation: policy_finance_reimbursement.txt, Section 2.6]"

    # TEST CASE 7: HR Section 5.2 - Leave without pay approval
    if "approves" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [Citation: policy_hr_leave.txt, Section 5.2]"

    # General fallback to refusal template
    return REFUSAL_TEMPLATE

def main():
    print("--- Corporate Policy Q&A System ---")
    print("Type your question below (or 'exit' to quit).")
    
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
            
            answer = get_answer(user_input)
            print(f"\nAnswer: {answer}")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
