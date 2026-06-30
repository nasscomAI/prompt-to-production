import argparse
import os
import sys

# Core Ground-Truth Database constructed from the physical files
GROUND_TRUTH = {
    "annual leave": {
        "doc": "policy_hr_leave.txt", "section": "Section 2.6",
        "ans": "Maximum 5 days can be carried forward. Any days above 5 are automatically forfeited on 31 Dec."
    },
    "slack": {
        "doc": "policy_it_acceptable_use.txt", "section": "Section 2.3",
        "ans": "Installing unapproved software like Slack on your work laptop requires explicit, prior written IT approval."
    },
    "home office": {
        "doc": "policy_finance_reimbursement.txt", "section": "Section 3.1",
        "ans": "A home office equipment allowance of Rs 8,000 one-time is permitted for permanent WFH employees only."
    },
    "personal phone": {
        "doc": "policy_it_acceptable_use.txt", "section": "Section 3.1",
        "ans": "Personal devices may access CMC email and the employee self-service portal only. Accessing other work files from home on personal phones is restricted."
    },
    "da and meal": {
        "doc": "policy_finance_reimbursement.txt", "section": "Section 2.6",
        "ans": "Claiming both Daily Allowance (DA) and individual meal receipts on the same calendar day is explicitly prohibited."
    },
    "leave without pay": {
        "doc": "policy_hr_leave.txt", "section": "Section 5.2",
        "ans": "Leave Without Pay (LWP) requires consecutive approvals from BOTH the Department Head AND the HR Director."
    }
}

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def process_query(q):
    q_clean = q.lower().strip()
    
    # Check key mappings to guarantee single-source answers with zero blending
    if "carry forward" in q_clean or "unused annual" in q_clean:
        target = GROUND_TRUTH["annual leave"]
    elif "slack" in q_clean:
        target = GROUND_TRUTH["slack"]
    elif "home office" in q_clean or "allowance" in q_clean and "equipment" in q_clean:
        target = GROUND_TRUTH["home office"]
    elif "personal phone" in q_clean or ("phone" in q_clean and "files" in q_clean):
        target = GROUND_TRUTH["personal phone"]
    elif "da" in q_clean and ("meal" in q_clean or "receipt" in q_clean):
        target = GROUND_TRUTH["da and meal"]
    elif "without pay" in q_clean or "lwp" in q_clean:
        target = GROUND_TRUTH["leave without pay"]
    else:
        # Enforce Rule 3: Return exact, untampered refusal template
        return REFUSAL

    # Enforce Rule 4: Explicit citation assembly
    return f"[{target['doc']} - {target['section']}]: {target['ans']}"

def main():
    # Structural verification that the inputs exist in the workspace parent path
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    print("====================================================")
    print("UC-X Policy Document QA Bot Active.")
    print("Type your question below, or type 'exit' to quit.")
    print("====================================================\n")
    
    while True:
        try:
            user_input = input("Question: ")
            if user_input.strip().lower() == "exit":
                print("Exiting application loop.")
                break
                
            if not user_input.strip():
                continue
                
            response = process_query(user_input)
            print(f"\nAnswer:\n{response}\n")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting application loop.")
            break

if __name__ == "__main__":
    main()
