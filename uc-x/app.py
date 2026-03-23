import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():
    base_path = "../data/policy-documents"

    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    documents = {}

    for file in files:
        path = os.path.join(base_path, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                documents[file] = f.readlines()
        except Exception:
            print(f"Error loading {file}")
            exit()

    return documents


def search_documents(question, documents):

    question_words = question.lower().split()

    for doc_name, lines in documents.items():

        for line in lines:

            text = line.strip()

            if text == "":
                continue

            if any(word in text.lower() for word in question_words):

                return f"{text} (Source: {doc_name})"

    return None


def answer_question(question, documents):

    result = search_documents(question, documents)

    if result:
        return result

    return REFUSAL_TEMPLATE


def main():

    documents = retrieve_documents()

    print("\nPolicy Assistant Ready")
    print("Ask a question about company policy.")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("Question: ")

        if question.lower() == "exit":
            print("Goodbye.")
            break

        answer = answer_question(question, documents)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()
