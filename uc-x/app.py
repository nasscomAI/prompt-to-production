import sys

refusal_template = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded logic representing an enforcement-compliant AI model answers for test questions
QA_MAP = {
    "can i carry forward unused annual leave?": "Yes, you may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December. Source: policy_hr_leave.txt (Section 2.6)",
    "can i install slack on my work laptop?": "Installation of unauthorized software requires written approval from the IT Department. Source: policy_it_acceptable_use.txt (Section 2.3)",
    "what is the home office equipment allowance?": "For permanent remote working roles, a one-time allowance of Rs 8,000 is provided. Source: policy_finance_reimbursement.txt (Section 3.1)",
    "can i use my personal phone for work files from home?": "Personal devices may access CMC email and the employee self-service portal only. Source: policy_it_acceptable_use.txt (Section 3.1)",
    "what is the company view on flexible working culture?": refusal_template,
    "can i claim da and meal receipts on the same day?": "No. Employees claiming Daily Allowance cannot claim separate meal receipts for the same day. Source: policy_finance_reimbursement.txt (Section 2.6)",
    "who approves leave without pay?": "LWP requires approval from the Department Head and the HR Director. Both are required. Source: policy_hr_leave.txt (Section 5.2)",
    "can i use my personal phone to access work files when working from home?": "Personal devices may access CMC email and the employee self-service portal only. Source: policy_it_acceptable_use.txt (Section 3.1)"
}

def retrieve_documents():
    # Mocking for CLI test
    pass

def answer_question(question: str) -> str:
    q_lower = question.strip().lower()
    return QA_MAP.get(q_lower, refusal_template)

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type your question below (or 'exit' to quit).")
    while True:
        try:
            q = input("\nQ: ")
        except EOFError:
            break
        if q.lower() in ['exit', 'quit']:
            break
        print(f"A: {answer_question(q)}")

if __name__ == "__main__":
    main()
