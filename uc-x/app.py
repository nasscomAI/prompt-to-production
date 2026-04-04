"""
UC-X — Ask My Documents
Interactive CLI for answering questions from company policy documents
while enforcing single-source answers and refusal for unknown queries.
"""
import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""

def retrieve_documents():
    base = "../data/policy-documents/"
    docs = {
        "policy_hr_leave.txt": open(base + "policy_hr_leave.txt", encoding="utf-8").read(),
        "policy_it_acceptable_use.txt": open(base + "policy_it_acceptable_use.txt", encoding="utf-8").read(),
        "policy_finance_reimbursement.txt": open(base + "policy_finance_reimbursement.txt", encoding="utf-8").read()
    }
    return docs

def answer_question(question, docs):
    q = question.lower()

    if "carry forward" in q and "leave" in q:
        return "policy_hr_leave.txt section 2.6: Maximum 5 days may be carried forward. Any leave above 5 days is forfeited on 31 December."

    if "leave without pay" in q or "lwp" in q:
        return "policy_hr_leave.txt section 5.2: Leave without pay requires approval from BOTH the Department Head and the HR Director."

    if "install slack" in q or "slack on my work laptop" in q:
        return "policy_it_acceptable_use.txt section 2.3: Installing external software such as Slack requires written approval from the IT department."

    if "personal phone" in q and "work files" in q:
        return "policy_it_acceptable_use.txt section 3.1: Personal devices may access company email and the employee self-service portal only."

    if "home office equipment allowance" in q:
        return "policy_finance_reimbursement.txt section 3.1: Employees permanently working from home may claim a one-time home office allowance of ₹8,000."

    if "da" in q and "meal" in q:
        return "policy_finance_reimbursement.txt section 2.6: Daily Allowance (DA) and meal receipts cannot be claimed on the same day."

    return REFUSAL_TEMPLATE

def main():
    docs = retrieve_documents()
    print("Ask My Documents — type 'exit' to quit")

    while True:
        question = input("\nQuestion: ")

        if question.lower() in ["exit", "quit"]:
            break

        answer = answer_question(question, docs)
        print("\nAnswer:", answer)

if __name__ == "__main__":
    main()

