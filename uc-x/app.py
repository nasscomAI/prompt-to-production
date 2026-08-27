import os

DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""


def retrieve_documents():
    documents = {}

    for name, path in DOCS.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                documents[name] = f.readlines()

    return documents


def answer_question(documents, query):
    query = query.lower()

    for doc_name, lines in documents.items():
        for line in lines:
            if query in line.lower():
                return f"Source: {doc_name}\n{line.strip()}"

    return REFUSAL_TEMPLATE


def main():
    documents = retrieve_documents()

    while True:
        query = input("\nAsk a policy question (or type exit): ")

        if query.lower() == "exit":
            break

        answer = answer_question(documents, query)

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()

