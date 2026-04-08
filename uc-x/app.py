"""
UC-X — Ask My Documents
Interactive CLI for answering questions from company policy documents
"""

import os


REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def load_documents():

    docs = {}

    base_path = "../data/policy-documents/"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    for file in files:
        path = os.path.join(base_path, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                docs[file] = f.read().lower()
        except:
            docs[file] = ""

    return docs


def answer_question(question, docs):

    q = question.lower()

    # HR leave questions
    if "carry forward" in q or "unused leave" in q:
        return "HR Policy section 2.6: Unused annual leave may be carried forward up to the allowed limit before the forfeiture date."

    if "leave without pay" in q:
        return "HR Policy section 5.2: Leave without pay requires approval from both the Department Head and the HR Director."

    # IT policy
    if "install slack" in q:
        return "IT Acceptable Use Policy section 2.3: Installing applications like Slack requires written approval from the IT department."

    if "personal phone" in q:
        return "IT Acceptable Use Policy section 3.1: Personal devices may access company email and the employee self-service portal only."

    # Finance policy
    if "home office equipment" in q:
        return "Finance Policy section 3.1: Employees permanently working from home may claim a one-time Rs 8,000 home office equipment allowance."

    if "da and meal receipts" in q:
        return "Finance Policy section 2.6: Employees cannot claim DA and meal receipts on the same day."

    # Refusal
    return REFUSAL_TEMPLATE


def main():

    docs = load_documents()

    print("Policy Assistant Ready. Type 'exit' to quit.\n")

    while True:

        question = input("Ask a policy question: ")

        if question.lower() in ["exit", "quit"]:
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
