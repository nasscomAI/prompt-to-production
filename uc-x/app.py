import argparse
from pathlib import Path


DOCUMENTS = {
    "hr_leave": Path("../data/policy-documents/policy_hr_leave.txt"),
    "it_acceptable_use": Path("../data/policy-documents/policy_it_acceptable_use.txt"),
    "finance_reimbursement": Path("../data/policy-documents/policy_finance_reimbursement.txt"),
}


def load_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        if path.exists():
            documents[name] = path.read_text(encoding="utf-8")

    return documents


def select_document(question):
    q = question.lower()

    if any(word in q for word in ["leave", "vacation", "holiday", "hr"]):
        return "hr_leave"

    if any(word in q for word in ["computer", "internet", "email", "acceptable", "it"]):
        return "it_acceptable_use"

    if any(word in q for word in ["reimbursement", "expense", "receipt", "travel", "finance"]):
        return "finance_reimbursement"

    return None


def answer_question(question, documents):
    document_name = select_document(question)

    if document_name is None:
        return "Information not found in the provided documents."

    if document_name not in documents:
        return "Information not found in the provided documents."

    # Return only the relevant document so information from different
    # policies is not accidentally blended.
    return f"Source: {document_name}\n\n{documents[document_name]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", help="Question to ask about the policy documents")
    args = parser.parse_args()

    documents = load_documents()

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("UC-X Ask My Documents")
    print("Type a question, or type 'exit' to quit.")

    while True:
        question = input("> ").strip()

        if question.lower() == "exit":
            break

        if question:
            print(answer_question(question, documents))


if __name__ == "__main__":
    main()
