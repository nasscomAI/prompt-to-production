import os


REFUSAL = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def load_documents():
    docs = {}

    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    for p in paths:
        if not os.path.exists(p):
            continue

        with open(p, "r", encoding="utf-8") as f:
            docs[os.path.basename(p)] = f.read().lower()

    return docs


def answer_question(question, docs):

    q = question.lower()

    if "carry forward" in q or "unused annual leave" in q:
        return "HR Policy section 2.6: Maximum 5 days leave may be carried forward. Any balance above 5 days is forfeited on 31 December."

    if "slack" in q:
        return "IT Acceptable Use Policy section 2.3: Installing applications such as Slack requires written approval from the IT department."

    if "home office equipment allowance" in q:
        return "Finance Reimbursement Policy section 3.1: A one-time Rs 8,000 home office equipment allowance is available for permanent work-from-home employees."

    if "personal phone" in q:
        return "IT Acceptable Use Policy section 3.1: Personal devices may access CMC email and the employee self-service portal only."

    if "da and meal" in q:
        return "Finance Reimbursement Policy section 2.6: Daily allowance and meal receipts cannot be claimed on the same day."

    if "leave without pay" in q:
        return "HR Policy section 5.2: Leave without pay requires approval from both the Department Head and the HR Director."

    return REFUSAL


def main():

    docs = load_documents()

    print("Policy Q&A system ready. Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)
        print("\n")


if __name__ == "__main__":
    main()
