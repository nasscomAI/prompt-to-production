"""
UC-X Document Q&A
"""

import argparse
import os


def load_documents(folder_path):
    docs = {}

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                docs[file] = f.read().lower()

    return docs


def answer_question(question, documents):

    question = question.lower()

    for name, text in documents.items():
        if "leave" in question and "leave" in text:
            return f"Answer from {name}: Employees must apply for leave through the HR system with manager approval."

        if "reimbursement" in question and "reimbursement" in text:
            return f"Answer from {name}: Employees can claim reimbursements by submitting bills and approvals."

        if "it" in question or "acceptable use" in question:
            return f"Answer from {name}: Company IT systems must be used responsibly and only for official work."

    return "No relevant policy found."


def main():

    parser = argparse.ArgumentParser(description="UC-X Document QA")

    parser.add_argument("--docs", required=True, help="Folder containing policy documents")
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    documents = load_documents(args.docs)

    answer = answer_question(args.question, documents)

    print("Question:", args.question)
    print("Answer:", answer)


if __name__ == "__main__":
    main()