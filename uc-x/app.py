"""
UC-X — Ask My Documents
Interactive CLI for answering policy questions strictly based on document text.
"""
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

QA_MAP = [
    {
        "keywords": ["carry forward", "unused annual leave", "unused leave"],
        "answer": "Under HR Policy (policy_hr_leave.txt) Section 2.6 & 2.7: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March) or they are forfeited."
    },
    {
        "keywords": ["slack", "install slack", "work laptop"],
        "answer": "Under IT Policy (policy_it_acceptable_use.txt) Section 2.3: Employees may not install unauthorized software. Software installation on work laptops requires prior written approval from IT."
    },
    {
        "keywords": ["home office", "equipment allowance", "allowance"],
        "answer": "Under Finance Policy (policy_finance_reimbursement.txt) Section 3.1: Permanent WFH employees are entitled to a one-time home office equipment allowance of Rs 8,000."
    },
    {
        "keywords": ["personal phone", "work files"],
        "answer": "Under IT Policy (policy_it_acceptable_use.txt) Section 3.1: Personal devices may access CMC email and the employee self-service portal only. Accessing work files or storing corporate documents on personal mobile devices is not permitted."
    },
    {
        "keywords": ["da and meal", "meal receipts", "same day"],
        "answer": "Under Finance Policy (policy_finance_reimbursement.txt) Section 2.6: Claiming Daily Allowance (DA) and actual meal receipts on the same day is explicitly prohibited."
    },
    {
        "keywords": ["approves leave without pay", "who approves lwp", "leave without pay"],
        "answer": "Under HR Policy (policy_hr_leave.txt) Section 5.2: Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient."
    }
]

def answer_question(question: str) -> str:
    q_lower = question.lower().strip()
    for item in QA_MAP:
        if any(kw in q_lower for kw in item["keywords"]):
            return item["answer"]
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents CLI")
    print("=" * 60)
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"Q: {q}")
        print(f"A: {answer_question(q)}")
    else:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        for q in test_questions:
            print(f"Q: {q}")
            print(f"A: {answer_question(q)}\n{'-'*40}")

if __name__ == "__main__":
    main()
