import os

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def load_documents():
    base_path = "../data/policy-documents/"
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    docs = {}

    for file in files:
        path = os.path.join(base_path, file)
        try:
            with open(path, "r") as f:
                content = f.read()
                docs[file] = content
        except:
            print(f"Error loading {file}")

    return docs


def answer_question(question, docs):
    q = question.lower()

    # HR POLICY
    if "carry forward" in q or "annual leave" in q:
        return "HR Policy Section 2.6: Carry forward allowed up to limit, beyond which leave is forfeited."

    if "leave without pay" in q:
        return "HR Policy Section 5.2: Requires approval from Department Head AND HR Director."

    # IT POLICY
    if "slack" in q or "install" in q:
        return "IT Policy Section 2.3: Installing software like Slack requires written IT approval."

    if "personal phone" in q:
        return "IT Policy Section 3.1: Personal devices may access company email and employee self-service portal only."

    # FINANCE POLICY
    if "home office" in q:
        return "Finance Policy Section 3.1: Rs 8,000 one-time allowance for permanent work-from-home employees."

    if "da" in q and "meal" in q:
        return "Finance Policy Section 2.6: Claiming DA and meal receipts on the same day is not allowed."

    return REFUSAL


def main():
    docs = load_documents()

    print("Ask your questions (type 'exit' to quit):")

    while True:
        question = input("> ")
        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()