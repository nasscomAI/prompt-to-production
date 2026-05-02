import argparse
import sys

def get_policy_answer(question):
    """
    Simulates the Agentic Retrieval Skill defined in skills.md.
    """
    q = question.lower()
    
    # THE REFUSAL TEMPLATE (Must be verbatim from agents.md)
    refusal_msg = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact [relevant team] for guidance."
    )

    # TRAP 1: The Personal Phone Question (IT Section 3.1 only)
    if "personal phone" in q and "work files" in q:
        return "IT Policy Section 3.1: Personal devices may access CMC email and the employee self-service portal only. Accessing work files is not mentioned."

    # TRAP 2: Flexible Culture (Not in docs)
    elif "flexible" in q or "culture" in q:
        return refusal_msg

    # TRAP 3: Leave Approval (HR Section 5.2 - Dual Approval)
    elif "approve" in q and "leave" in q:
        return "HR Policy Section 5.2: Leave without pay (LWP) requires approval from BOTH the Department Head AND HR Director."

    # TRAP 4: DA/Meal Receipts (Finance Section 2.6 - Explicit Prohibit)
    elif "da" in q and "meal" in q:
        return "Finance Policy Section 2.6: Claiming Daily Allowance (DA) and meal receipts on the same day is explicitly prohibited."

    else:
        return refusal_msg

def main():
    print("--- Policy Assistant CLI (UC-X) ---")
    print("Type your question below. Type 'exit' to quit.")
    
    while True:
        user_q = input("\nYour Question: ")
        if user_q.lower() in ['exit', 'quit']:
            break
        
        answer = get_policy_answer(user_q)
        print(f"\nANSWER: {answer}")

if __name__ == "__main__":
    main()
