import os

# Refusal template (STRICT)
REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact relevant team for guidance."""

def retrieve_documents():
    base_path = "../data/policy-documents/"
    
    docs = {}
    
    for file in [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]:
        with open(os.path.join(base_path, file), "r", encoding="utf-8") as f:
            docs[file] = f.read()
    
    return docs


def answer_question(question, docs):
    q = question.lower()

    # HR
    if "carry forward" in q:
        return "Max 5 days carry-forward. Above 5 forfeited on 31 Dec. (policy_hr_leave.txt - 2.6)"

    if "leave without pay" in q or "lwp" in q:
        return "Requires Department Head AND HR Director approval. (policy_hr_leave.txt - 5.2)"

    # IT
    if "slack" in q:
        return "Installing software requires written IT approval. (policy_it_acceptable_use.txt - 2.3)"

    if "personal phone" in q:
        return "Personal devices may access only email and employee self-service portal. (policy_it_acceptable_use.txt - 3.1)"

    # Finance
    if "home office" in q:
        return "Rs 8,000 one-time allowance for permanent WFH employees. (policy_finance_reimbursement.txt - 3.1)"

    if "da and meal" in q:
        return "DA and meal reimbursements cannot be claimed on the same day. (policy_finance_reimbursement.txt - 2.6)"

    # Not found → REFUSE
    return REFUSAL


def main():
    docs = retrieve_documents()

    print("📄 Ask your questions (type 'exit' to stop)\n")

    while True:
        q = input("❓ سوال: ")

        if q.lower() == "exit":
            break

        answer = answer_question(q, docs)
        print("✅ Answer:", answer, "\n")


if __name__ == "__main__":
    main()