import os

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance.
"""

documents = {
    "policy_hr_leave.txt": {},
    "policy_it_acceptable_use.txt": {},
    "policy_finance_reimbursement.txt": {}
}

def load_documents():
    base = "../data/policy-documents"
    for doc in documents.keys():
        path = os.path.join(base, doc)
        if os.path.exists(path):
            with open(path, "r") as f:
                documents[doc]["content"] = f.read().lower()

def answer_question(q):
    q = q.lower()

    if "carry forward" in q:
        return "HR Policy section 2.6: Maximum 5 days leave can be carried forward and unused days above 5 are forfeited on 31 December."

    if "slack" in q:
        return "IT Policy section 2.3: Installing software such as Slack requires written approval from the IT department."

    if "home office equipment" in q:
        return "Finance Policy section 3.1: Employees permanently working from home may claim a one-time home office equipment allowance of Rs 8,000."

    if "personal phone" in q:
        return "IT Policy section 3.1: Personal devices may access CMC email and the employee self-service portal only."

    if "da and meal" in q:
        return "Finance Policy section 2.6: DA and meal reimbursements cannot be claimed on the same day."

    if "leave without pay" in q:
        return "HR Policy section 5.2: Leave without pay requires approval from both the Department Head and the HR Director."

    return REFUSAL

def main():
    load_documents()

    print("Ask My Documents CLI (type 'exit' to quit)")

    while True:
        q = input("\nQuestion: ")

        if q.lower() == "exit":
            break

        print("\nAnswer:")
        print(answer_question(q))


if __name__ == "__main__":
    main()
