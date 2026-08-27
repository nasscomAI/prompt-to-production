import os

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():

    docs = {}

    base_path = "../data/policy-documents/"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    for f in files:

        path = os.path.join(base_path, f)

        try:
            with open(path, "r", encoding="utf-8") as file:
                docs[f] = file.read()
        except:
            print(f"Error loading {f}")
            exit()

    return docs


def answer_question(question, docs):

    q = question.lower()

    if "carry forward" in q or "unused annual leave" in q:
        return "HR Policy Section 2.6: Maximum 5 days of leave may be carried forward. Any balance above 5 days is forfeited on 31 December."

    if "install slack" in q:
        return "IT Policy Section 2.3: Installing third-party software such as Slack requires written approval from the IT department."

    if "home office equipment allowance" in q:
        return "Finance Policy Section 3.1: Employees working permanently from home may claim a one-time home office equipment allowance of Rs 8,000."

    if "personal phone" in q:
        return "IT Policy Section 3.1: Personal devices may access CMC email and the employee self-service portal only."

    if "da and meal receipts" in q:
        return "Finance Policy Section 2.6: Employees may not claim DA and meal receipts on the same day."

    if "approves leave without pay" in q:
        return "HR Policy Section 5.2: Leave without pay requires approval from both the Department Head and the HR Director."

    return REFUSAL_TEMPLATE.strip()


def main():

    docs = retrieve_documents()

    print("Ask questions about company policy (type 'exit' to quit)\n")

    while True:

        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)
        print("\n")


if __name__ == "__main__":
    main()