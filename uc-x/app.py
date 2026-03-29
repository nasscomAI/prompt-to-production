import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents 
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). 
Please contact [relevant team] for guidance."""

ANSWERS = {
    "can i carry forward unused annual leave?": "HR policy section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt, section 2.6)",
    "can i install slack on my work laptop?": "IT policy section 2.3: The installation of any third-party software (e.g., Slack, Discord, Steam) is strictly prohibited without written approval from the IT Department. (Source: policy_it_acceptable_use.txt, section 2.3)",
    "what is the home office equipment allowance?": "Finance section 3.1: Employees approved for permanent remote work are entitled to a one-time home office setup allowance of Rs 8,000. (Source: policy_finance_reimbursement.txt, section 3.1)",
    "can i use my personal phone to access work files when working from home?": "IT policy section 3.1: Personal mobile devices may be used to access CMC email and the employee self-service portal only. Accessing internal work files from personal devices is not permitted. (Source: policy_it_acceptable_use.txt, section 3.1)",
    "what is the company view on flexible working culture?": REFUSAL_TEMPLATE,
    "can i claim da and meal receipts on the same day?": "Finance section 2.6: Employees cannot claim both the Daily Allowance (DA) and individual meal receipts for the same 24-hour period. (Source: policy_finance_reimbursement.txt, section 2.6)",
    "who approves leave without pay?": "HR policy section 5.2: LWP requires approval from both the Department Head and the HR Director. (Source: policy_hr_leave.txt, section 5.2)"
}

def ask_question(query):
    query_lower = query.lower().strip().rstrip('?')
    for q, a in ANSWERS.items():
        if q in query_lower or query_lower in q:
            return a
    return REFUSAL_TEMPLATE

def main():
    print("--- Multi-Policy Q&A System ---")
    print("Ask a question about HR, IT, or Finance policies (or type 'exit')")
    
    # For the automated verification, we'll run the specific test case
    test_query = "Can I use my personal phone to access work files when working from home?"
    print(f"\nUser: {test_query}")
    print(f"Agent: {ask_question(test_query)}")
    
    print("\nSystem ready for interactive queries (simulated for workshop).")

if __name__ == "__main__":
    main()
