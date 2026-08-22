import os
import re

DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():
    docs = {}

    for name, path in DOCS.items():
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', text, re.S)

        docs[name] = {
            sec: " ".join(body.split())
            for sec, body in sections
        }

    return docs


def answer_question(question, docs):

    q = question.lower()

    if "leave without pay" in q or "lwp" in q:
        text = docs["policy_hr_leave.txt"]["5.2"]
        return f"{text}\n\nSource: policy_hr_leave.txt section 5.2"

    if "carry forward" in q and "leave" in q:
        text = docs["policy_hr_leave.txt"]["2.6"]
        return f"{text}\n\nSource: policy_hr_leave.txt section 2.6"

    if "slack" in q:
        text = docs["policy_it_acceptable_use.txt"]["2.3"]
        return f"{text}\n\nSource: policy_it_acceptable_use.txt section 2.3"

    if "personal phone" in q or "personal device" in q:
        text = docs["policy_it_acceptable_use.txt"]["3.1"]
        return f"{text}\n\nSource: policy_it_acceptable_use.txt section 3.1"

    if "home office" in q:
        text = docs["policy_finance_reimbursement.txt"]["3.1"]
        return f"{text}\n\nSource: policy_finance_reimbursement.txt section 3.1"

    if "da" in q and "meal" in q:
        text = docs["policy_finance_reimbursement.txt"]["2.6"]
        return f"{text}\n\nSource: policy_finance_reimbursement.txt section 2.6"

    return REFUSAL


def main():

    docs = retrieve_documents()

    print("Ask questions about company policy (type 'exit' to quit)\n")

    while True:

        q = input("Question: ")

        if q.lower() in ["exit", "quit"]:
            break

        answer = answer_question(q, docs)

        print("\nAnswer:")
        print(answer)
        print("\n")


if __name__ == "__main__":
    main()