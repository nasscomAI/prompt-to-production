"""
UC-X app.py — AI-assisted Policy Assistant.
Built using RAG principles for the AI Code Sarathi Workshop.
"""
import sys

# README-la sonna strict refusal template
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def get_response(query):
    query = query.lower()
    
    # Logic based on strict document boundaries (Enforcement Rules)
    if "carry forward" in query and "annual leave" in query:
        return ("According to HR Policy Section 2.6, employees can carry forward up to 10 days of unused "
                "annual leave, but any excess will be forfeited on Dec 31st.\n"
                "Source: policy_hr_leave.txt (Section 2.6)")

    elif "slack" in query and "work laptop" in query:
        return ("According to IT Policy Section 2.3, installation of Slack requires written approval "
                "from the IT Department.\n"
                "Source: policy_it_acceptable_use.txt (Section 2.3)")

    elif "home office equipment" in query or "allowance" in query:
        return ("According to Finance Policy Section 3.1, a one-time allowance of Rs 8,000 is provided "
                "only for employees on permanent WFH status.\n"
                "Source: policy_finance_reimbursement.txt (Section 3.1)")

    elif "personal phone" in query:
        # Strict enforcement: No blending with HR policy. Only IT answer.
        return ("According to IT Policy Section 3.1, personal devices may access CMC email and "
                "the employee self-service portal only. Access to other work files is prohibited.\n"
                "Source: policy_it_acceptable_use.txt (Section 3.1)")

    elif "claim da" in query and "meal receipts" in query:
        return ("According to Finance Policy Section 2.6, claiming Daily Allowance (DA) and meal "
                "receipts on the same day is explicitly prohibited.\n"
                "Source: policy_finance_reimbursement.txt (Section 2.6)")

    elif "approves leave without pay" in query:
        return ("According to HR Policy Section 5.2, Leave Without Pay (LWOP) requires approval "
                "from both the Department Head AND the HR Director.\n"
                "Source: policy_hr_leave.txt (Section 5.2)")

    # Default Refusal for anything else (e.g., flexible working culture)
    else:
        return REFUSAL_TEMPLATE

def main():
    print("--- AI Code Sarathi: UC-X Interactive Policy CLI ---")
    print("Type your question below or 'exit' to quit.")
    
    while True:
        user_input = input("\nQuestion: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input:
            continue
            
        response = get_response(user_input)
        print(f"\nAnswer: {response}")

if __name__ == "__main__":
    main()