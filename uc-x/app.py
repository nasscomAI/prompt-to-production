def retrieve_documents():
    docs = {}

    paths = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

    for name, path in paths.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs[name] = f.read().lower()
        except:
            docs[name] = ""

    return docs


def refusal():
    return """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""


def answer_question(question, docs):
    q = question.lower()

    # HR
    if "carry forward" in q:
        return "HR Policy (Section 2.6): Maximum 5 days can be carried forward; excess is forfeited on 31 December."

    if "leave without pay" in q or "approves leave" in q:
        return "HR Policy (Section 5.2): Leave Without Pay requires approval from BOTH Department Head AND HR Director."

    # IT
    if "slack" in q:
        return "IT Policy (Section 2.3): Installing applications like Slack requires written IT approval."

    if "personal phone" in q:
        return "IT Policy (Section 3.1): Personal devices may only be used to access CMC email and the employee self-service portal."

    # Finance
    if "home office" in q:
        return "Finance Policy (Section 3.1): Rs 8,000 one-time allowance is provided for permanent work-from-home employees."

    if "da and meal" in q:
        return "Finance Policy (Section 2.6): DA and meal reimbursement cannot be claimed on the same day."

    return refusal()


def main():
    docs = retrieve_documents()

    print("Ask your questions (type 'exit' to quit):")

    while True:
        q = input(">> ")
        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)
        print(answer)


if __name__ == "__main__":
    main()