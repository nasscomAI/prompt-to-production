import os

docs_path = "../data/policy-documents"

def load_documents():
    documents = {}

    for file in os.listdir(docs_path):
        if file.endswith(".txt"):
            with open(os.path.join(docs_path, file), "r") as f:
                documents[file] = f.read()

    return documents


def ask_question(question, documents):
    question = question.lower()

    if "leave" in question:
        doc = documents.get("policy_hr_leave.txt")
        return f"Answer from policy_hr_leave.txt: {doc.splitlines()[0]}"

    if "reimbursement" in question:
        doc = documents.get("policy_finance_reimbursement.txt")
        return f"Answer from policy_finance_reimbursement.txt: {doc.splitlines()[0]}"

    if "it" in question or "computer" in question:
        doc = documents.get("policy_it_acceptable_use.txt")
        return f"Answer from policy_it_acceptable_use.txt: {doc.splitlines()[0]}"

    return "No relevant answer found."


def main():
    documents = load_documents()

    question = input("Ask a question: ")

    answer = ask_question(question, documents)

    print("\n" + answer)


if __name__ == "__main__":
    main()
