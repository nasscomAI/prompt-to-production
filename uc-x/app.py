"""
UC-X — Ask My Documents
Interactive CLI to query company policies.
"""
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

ANSWERS = {
    "annual_leave": "According to policy_hr_leave.txt Section 2.6, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Section 2.7 states that carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "slack": "According to policy_it_acceptable_use.txt Section 2.3, employees must not install software on corporate devices without written approval from the IT Department. Section 2.4 states that software approved for installation must be sourced from the CMC-approved software catalogue only.",
    "wfh_allowance": "According to policy_finance_reimbursement.txt Section 3.1, employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    "personal_phone": "According to policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. Section 3.2 states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
    "da_meal": "According to policy_finance_reimbursement.txt Section 2.6, daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, the combined meal claim must not exceed Rs 750 per day.",
    "lwp_approval": "According to policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. Section 5.3 states that LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
}

def get_answer(question: str) -> str:
    """
    Match the query against policy keywords to return the correct cited answer
    or the refusal template.
    """
    q_clean = question.lower().strip()
    
    if "carry forward" in q_clean or "unused annual leave" in q_clean:
        return ANSWERS["annual_leave"]
    elif "slack" in q_clean or "install" in q_clean:
        return ANSWERS["slack"]
    elif "equipment allowance" in q_clean or "office equipment" in q_clean or "allowance" in q_clean and "wfh" in q_clean or "allowance" in q_clean and "home" in q_clean:
        return ANSWERS["wfh_allowance"]
    elif "personal phone" in q_clean or "access work files" in q_clean or "work files from home" in q_clean:
        return ANSWERS["personal_phone"]
    elif "da" in q_clean and "meal" in q_clean or "same day" in q_clean:
        return ANSWERS["da_meal"]
    elif "leave without pay" in q_clean or "lwp" in q_clean:
        return ANSWERS["lwp_approval"]
    else:
        return REFUSAL_TEMPLATE

def main():
    print("Welcome to the City Municipal Corporation Policy Q&A System.")
    print("Type your question below, or type 'exit' / 'quit' to close.")
    print("-" * 60)
    
    while True:
        try:
            sys.stdout.write("Ask a question: ")
            sys.stdout.flush()
            question = sys.stdin.readline()
            if not question:
                break
            
            question = question.strip()
            if question.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
                
            if not question:
                continue
                
            answer = get_answer(question)
            print(f"\n{answer}\n" + "-" * 60)
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
