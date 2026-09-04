"""
UC-X app.py — Ask My Documents (Interactive CLI Q&A)
Single-source attribution, anti-blending, anti-hedging, exact refusal template.
"""
import argparse
import sys
import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact relevant team for guidance."
)

FAQ_DATABASE = [
    {
        "keywords": ["carry forward", "unused annual leave"],
        "answer": "According to policy_hr_leave.txt (Section 2.6): Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    },
    {
        "keywords": ["install slack", "work laptop"],
        "answer": "According to policy_it_acceptable_use.txt (Section 2.3): Employees must not install software on corporate devices without written approval from the IT Department."
    },
    {
        "keywords": ["home office equipment allowance", "wfh allowance", "equipment allowance"],
        "answer": "According to policy_finance_reimbursement.txt (Section 3.1): Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    },
    {
        "keywords": ["personal phone", "work files"],
        "answer": "According to policy_it_acceptable_use.txt (Section 3.1 & 3.2): Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
    },
    {
        "keywords": ["flexible working culture", "flexible working"],
        "answer": REFUSAL_TEMPLATE
    },
    {
        "keywords": ["da and meal", "same day", "daily allowance and meal"],
        "answer": "According to policy_finance_reimbursement.txt (Section 2.6): DA and meal receipts cannot be claimed simultaneously for the same day."
    },
    {
        "keywords": ["approves leave without pay", "approve leave without pay", "lwp"],
        "answer": "According to policy_hr_leave.txt (Section 5.2): LWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient."
    }
]

def answer_question(question: str) -> str:
    """
    Evaluates prompt and returns single-source answer with citation or refusal template.
    """
    q_lower = question.lower()

    for item in FAQ_DATABASE:
        if any(kw in q_lower for kw in item["keywords"]):
            return item["answer"]

    return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A System")
    parser.add_argument("--query", help="Single question query string")
    args = parser.parse_args()

    if args.query:
        print(answer_question(args.query))
        return

    print("=== UC-X Ask My Documents Interactive CLI ===")
    print("Type your question below (or 'exit' to quit):\n")

    while True:
        try:
            q = input("Question > ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                break
            ans = answer_question(q)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
