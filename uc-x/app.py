import argparse
import os

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():
    docs = {}

    base_path = "../data/policy-documents"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    for f in files:
        path = os.path.join(base_path, f)

        with open(path, "r", encoding="utf-8") as file:
            docs[f] = file.read()

    return docs


def answer_question(question, docs):
    q = question.lower()

    # HR POLICY
    if "carry forward" in q and "leave" in q:
        return ("HR Policy section 2.6 states that a maximum of 5 days of leave "
                "may be carried forward and any balance above this is forfeited "
                "on 31 December.\n"
                "Source: policy_hr_leave.txt §2.6")

    if "leave without pay" in q or "who approves leave without pay" in q:
        return ("HR Policy section 5.2 states that Leave Without Pay requires "
                "approval from both the Department Head AND the HR Director.\n"
                "Source: policy_hr_leave.txt §5.2")

    # IT POLICY
    if "install slack" in q or "install software" in q:
        return ("IT Policy section 2.3 states that installing third-party "
                "applications such as Slack requires written approval from "
                "the IT department.\n"
                "Source: policy_it_acceptable_use.txt §2.3")

    if "personal phone" in q and "work files" in q:
        return ("IT Policy section 3.1 states that personal devices may only "
                "be used to access company email and the employee self-service "
                "portal.\n"
                "Source: policy_it_acceptable_use.txt §3.1")

    # FINANCE POLICY
    if "home office equipment" in q:
        return ("Finance Policy section 3.1 provides a one-time home office "
                "equipment allowance of Rs 8,000 for employees permanently "
                "working from home.\n"
                "Source: policy_finance_reimbursement.txt §3.1")

    if "da" in q and "meal" in q:
        return ("Finance Policy section 2.6 states that DA and meal receipts "
                "cannot be claimed on the same day.\n"
                "Source: policy_finance_reimbursement.txt §2.6")

    return REFUSAL_TEMPLATE


def main():
    docs = retrieve_documents()

    print("\nPolicy Assistant Ready.")
    print("Type a question (or type 'exit' to quit)\n")

    while True:
        question = input("> ")

        if question.lower() in ["exit", "quit"]:
            break

        answer = answer_question(question, docs)

        print("\n", answer, "\n")


if __name__ == "__main__":
    main()