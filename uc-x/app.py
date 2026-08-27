import os

DOC_FOLDER = "../data/policy-documents"

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""


def retrieve_documents():

    docs = {}

    for file in os.listdir(DOC_FOLDER):
        if file.endswith(".txt"):
            path = os.path.join(DOC_FOLDER, file)

            with open(path, encoding="utf-8") as f:
                docs[file] = f.read()

    return docs


def answer_question(question, docs):

    keywords = question.lower().split()

    for name, text in docs.items():

        lines = text.split("\n")

        for line in lines:

            line_lower = line.lower()

            for word in keywords:
                if word in line_lower:
                    return f"{line.strip()} (Source: {name})"

    return REFUSAL


def main():

    docs = retrieve_documents()

    print("Ask policy questions (type 'exit' to quit)\n")

    while True:

        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = answer_question(question, docs)

        print("\nAnswer:", answer, "\n")


if __name__ == "__main__":
    main()