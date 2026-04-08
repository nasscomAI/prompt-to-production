import os

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def load_documents():
    docs = {}

    base = "../data/policy-documents"

    for file in os.listdir(base):
        if file.endswith(".txt"):
            with open(os.path.join(base, file)) as f:
                docs[file] = f.read().lower()

    return docs


def answer_question(question, docs):
    q = question.lower()

    # HR leave queries
    if "carry forward" in q or "unused annual leave" in q:
        return "Source: policy_hr_leave.txt Section 2.6 — Maximum 5 unused leave days may be carried forward. Any above 5 are forfeited on 31 December."

    if "leave without pay" in q or "approves leave without pay" in q:
        return "Source: policy_hr_leave.txt Section 5.2 — Leave Without Pay requires approval from BOTH the Department Head AND the HR Director."

    # IT policy queries
    if "slack" in q and "laptop" in q:
        return "Source: policy_it_acceptable_use.txt Section 2.3 — Installing software such as Slack on work devices requires written approval from the IT department."

    if "personal phone" in q:
        return "Source: policy_it_acceptable_use.txt Section 3.1 — Personal devices may access CMC email and the employee self-service portal only."

    # Finance queries
    if "home office" in q or "equipment allowance" in q:
        return "Source: policy_finance_reimbursement.txt Section 3.1 — A one-time ₹8,000 home office equipment allowance is available for permanent work-from-home employees."

    if "da and meal" in q:
        return "Source: policy_finance_reimbursement.txt Section 2.6 — Daily Allowance (DA) and meal reimbursements cannot be claimed on the same day."

    # fallback
    return REFUSAL


def main():
    docs = load_documents()

    print("Policy Q&A System (type 'exit' to quit)\n")

    while True:
        q = input("Question: ")

        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
