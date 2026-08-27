import os

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_MESSAGE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def retrieve_documents():
    """
    Load all policy documents into memory.
    """
    documents = {}

    for name, path in DOCUMENTS.items():
        try:
            with open(path, "r", encoding="utf-8") as file:
                documents[name] = file.read().lower()
        except FileNotFoundError:
            documents[name] = ""

    return documents


def answer_question(question, documents):
    """
    Returns a single-source answer if found,
    otherwise returns the refusal template.
    """

    question = question.lower()

    for doc_name, content in documents.items():

        keywords = question.split()

        matches = sum(1 for word in keywords if word in content)

        if matches >= 2:
            return (
                f"Relevant information found in {doc_name}.\n"
                f"Please refer to the appropriate section in this document."
            )

    return REFUSAL_MESSAGE


def main():

    docs = retrieve_documents()

    print("=" * 50)
    print("Ask My Documents")
    print("Type 'exit' to quit.")
    print("=" * 50)

    while True:

        question = input("\nQuestion: ")

        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()
