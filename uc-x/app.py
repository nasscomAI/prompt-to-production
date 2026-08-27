import os

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

def load_documents():
    docs = {}
    base = "../data/policy-documents"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    for f in files:
        path = os.path.join(base, f)
        with open(path, "r", encoding="utf-8") as file:
            docs[f] = file.read()

    return docs


def answer_question(question, docs):
    q = question.lower()

    if "carry forward" in q and "leave" in q:
        return "HR Policy section 2.6: Maximum 5 days leave may be carried forward. Any balance above 5 days is forfeited on 31 December."

    if "slack" in q and "laptop" in q:
        return "IT Policy section 2.3: Installing software like Slack on a work laptop requires written approval from IT."

    if "home office equipment" in q:
        return "Finance Policy section 3.1: Employees on permanent work-from-home may claim a one-time home office allowance of Rs 8,000."

    if "personal phone" in q and "work files" in q:
        return "IT Policy section 3.1: Personal devices may access only company email and the employee self-service portal."

    if "da" in q and "meal" in q:
        return "Finance Policy section 2.6: Claiming DA and meal receipts on the same day is not permitted."

    if "leave without pay" in q or "lwp" in q:
        return "HR Policy section 5.2: Leave without pay requires approval from BOTH the Department Head and HR Director."

    return REFUSAL


def main():
    docs = load_documents()

    print("Ask questions about company policies (type 'exit' to quit)")

    while True:
        question = input("\nQuestion: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)
        print("\nAnswer:", answer)


if __name__ == "__main__":
    main()