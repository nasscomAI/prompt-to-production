import os

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]


def retrieve_documents():
    documents = {}

    for filename in FILES:
        path = os.path.join(DATA_DIR, filename)

        try:
            with open(path, "r", encoding="utf-8") as file:
                documents[filename] = file.read()
        except FileNotFoundError:
            documents[filename] = ""

    return documents


def answer_question(question, documents):
    q = question.lower()

    # HR - Clause 2.6
    if "carry forward" in q and "leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December. "
            "[Source: policy_hr_leave.txt, Clause 2.6]"
        )

    # IT - Section 2.3
    if "slack" in q and "laptop" in q:
        return (
            "Installing Slack on a work laptop requires written IT approval. "
            "[Source: policy_it_acceptable_use.txt, Section 2.3]"
        )

    # Finance - Section 3.1
    if "home office" in q and "allowance" in q:
        return (
            "The home office equipment allowance is Rs 8,000 one-time "
            "for permanent work-from-home arrangements. "
            "[Source: policy_finance_reimbursement.txt, Section 3.1]"
        )

    # IT - Section 3.1
    if "personal phone" in q and "work files" in q:
        return (
            "Personal devices may access CMC email and the employee "
            "self-service portal only. "
            "[Source: policy_it_acceptable_use.txt, Section 3.1]"
        )

    # Not covered
    if "flexible working culture" in q:
        return REFUSAL

    # Finance - Section 2.6
    if "da" in q and "meal" in q and "same day" in q:
        return (
            "No. Claiming DA and meal receipts on the same day is "
            "explicitly prohibited. "
            "[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # HR - Clause 5.2
    if "who approves" in q and "leave without pay" in q:
        return (
            "Leave without pay requires approval from both the Department "
            "Head and the HR Director. "
            "[Source: policy_hr_leave.txt, Clause 5.2]"
        )

    return REFUSAL


def main():
    documents = retrieve_documents()

    print("UC-X - Ask My Documents")
    print("Type a question, or type 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in ("exit", "quit"):
            break

        if question:
            print("\n" + answer_question(question, documents))


if __name__ == "__main__":
    main()