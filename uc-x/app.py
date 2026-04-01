import os

REFUSAL = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents(folder):
    docs = {}

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                docs[file] = f.readlines()

    return docs


def answer_question(docs, question):
    q = question.lower()

    for doc_name, lines in docs.items():
        for line in lines:
            if any(word in line.lower() for word in q.split()):
                return f"{doc_name}: {line.strip()}"

    return REFUSAL


def main():
    docs = retrieve_documents("../data/policy-documents")

    print("Ask questions about company policies. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(docs, question)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()