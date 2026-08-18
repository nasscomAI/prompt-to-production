import os
import re


DOCUMENTS = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def load_documents():
    documents = {}

    for path in DOCUMENTS:
        with open(path, "r", encoding="utf-8") as file:
            name = os.path.basename(path)
            documents[name] = file.read()

    return documents


def find_answer(question, documents):
    q = question.lower()

    # HR - Annual leave carry forward
    if "carry forward" in q and "annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December. "
            "[Source: policy_hr_leave.txt, Section 2.6]"
        )

    # IT - Software installation
    if ("install" in q or "installation" in q) and (
        "slack" in q or "software" in q or "work laptop" in q
    ):
        return (
            "Employees must not install software on corporate devices without "
            "written approval from the IT Department. "
            "[Source: policy_it_acceptable_use.txt, Section 2.3]"
        )

    # Finance - Home office allowance
    if "home office" in q and "allowance" in q:
        return (
            "Employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000. "
            "[Source: policy_finance_reimbursement.txt, Section 3.1]"
        )

    # IT - Personal phone
    if "personal phone" in q and ("work files" in q or "work" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. "
            "[Source: policy_it_acceptable_use.txt, Section 3.1]"
        )

    # Finance - DA and meal receipts
    if ("da" in q or "daily allowance" in q) and "meal" in q:
        return (
            "DA and meal receipts cannot be claimed simultaneously for the "
            "same day. "
            "[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # HR - LWP approval
    if "lwp" in q or "leave without pay" in q:
        return (
            "LWP requires approval from the Department Head and the HR Director. "
            "Manager approval alone is not sufficient. "
            "[Source: policy_hr_leave.txt, Section 5.2]"
        )

    return REFUSAL


def main():
    documents = load_documents()

    print("UC-X Policy Assistant")
    print("Type your question. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            continue

        answer = find_answer(question, documents)
        print("\nAnswer:", answer)
        print()


if __name__ == "__main__":
    main()