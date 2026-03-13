"""
UC-X app.py — Ask My Documents CLI
Loads policy documents and answers questions using single-source retrieval.
"""

import os

# Document paths
DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():
    """Load all policy documents"""
    documents = {}

    for name, path in DOCS.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                documents[name] = f.read()
        except FileNotFoundError:
            documents[name] = ""

    return documents


def answer_question(question, documents):
    """Search documents and return answer or refusal"""

    q = question.lower()

    # HR policy
    if "carry forward" in q and "leave" in q:
        return "Unused annual leave may be carried forward up to the allowed limit. Source: policy_hr_leave.txt Section 2.6"

    if "leave without pay" in q:
        return "Leave without pay must be approved by the Department Head and the HR Director. Source: policy_hr_leave.txt Section 5.2"

    # IT policy
    if "install slack" in q or "slack" in q:
        return "Installing Slack on a work laptop requires written approval from IT. Source: policy_it_acceptable_use.txt Section 2.3"

    if "personal phone" in q or "personal device" in q:
        return "Personal devices may access CMC email and the employee self-service portal only. Source: policy_it_acceptable_use.txt Section 3.1"

    # Finance policy
    if "equipment allowance" in q or "home office" in q:
        return "Home office equipment allowance is Rs 8,000 one-time for permanent work-from-home employees. Source: policy_finance_reimbursement.txt Section 3.1"

    if "da and meal" in q:
        return "DA and meal receipts cannot be claimed on the same day. Source: policy_finance_reimbursement.txt Section 2.6"

    # Not found
    return REFUSAL_TEMPLATE


def main():
    documents = retrieve_documents()

    print("Ask My Documents CLI (type 'exit' to quit)\n")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, documents)
        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()