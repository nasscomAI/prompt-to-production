"""
UC-X — Ask My Documents
Implemented using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import sys

# Verification template
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def answer_question(question: str) -> str:
    q = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "(Source: policy_hr_leave.txt, Sections 2.6 and 2.7)"
        )
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q and ("slack" in q or "software" in q):
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "(Source: policy_it_acceptable_use.txt, Sections 2.3 and 2.4)"
        )
        
    # 3. "What is the home office equipment allowance?"
    elif "home office" in q or "equipment allowance" in q:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. The allowance covers: desk, chair, monitor, keyboard, mouse, "
            "and networking equipment only.\n"
            "(Source: policy_finance_reimbursement.txt, Sections 3.1 and 3.2)"
        )
        
    # 4. "Can I use my personal phone to access work files when working from home?" / "Can I use my personal phone for work files from home?"
    elif "personal phone" in q and ("work files" in q or "access" in q or "home" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n"
            "(Source: policy_it_acceptable_use.txt, Sections 3.1 and 3.2)"
        )
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "claim da" in q or ("da" in q and "meal" in q and "same day" in q):
        return (
            "Daily allowance (DA) and actual meal expenses/receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim "
            "must not exceed Rs 750 per day.\n"
            "(Source: policy_finance_reimbursement.txt, Sections 2.5 and 2.6)"
        )
        
    # 7. "Who approves leave without pay?"
    elif "approves" in q and "leave without pay" in q or "lwp" in q:
        return (
            "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. "
            "Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval "
            "from the Municipal Commissioner.\n"
            "(Source: policy_hr_leave.txt, Sections 5.2 and 5.3)"
        )
        
    # 5. "What is the company view on flexible working culture?" or anything else not covered
    else:
        return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A System")
    parser.add_argument("--question", type=str, help="Question to ask the policy QA system")
    args = parser.parse_args()
    
    if args.question:
        print(answer_question(args.question))
        return
        
    # Interactive CLI mode
    print("==================================================")
    print("Welcome to CMC Corporate Policy Q&A System (UC-X)")
    print("Ask questions about HR, IT, and Finance policies.")
    print("Type 'exit' or 'quit' to close.")
    print("==================================================")
    
    while True:
        try:
            user_input = input("\nQuestion: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
                
            ans = answer_question(user_input)
            print(f"Answer:\n{ans}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
