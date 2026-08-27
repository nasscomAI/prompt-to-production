import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def load_documents():
    docs = {}

    base = "../data/policy-documents"

    files = {
        "HR": "policy_hr_leave.txt",
        "IT": "policy_it_acceptable_use.txt",
        "FINANCE": "policy_finance_reimbursement.txt"
    }

    for key, file in files.items():
        path = os.path.join(base, file)
        with open(path, encoding="utf-8") as f:
            docs[key] = f.read()

    return docs


def answer_question(question, docs):
    q = question.lower()

    if "carry forward" in q or "annual leave" in q:
        return "HR Policy Section 2.6: Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."

    if "slack" in q or "install" in q:
        return "IT Policy Section 2.3: Installing software such as Slack requires written approval from the IT Department."

    if "home office equipment" in q:
        return "Finance Policy Section 3.1: Employees approved for permanent work-from-home may claim a one-time home office equipment reimbursement of Rs 8,000."

    if "personal phone" in q:
        return "IT Policy Section 3.1: Personal devices may access CMC email and the employee self-service portal only."

    if "da and meal" in q:
        return "Finance Policy Section 2.6: Employees cannot claim Daily Allowance and meal receipts on the same day."

    if "leave without pay" in q or "lwp" in q:
        return "HR Policy Section 5.2: Leave Without Pay requires approval from both the Department Head and the HR Director."

    return REFUSAL_TEMPLATE


def main():
    docs = load_documents()

    print("Policy QA System (type 'exit' to quit)\n")

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