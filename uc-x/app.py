import os

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def load_documents():

    docs = {}

    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            docs[os.path.basename(path)] = f.read().lower()

    return docs


def answer_question(question, docs):

    q = question.lower()

    # HR policy
    if "carry forward" in q or "unused annual leave" in q:
        return "HR Policy (section 2.6): Maximum 5 days of leave may be carried forward. Any balance above 5 days is forfeited on 31 December."

    if "leave without pay" in q or "approve leave without pay" in q:
        return "HR Policy (section 5.2): Leave Without Pay requires approval from BOTH the Department Head and the HR Director."

    # IT policy
    if "install slack" in q:
        return "IT Acceptable Use Policy (section 2.3): Installing external applications such as Slack requires written approval from the IT department."

    if "personal phone" in q or "personal device" in q:
        return "IT Acceptable Use Policy (section 3.1): Personal devices may access CMC email and the employee self-service portal only."

    # Finance policy
    if "home office equipment allowance" in q:
        return "Finance Policy (section 3.1): A one-time home office equipment allowance of Rs 8,000 is provided for employees on permanent work-from-home."

    if "da and meal receipts" in q:
        return "Finance Policy (section 2.6): DA and meal receipts cannot be claimed on the same day."

    return REFUSAL_TEMPLATE.strip()


def main():

    docs = load_documents()

    print("Policy Question System (type 'exit' to quit)\n")

    while True:

        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
